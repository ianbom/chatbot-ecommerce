# Repository Guidelines

## Project Structure & Module Organization

This repository contains an ecommerce chatbot stack split into backend and frontend projects.

- `api-chatbot/` contains the FastAPI backend. Current entry point is `api-chatbot/main.py`; future backend packages should live under `api-chatbot/app/`.
- `web-chatbot/` contains the Vite React frontend. Application code lives in `web-chatbot/src/`.
- `web-chatbot/src/components/` stores reusable React components; `components/ui/` contains shadcn primitives.
- `web-chatbot/src/hooks/`, `src/lib/`, `src/assets/`, and `src/app/dashboard/` contain hooks, utilities, assets, and dashboard data.
- Root docs (`prd.md`, `srs.md`, `erd.md`) describe product, requirements, and data model context.

Avoid editing generated dependency folders such as `api-chatbot/venv/`.

## Build, Test, and Development Commands

Run frontend commands from `web-chatbot/`:

- `npm install`: install dependencies from `package-lock.json`.
- `npm run dev`: start the Vite development server.
- `npm run build`: run TypeScript build and create production assets.
- `npm run lint`: run ESLint across the frontend.
- `npm run preview`: serve the built frontend locally.

Run backend commands from `api-chatbot/`:

- `.\venv\Scripts\Activate.ps1`: activate the Windows virtual environment.
- `uvicorn main:app --reload`: start the FastAPI API locally.

## Coding Style & Naming Conventions

Use TypeScript and React function components in the frontend. Keep component filenames kebab-case, as in `site-header.tsx`, and export PascalCase names. Keep utilities in `src/lib/` and hooks in `src/hooks/` with `use-` filenames.

Frontend linting uses ESLint (`npm run lint`). Prefer existing Tailwind/shadcn patterns and the `cn` helper from `src/lib/utils.ts`.

Use Python type hints for new backend code. Keep FastAPI routers, schemas, and services separated under `api-chatbot/app/` as the API grows.

## Testing Guidelines

No test suite is currently configured. For frontend changes, add tests near changed features when a framework is introduced, using `*.test.ts` or `*.test.tsx`. For backend changes, prefer `pytest` under `api-chatbot/tests/`, with files named `test_*.py`.

Until automated tests exist, verify changes with `npm run lint`, `npm run build`, and a manual API smoke test against `GET /`.

## Commit & Pull Request Guidelines

Git history only has a minimal `first` commit, so no strict convention exists. Use short, imperative subjects such as `Add dashboard filters` or `Fix chatbot API response`.

Pull requests should include summary, verification notes, linked issue or requirement, and screenshots for visible frontend changes. Call out environment or migration steps.

## Security & Configuration Tips

Do not commit secrets, API keys, or local `.env` files. Keep virtual environments and generated output out of review. Document required environment variables in README or example env files.
