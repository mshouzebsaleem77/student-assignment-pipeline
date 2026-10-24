# Five-minute walkthrough
1. Explain the access limitation honestly: local results were executed; Fabric notebook is proposed and syntax checked only.
2. Show architecture.svg or architecture.md. Bronze preserves evidence, Silver cleans and models, Gold answers product questions.
3. Show source CSVs: 8 students, 3 courses, 6 assignments, 7 submission rows including one duplicate.
4. Run `python run_pipeline.py`, then `python -m unittest discover -s tests -v`.
5. Open outputs/missing_assignment_101.json: S003 has not submitted. S002 submitted late and is not missing.
6. Explain 17 expected student-assignment pairs: 3*3 + 3*2 + 2*1. Course rates are 3/9, 2/6, 1/2.
7. Explain future deadlines: included in overall submission rate, excluded from overdue counts. Documenting the denominator avoids ambiguous metrics.
8. Explain first accepted submission and deduplication; future submissions are ignored at the reporting cutoff.
9. Show Fabric notebook and deployment guide, CI configuration and masking limitations.
10. Production extension: incremental ingestion, schema contracts, quarantines, transactional publishing, monitored orchestration, restricted identities and paginated serving.
