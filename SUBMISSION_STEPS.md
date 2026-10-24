# Submit the repository
1. Extract ZIP to a new folder. Open CMD there.
2. Run `python run_pipeline.py`.
3. Run `python -m unittest discover -s tests -v`.
4. Open notebooks/Local_Demonstration.ipynb in an editor supporting notebooks, or review outputs/*.json and outputs/validation.txt. The notebook contains saved local execution output.
5. Create an empty GitHub repository in your account. Do not pre-create README there.
6. Run the following commands, replacing the URL with your real repository URL:
```bat
git init
git add .
git commit -m "Add assignment analytics pipeline and Fabric design"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/student-assignment-pipeline.git
git push -u origin main
```
If Git requests identity, configure your own name/email; authenticate using GitHub's login flow. Never embed a token in the repository or URL.
7. Check GitHub Actions. Share your repository URL only after reviewing the files and understanding the walkthrough.

## Cover note
Hi Team,
Please find my technical assignment at: [insert actual repository URL].
The repository includes the sample datasets, Bronze/Silver/Gold pipeline, required queries and JSON outputs, validation tests, CI workflow, governance examples and architecture diagram. Due to the Fabric trial activation issue, I validated the local SQL reference implementation and provided the corresponding Fabric PySpark notebook and deployment instructions. The README clearly identifies execution status and assumptions.
Regards,
Shouzeb Saleem
