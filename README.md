# Student Assignment Analytics
A small, reproducible Bronze → Silver → Gold pipeline with a Fabric PySpark implementation and an executable local SQL reference.

## Execution status
Microsoft Fabric trial capacity activation failed during setup. The evaluator advised proceeding with artifacts and an architecture diagram.
- Local standard-library Python + SQLite pipeline: executed and tested; outputs included.
- Fabric PySpark/Delta notebook: supplied and Python syntax checked, **not executed in Fabric**.
- GitHub Actions: workflow supplied; local equivalent tested. Hosted CI has not yet run.
- Security/governance: masking demonstrated; access enforcement proposed, not provisioned.

## Quick start on Windows
Extract this ZIP to a **new folder** (avoid mixing it with earlier practice scripts). Open CMD in that folder.
```bat
python run_pipeline.py
python -m unittest discover -s tests -v
```
Python 3.12+ is sufficient for the local reference. It uses only standard-library modules: no Java, pip packages or credentials needed. It was validated in the accompanying execution environment; run the same tests on your machine before submission.

Open outputs/*.json for answers and docs/architecture.svg for the diagram. The executed local notebook is notebooks/Local_Demonstration.ipynb.
For actual PySpark use notebooks/Fabric_Pipeline.ipynb; see docs/fabric_deployment.md. Local execution is explicitly SQL-based, while the Fabric artifact is PySpark-based.

## Structure
- data/source: four synthetic CSV files, including one deliberate duplicate and whitespace/case variations.
- src/pipeline.py: ingestion, cleaning, validation, SQL modeling, export.
- sql: Silver mapping and the three requested analytical queries.
- fabric and notebooks: complete Fabric PySpark script/notebook and executed local demonstration.
- outputs: generated API-style JSON results and run summary.
- docs: architecture, assumptions, governance, metadata and presentation notes.
- tests: functional checks. .github/workflows/ci.yml: CI simulation.

## Business rules
- Each student is enrolled in exactly one course for this four-source simulation. A production many-course model adds an enrollment bridge.
- Every student is expected to submit every listed assignment in that course. All sample students/assignments are assumed active before the reporting cutoff; no historical enrollment tracking is modeled.
- Fixed cutoff: **2026-10-25T00:00:00Z**. All timestamps are normalized to UTC.
- Missing Assignment_101: only enrolled students without a submission by the cutoff.
- Course submission rate: unique submitted student-assignment pairs / all expected student-assignment pairs * 100. Future-due assignments are included; this is an overall rate, not a due-only rate.
- Overdue: deadline strictly before cutoff AND no submission by cutoff. A late-but-submitted assignment is tracked separately, not counted as outstanding overdue.
- Identical duplicate records are removed; conflicting primary-key duplicates fail. Multiple distinct submission attempts use the earliest timestamp to assess whether an assignment was ever submitted on time.
- Invalid relationships, required values and timestamps fail the run instead of silently losing records.

## Expected answers
- Assignment_101 missing: **S003 / Usman Malik**.
- Course C001: 3/9 = **33.33%**; C002: 2/6 = **33.33%**; C003: 1/2 = **50%**.
- Overdue counts S001–S008: **0, 1, 2, 0, 0, 1, 0, 1**.
- Late submissions: S002 and S005, one each.
- Bronze submissions: 7 rows; Silver submissions: 6; expected mapping: 17 rows.

## Reliability and limits
Reruns overwrite demonstration snapshots and produce the same analytical answers. Bronze CSV bytes remain unchanged; raw history is not retained per run in this small version. Local database is built in a temporary file and replaces the prior DB only after SQL succeeds. CSV/JSON exports and Fabric multiple-table writes are not globally atomic; an error may leave partially updated exports/tables. Production requires versioned run outputs plus a published-success pointer, source schema enforcement, concurrency controls and monitoring. Local SQLite is suitable for this tiny simulation, not a distributed warehouse. Driver-side JSON collection is bounded by the sample size; production consumers need pagination or distributed export.

## Security and credentials
All data is fictional. No cloud credentials required; `.env.example` supplied and `.env` ignored. Never commit passwords, tokens or real student records. Masking view demonstrates transformation only; see docs/governance.md for enforcement design.

## Submission
1. Run pipeline/tests and review notebooks/Local_Demonstration.ipynb.
2. Create a new GitHub repository, for example `student-assignment-pipeline`.
3. Upload this folder's files (including .github) or use Git commands in SUBMISSION_STEPS.md.
4. Confirm workflow succeeds on GitHub. Share the actual repository URL with the evaluator.
5. Explain the Fabric capacity limitation and distinguish local evidence from proposed cloud deployment.
