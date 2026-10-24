import unittest,tempfile,shutil,json
from pathlib import Path
from src.pipeline import run,clean,validate,ROOT

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        shutil.copytree(ROOT/'data',self.root/'data')
        self.results=run(self.root)
    def tearDown(self): self.temp.cleanup()
    def test_missing(self):
        self.assertEqual([r['student_id'] for r in self.results['missing_assignment_101']['data']],['S003'])
    def test_rates(self):
        self.assertEqual([r['submission_rate_pct'] for r in self.results['course_submission_rates']['data']],[33.33,33.33,50.0])
        self.assertEqual([r['expected_submissions'] for r in self.results['course_submission_rates']['data']],[9,6,2])
    def test_overdue_and_late(self):
        rows=self.results['overdue_per_student']['data']
        self.assertEqual([r['overdue_count'] for r in rows],[0,1,2,0,0,1,0,1])
        self.assertEqual(sum(r['late_submission_count'] for r in rows),2)
    def test_idempotent(self): self.assertEqual(self.results,run(self.root))
    def test_duplicate_and_cleaning(self):
        report=json.loads((self.root/'outputs/run_summary.json').read_text())
        self.assertEqual(report['counts']['submissions'],{'bronze':7,'silver':6})
        row=clean([{'student_id':' S001 ','email':'ALI@example.com'}],'students')[0]
        self.assertEqual(row['email'],'ali@example.com')
    def test_conflict_rejected(self):
        with self.assertRaises(ValueError): clean([{'course_id':'C1','course_name':'A'},{'course_id':'C1','course_name':'B'}],'courses')
    def test_invalid_foreign_key(self):
        with self.assertRaises(ValueError): validate({'courses':[],'students':[{'student_id':'S1','course_id':'bad'}],'assignments':[],'submissions':[]})
    def test_future_submission_excluded(self):
        result=run(self.root,'2026-10-20T00:00:00Z')
        self.assertEqual([r['student_id'] for r in result['missing_assignment_101']['data']],['S002','S003'])
    def test_json_contract(self):
        for value in self.results.values(): self.assertEqual(set(value),{'status','message','data'})

if __name__=='__main__': unittest.main()
