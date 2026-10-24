# Fabric: attach a default Lakehouse and upload the four CSVs to Files/source/.
from pyspark.sql import functions as F
spark.conf.set('spark.sql.session.timeZone','UTC')
AS_OF = '2026-10-25T00:00:00Z'
SOURCE = 'Files/source'
NAMES = ['courses','students','assignments','submissions']
KEYS = {'courses':'course_id','students':'student_id','assignments':'assignment_id','submissions':'submission_id'}
# Prefixes separate layers while working with both schema-enabled and legacy lakehouses.
frames = {}
for name in NAMES:
    raw = spark.read.option('header',True).option('mode','FAILFAST').csv(f'{SOURCE}/{name}.csv')
    raw.write.format('delta').mode('overwrite').option('overwriteSchema','true').saveAsTable(f'bronze_{name}')
    df = spark.table(f'bronze_{name}').select([F.trim(F.col(c)).alias(c) for c in raw.columns])
    for c in df.columns:
        assert df.filter(F.col(c).isNull() | (F.col(c)=='')).limit(1).count()==0, f'Missing {name}.{c}'
    if name=='students':
        df=df.withColumn('email',F.lower('email'))
        assert df.filter(~F.col('email').rlike(r'^[^@]+@[^@]+$')).limit(1).count()==0, 'Invalid email'
    for c in ['due_at','submitted_at']:
        if c in df.columns:
            # Sample contract: UTC timestamps ending in Z.
            assert df.filter(~F.col(c).endswith('Z')).limit(1).count()==0, 'Expected UTC timestamp'
            df=df.withColumn(c,F.to_timestamp(c))
            assert df.filter(F.col(c).isNull()).limit(1).count()==0, 'Invalid timestamp'
    df=df.dropDuplicates()
    assert df.groupBy(KEYS[name]).count().filter('count > 1').limit(1).count()==0, f'Conflicting {name} key'
    frames[name]=df
# Fail on invalid relationships instead of silently dropping records.
for name in ['students','assignments']:
    assert frames[name].join(frames['courses'],'course_id','left_anti').limit(1).count()==0, 'Unknown course'
for name,key in [('students','student_id'),('assignments','assignment_id')]:
    assert frames['submissions'].join(frames[name],key,'left_anti').limit(1).count()==0, f'Unknown {key}'
invalid=frames['submissions'].alias('u').join(frames['students'].alias('s'),'student_id').join(frames['assignments'].alias('a'),'assignment_id').filter(F.col('s.course_id')!=F.col('a.course_id'))
assert invalid.limit(1).count()==0, 'Student not enrolled in assignment course'
for name,df in frames.items():
    df.write.format('delta').mode('overwrite').option('overwriteSchema','true').saveAsTable(f'silver_{name}')
first = frames['submissions'].filter(F.col('submitted_at')<=F.to_timestamp(F.lit(AS_OF))).groupBy('student_id','assignment_id').agg(F.min('submitted_at').alias('submitted_at'))
first.createOrReplaceTempView('first_submission')
joined=spark.sql('SELECT s.student_id,s.student_name,s.email,c.course_id,c.course_name,\na.assignment_id,a.assignment_name,a.due_at,f.submitted_at\nFROM silver_students s JOIN silver_courses c ON s.course_id=c.course_id\nJOIN silver_assignments a ON a.course_id=c.course_id\nLEFT JOIN first_submission f ON s.student_id=f.student_id AND a.assignment_id=f.assignment_id')
joined=joined.withColumn('is_submitted',F.col('submitted_at').isNotNull().cast('int')).withColumn('is_overdue',((F.col('due_at')<F.to_timestamp(F.lit(AS_OF))) & F.col('submitted_at').isNull()).cast('int')).withColumn('is_late',F.coalesce((F.col('submitted_at')>F.col('due_at')).cast('int'),F.lit(0)))
joined.write.format('delta').mode('overwrite').option('overwriteSchema','true').saveAsTable('silver_student_assignments')

result=spark.sql("SELECT student_id,student_name,course_id FROM silver_student_assignments WHERE assignment_id='Assignment_101' AND is_submitted=0 ORDER BY student_id")
result.write.format('delta').mode('overwrite').option('overwriteSchema','true').saveAsTable('gold_missing_assignment_101')
display(result)

result=spark.sql('SELECT course_id,course_name,COUNT(*) AS expected_submissions,\nSUM(is_submitted) AS submitted_count,ROUND(100.0*SUM(is_submitted)/COUNT(*),2) AS submission_rate_pct\nFROM silver_student_assignments GROUP BY course_id,course_name ORDER BY course_id')
result.write.format('delta').mode('overwrite').option('overwriteSchema','true').saveAsTable('gold_course_submission_rates')
display(result)

result=spark.sql('SELECT student_id,student_name,SUM(is_overdue) AS overdue_count,SUM(is_late) AS late_submission_count\nFROM silver_student_assignments GROUP BY student_id,student_name ORDER BY student_id')
result.write.format('delta').mode('overwrite').option('overwriteSchema','true').saveAsTable('gold_overdue_per_student')
display(result)

# Bounded sample outputs collected to the driver; use pagination for production-sized APIs.
import json
from pathlib import Path
out=Path('/lakehouse/default/Files/outputs');out.mkdir(parents=True,exist_ok=True)
for name in ['missing_assignment_101','course_submission_rates','overdue_per_student']:
    df=spark.table('gold_'+name)
    order=['course_id'] if name=='course_submission_rates' else ['student_id']
    rows=[json.loads(row) for row in df.orderBy(*order).toJSON().collect()]
    payload={'status':'success','message':f'{name}; as_of={AS_OF}','data':rows}
    (out/f'{name}.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
assert spark.table('silver_submissions').count()==6
assert joined.count()==17
assert [r.student_id for r in spark.table('gold_missing_assignment_101').collect()]==['S003']
# Mock column security: masking is a transformation, not access enforcement.
spark.sql("SELECT student_id,student_name,course_id,concat(left(email,1),'***@example.com') AS email FROM silver_students").write.format('delta').mode('overwrite').saveAsTable('gold_masked_students')
print('Fabric pipeline complete; Delta tables, JSON exports and checks finished.')
