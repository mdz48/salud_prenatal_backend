# Agent Rules for salud_prenatal_backend

## Dependency Management

- Whenever you introduce a new Python library (via import or usage), you MUST add it to `requirements.txt` in the project root before finishing the task. Never leave a library undeclared.
- NEVER install packages globally. All installations must target the local `.venv` virtual environment inside the project root.
  - Correct:   `.venv\Scripts\pip install <package>`
  - Incorrect: `pip install <package>` (this may modify the global environment)
- After adding a library to `requirements.txt`, remind the user to run:
  `.venv\Scripts\pip install -r requirements.txt`
