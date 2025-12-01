<!-- .github/copilot-instructions.md -->
# Bienen-App — instructions for AI coding agents

This short guide helps an AI agent (called "Chatty") become productive quickly in this repository. It documents the app architecture, developer workflows, project-specific patterns, and small code examples you should follow when making changes.

1) Big picture (what this repo is)
- Single-process Flask web app (file: `app.py`) serving server-rendered templates from `templates/`.
- Data stored with SQLAlchemy (`models.py`) using SQLite; migrations live in `migrations/` (Flask-Migrate / Alembic).
- Forms are built with WTForms (`forms.py`), templates use Bootstrap via CDN (`templates/base.html`).

2) Key components and where to look
- HTTP surface / routes: `app.py` — examples: `/neues-volk`, `/neue-inspektion`, `/voelker`, `/inspektionen`, `/volk/<id>`.
- Data models: `models.py` — `BeeColony` and `Inspection` (note: several inspection fields such as `volksstaerke`, `mittelwaende`, `brutwaben`).
- Forms: `forms.py` — `BeeColonyForm`, `InspectionForm`. `InspectionForm.colony_id` is a SelectField with `coerce=int` and choices are set in `app.py`.
- Templates: `templates/*.html` — use `base.html` for layout and `{{ url_for('static', filename='styles.css') }}` for CSS.
- DB file: a SQLite DB is expected (created by SQLAlchemy). There is a `var/app-instance/bienen.db` in the workspace; `app.py` uses `sqlite:///bienen.db` by default.

3) Important patterns / project conventions (copy these exactly)
- German-language identifiers and routes: variable names, routes and templates use German (`voelker`, `inspektionen`, `volk`, `neues-volk`). Keep names consistent.
- Forms vs request.form: numeric inspection fields are often read with `request.form.get('field', type=int)` in `app.py` instead of relying solely on WTForms IntegerField. When adding similar fields follow the existing pattern so templates/forms and route handling remain consistent.
- Choices population: `InspectionForm.colony_id.choices = [(v.id, v.name) for v in voelker]` — always set `choices` before rendering or validating the form.
- Context processor: `app.py` registers `queen_colors` via `@app.context_processor` — templates assume `queen_colors` is available.
- Delete behavior: `BeeColony.inspections` uses `cascade='all, delete-orphan'`; deleting a colony should remove related inspections.

4) Dev / run / migration workflow (explicit commands)
- Activate the provided virtual environment (if present):
  - source ./bin/activate
- Run the app (dev):
  - python app.py
  - (This sets debug=True and listens on 0.0.0.0 in development.)
- Flask-Migrate (standard pattern used):
  - export FLASK_APP=app.py
  - flask db migrate -m "msg"
  - flask db upgrade
  - If `flask` isn't on PATH, run `python -m flask ...` while the venv is active.

- Helper script: `migrate.py`
  - The repository includes a small helper script `migrate.py` that automates setting
    `FLASK_APP`, creating an initial `migrations/` folder if missing, running
    `flask db migrate -m "msg"` and `flask db upgrade`.
  - It prompts interactively for the migration message. Example usage (with venv active):

```bash
python migrate.py
```

  - Note: `migrate.py` uses `os.system()` to invoke the `flask` CLI; ensure your virtualenv
    is active so the `flask` command and environment are correct. You can also run the
    equivalent explicit commands shown above if you prefer.

5) Safety notes and small gotchas
- SECRET_KEY in `app.py` is the literal `'biene'` — it's fine for local dev but do not leak or harden in production changes.
- Many form-handling paths use `get_or_404` for lookups — update redirects and flash messages consistently when changing behavior.
- Templates expect Bootstrap 5 classes and the existing `styles.css`; keep responsive behavior intact.

6) Code-change contract (minimal checklist for PRs)
- Keep route names and templates consistent with German naming.
- Update `forms.py` and `app.py` together when adding new fields: add WTForm entries, add template inputs, and ensure `request.form.get(...)` usage or `form.populate_obj` is handled consistently.
- If altering models, add an Alembic migration (`flask db migrate`) and include the migration file under `migrations/versions/`.

7) Quick examples to cite in edits
- Populate select choices (app.py):
  - form.colony_id.choices = [(v.id, v.name) for v in BeeColony.query.all()]
- Use context processor mapping (app.py):
  - @app.context_processor
    def utility_processor():
        return {'queen_colors': QUEEN_COLORS}

8) Where to look for follow-ups
- `migrations/` — DB migration history and Alembic configuration.
- `templates/` — pattern for flash messages and form blocks (follow existing blocks when adding UI).
- `project_structure.txt` — lightweight notes and minimal dependency hints.

If anything here is unclear, tell me which section you want expanded (e.g., exact migration commands you use, CI/test commands if you have them, or a preference for naming). I can iterate and update this file.
