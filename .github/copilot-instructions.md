<!-- .github/copilot-instructions.md -->
# Bienen-App — instructions for AI coding agents

This short guide helps an AI agent (called "Chatty") become productive quickly in this repository. It documents the app architecture, developer workflows, project-specific patterns, and small code examples you should follow when making changes.

**IMPORTANT: Git Workflow & Public/Local Code Separation**

This repository maintains **strict separation** between public app code and local production files:

**PUBLIC CODE (commit to GitHub):**
- ✅ app.py, forms.py, models.py, user_models.py, upload_utils.py
- ✅ templates/, static/ (HTML, CSS)
- ✅ init_admin.py, setup_user.py (setup scripts)
- ✅ requirements.txt, .env.example, default_user.example.txt (templates only)
- ✅ README.md, CHANGELOG.md, DEPLOYMENT.md (documentation)
- ✅ .gitignore, project_structure.txt

**LOCAL PRODUCTION FILES (keep locally only - NEVER commit):**
- ❌ .env (production environment variables with SECRET_KEY)
- ❌ secret_key.txt (Flask SECRET_KEY - gitignored)
- ❌ default_user.txt (real admin credentials - gitignored)
- ❌ beehivetracker.service (systemd service file - gitignored)
- ❌ var/app-instance/*.db (production databases - gitignored)
- ❌ var/logs/ (application logs - gitignored)
- ❌ .cloudflared/ (Cloudflare tunnel config - gitignored)
- ❌ Anything in var/, migrations/, bin/, lib/, include/ (local runtime)

**Git Workflow Instructions:**
1. After app code changes (features, bug fixes, templates): commit to Git
2. Suggest commits for: app.py, forms.py, models.py, templates/, CHANGELOG.md, README.md
3. NEVER suggest commits for: .env, secret_key.txt, default_user.txt, *.db, beehivetracker.service
4. Always remind: "Production files stay local and are gitignored for security"
5. Update CHANGELOG.md with all changes (commit this too)

**Reference Documentation:**
- See .github/PRODUCTION_SETUP.md for local production file details
- See .github/GIT_WORKFLOW.md for detailed Git workflow examples
- See README.md for overview

1) Big picture (what this repo is)
- Single-process Flask web app (file: `app.py`) serving server-rendered templates from `templates/`.
- Data stored with SQLAlchemy (`models.py`) using SQLite; database is auto-created with `db.create_all()` on app start.
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

4) Dev / run workflow (explicit commands)
- Activate the provided virtual environment (if present):
  - source ./bin/activate
- Run the app (dev):
  - python app.py
  - (This sets debug=True and listens on 0.0.0.0 in development.)
- Database setup:
  - Database is automatically created on first run with `db.create_all()` in `app.py`
  - No migrations needed - schema is defined in `models.py`

5) Safety notes and small gotchas
- SECRET_KEY: Use environment variable from .env (production) or 'biene' (dev only)
  - NEVER hardcode SECRET_KEY in app.py or committed files
  - Store real SECRET_KEY in .env (local, gitignored)
  - .env template (.env.example) shows structure without secrets
- Production files MUST be gitignored:
  - .env, secret_key.txt, default_user.txt are NEVER committed
  - beehivetracker.service stays local (sudoadministered)
  - Databases (*.db) stay local (user data is private)
  - Use git status to verify no secrets are staged
- Many form-handling paths use `get_or_404` for lookups — update redirects and flash messages consistently when changing behavior.
- Templates expect Bootstrap 5 classes and the existing `styles.css`; keep responsive behavior intact.
- When testing: use local .env with DEBUG=True and dev credentials
- When deploying: use production .env with DEBUG=False (gitignored)

6) Code-change contract (minimal checklist for PRs)
- ✅ PUBLIC: Keep route names and templates consistent with German naming.
- ✅ PUBLIC: Update `forms.py` and `app.py` together when adding new fields
- ✅ PUBLIC: Update README.md and CHANGELOG.md for user-facing changes
- ✅ PUBLIC: Ensure all credentials/secrets use environment variables
- ❌ LOCAL ONLY: Never commit .env, secret_key.txt, beehivetracker.service, or *.db files
- ❌ LOCAL ONLY: Never commit production logs, uploads, or Cloudflare configs
- If altering models in `models.py`: commit to public repo, users will recreate local DBs
- Always verify: `git status --short` shows NO secrets before committing

7) Quick examples to cite in edits
- Populate select choices (app.py):
  - form.colony_id.choices = [(v.id, v.name) for v in BeeColony.query.all()]
- Use context processor mapping (app.py):
  - @app.context_processor
    def utility_processor():
        return {'queen_colors': QUEEN_COLORS}

8) Where to look for follow-ups
- `models.py` — Database schema definition (all tables and fields)
- `templates/` — pattern for flash messages and form blocks (follow existing blocks when adding UI).
- `project_structure.txt` — lightweight notes and minimal dependency hints.
- `.github/PRODUCTION_SETUP.md` — Documentation of local production files
- `.github/GIT_WORKFLOW.md` — Examples of safe Git workflows with public/local separation

If anything here is unclear, tell me which section you want expanded (e.g., exact migration commands you use, CI/test commands if you have them, or a preference for naming). I can iterate and update this file.

### Important Security Rule: Public/Local Code Separation & Credentials

**CRITICAL: Public App Code vs. Local Production Files**

This project MUST maintain strict separation:
- **PUBLIC** (safe for GitHub): All app code, templates, docs, setup scripts
- **LOCAL** (never commit): All secrets, credentials, databases, config files

**NEVER include credentials in ANY committed files**, including:
- Code files (app.py, forms.py, models.py, etc.) - NO hardcoded secrets
- Documentation (README.md, CHANGELOG.md) - NO default credentials shown
- Configuration files (NEVER .env, secret_key.txt, or beehivetracker.service)
- Database files or logs containing user/production data
- Cloudflare Tunnel configuration files

**Safe Patterns:**
- ✅ `.env.example` with placeholder values (e.g., SECRET_KEY=your-secret-here)
- ✅ `default_user.example.txt` as template only
- ✅ Environment variables from .env in app code
- ✅ Setup scripts (init_admin.py) that PROMPT users for credentials

**Unsafe Patterns:**
- ❌ Hardcoded SECRET_KEY in app.py
- ❌ Real admin credentials in README.md or docs
- ❌ Committing .env with real values
- ❌ Storing production databases in repo
- ❌ Committing beehivetracker.service (systemd file)
- ❌ Including .cloudflared/ tunnel config

**Verification before commit:**
```bash
# Should return NOTHING:
git ls-files | grep -E '(\.env$|secret_key|\.db$|\.cloudflared|default_user\.txt)'

# Should show only app files:
git status --short
```

**If you accidentally commit secrets:**
1. Remove from git history immediately: `git rm --cached <file>`
2. Regenerate all secrets (new SECRET_KEY, reset passwords, etc.)
3. Push corrected commit with --force-with-lease
4. Document the incident internally

