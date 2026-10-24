# Proposed Fabric deployment (not cloud-executed)
1. Provision a workspace with active Fabric capacity and create `student_assignment_lh`.
2. Upload four CSVs from data/source to Lakehouse Files/source.
3. Import notebooks/Fabric_Pipeline.ipynb and attach the Lakehouse as default.
4. Run all cells using the built-in PySpark runtime. Inspect bronze_*, silver_* and gold_* tables.
5. Inspect Files/outputs for JSON responses. Save executed notebook outputs/screenshots only after an actual successful run.
6. Create a Fabric Data Factory pipeline with one Notebook activity pointing to this notebook. Configure failure notification and a schedule.
7. For production, parameterize AS_OF/source path, disable overlapping writes, use managed identities and separate deployment environments.
8. Apply consumer-only permissions on masked Gold tables. The security example does not establish enforcement automatically.

The notebook performs ingestion, transformations, validation and exports in sequence, satisfying Python orchestration. The graphical pipeline is a deployment instruction, not an exported live Fabric pipeline artifact.
