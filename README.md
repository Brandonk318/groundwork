# Groundwork (working name)

A reentry and recovery social app: one community, one feed and one identity, for people coming home from incarceration and people in substance-use recovery (including people who were never incarcerated).

> The name is a placeholder. Finalists are Groundwork and Commissary Club ("Refresh" is taken). Rename by changing `backend/app/config.py` (`DEFAULT_APP_NAME`, or env `GW_APP_NAME`) and `frontend/src/brand.js` (or env `VITE_APP_NAME`).

**Status: scaffold.** All 45 features are registered as stubs. The working parts are:
- health, features and plans endpoints
- the crisis endpoint and the crisis button on every screen
- the lock and filter policy
- anonymity and phone-number redaction helpers
- vault envelope encryption
- real-delete wipe
- the i18n shell with 8 locales (Arabic RTL)

## Run
```bash
cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
GW_JWT_SECRET=$(python3 -c 'import secrets;print(secrets.token_hex(32))') .venv/bin/uvicorn app.main:create_app --factory --reload
cd ../frontend && npm install && npx vitest run && npm run dev
```

## Docs
- [AGENTS.md](AGENTS.md): rules for agents, including the safety defaults
- [docs/features.md](docs/features.md): the 45 features, with tier, build type and OSS candidates
- [docs/roadmap.md](docs/roadmap.md)
- [docs/domain-notes.md](docs/domain-notes.md)
- [docs/open-questions.md](docs/open-questions.md)
