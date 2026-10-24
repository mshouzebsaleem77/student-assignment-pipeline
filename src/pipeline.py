"""Executable local reference: standard-library Python + SQL, no Java needed."""
import argparse,csv,json,shutil,sqlite3
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NAMES=('courses','students','assignments','submissions')
KEYS={'courses':'course_id','students':'student_id','assignments':'assignment_id','submissions':'submission_id'}

def timestamp(value):
    dt=datetime.fromisoformat(value.replace('Z','+00:00'))
    if dt.tzinfo is None:
        raise ValueError('Timestamp must include a timezone: '+value)
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def clean(rows,name):
    result={}
    for raw in rows:
        if None in raw or any(v is None for v in raw.values()):
            raise ValueError('Malformed CSV row in '+name)
        row={k:v.strip() for k,v in raw.items()}
        if any(not v for v in row.values()):
            raise ValueError('Missing required value in '+name)
        if 'email' in row:
            row['email']=row['email'].lower()
            if row['email'].count('@')!=1:
                raise ValueError('Invalid email')
        for col in ('due_at','submitted_at'):
            if col in row: row[col]=timestamp(row[col])
        key=row[KEYS[name]]
        if key in result and row!=result[key]:
            raise ValueError('Conflicting duplicate key: '+key)
        result[key]=row
    return list(result.values())

def validate(data):
    courses={r['course_id'] for r in data['courses']}
    students={r['student_id']:r for r in data['students']}
    assignments={r['assignment_id']:r for r in data['assignments']}
    for name in ('students','assignments'):
        for r in data[name]:
            if r['course_id'] not in courses: raise ValueError('Unknown course')
    for r in data['submissions']:
        s=students.get(r['student_id']);a=assignments.get(r['assignment_id'])
        if not s or not a: raise ValueError('Unknown student/assignment')
        if s['course_id']!=a['course_id']: raise ValueError('Student not enrolled in course')

def load_table(con,name,rows,columns):
    con.execute('CREATE TABLE '+name+' ('+','.join('"'+c+'" TEXT NOT NULL' for c in columns)+')')
    con.executemany('INSERT INTO '+name+' VALUES ('+','.join('?' for _ in columns)+')',[[r[c] for c in columns] for r in rows])

def run(root=ROOT,as_of='2026-10-25T00:00:00Z'):
    root=Path(root);as_of=timestamp(as_of)
    for folder in ('lakehouse/bronze','lakehouse/silver','lakehouse/gold','outputs'):
        (root/folder).mkdir(parents=True,exist_ok=True)
    data={};counts={}
    for name in NAMES:
        src=root/'data/source'/f'{name}.csv';dst=root/'lakehouse/bronze'/src.name
        shutil.copy2(src,dst)
        with dst.open(newline='',encoding='utf-8') as f:
            reader=csv.DictReader(f);rows=list(reader);columns=reader.fieldnames
        data[name]=clean(rows,name);counts[name]={'bronze':len(rows),'silver':len(data[name])}
    validate(data)
    db=root/'lakehouse/silver/analytics.db';tmp=db.with_suffix('.tmp.db')
    if tmp.exists(): tmp.unlink()
    con=sqlite3.connect(tmp);con.row_factory=sqlite3.Row
    try:
        for name in NAMES:
            load_table(con,'silver_'+name,data[name],list(data[name][0]))
        con.execute((ROOT/'sql/silver.sql').read_text(),{'as_of':as_of})
        results={}
        for name in ('missing_assignment_101','course_submission_rates','overdue_per_student'):
            query=(ROOT/'sql'/f'{name}.sql').read_text().strip().rstrip(';')
            con.execute('CREATE TABLE gold_'+name+' AS '+query)
            records=[dict(r) for r in con.execute(query)]
            results[name]={'status':'success','message':f'{name}; as_of={as_of}','data':records}
        con.execute("CREATE VIEW masked_students AS SELECT student_id,student_name,course_id,substr(email,1,1)||'***@example.com' AS email FROM silver_students")
        con.commit()
    finally: con.close()
    tmp.replace(db)
    for name,value in results.items():
        (root/'outputs'/f'{name}.json').write_text(json.dumps(value,indent=2),encoding='utf-8')
        rows=value['data']
        with (root/'lakehouse/gold'/f'{name}.csv').open('w',newline='',encoding='utf-8') as f:
            if rows:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (root/'outputs/run_summary.json').write_text(json.dumps({'as_of':as_of,'counts':counts,'status':'success'},indent=2))
    print(json.dumps({'status':'success','message':'Pipeline completed','data':counts},indent=2))
    return results

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--as-of',default='2026-10-25T00:00:00Z');args=parser.parse_args()
    try: run(as_of=args.as_of)
    except Exception as exc:
        print(json.dumps({'status':'error','message':str(exc),'data':[]}));raise SystemExit(1)
