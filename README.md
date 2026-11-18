# Estate Scout

A small RAG-style assistant for publicly available DarGlobal project information and a dated sample of Wasalt Saudi listing pages. The app retrieves the most relevant source notes and asks OpenRouter's free-model router to answer from those notes. It returns source links with each answer.

## Run with Docker

1. Copy `.env.example` to `.env` and set `OPENROUTER_API_KEY` from your OpenRouter account.
2. Run `docker compose up --build`.
3. Open http://localhost:8080.

The app runs without a key, but AI responses are disabled until `OPENROUTER_API_KEY` is set. Set `OPENROUTER_MODEL` to `openrouter/free` to use OpenRouter's currently available free model router.

## Deploy with Render

This repository includes `render.yaml` for a Docker web service. Push the project to a Git repository, create a Render Blueprint from that repository, and add `OPENROUTER_API_KEY` as a secret environment variable in the Render service settings. Render will provide the public HTTPS URL after the service builds and starts.

## Data and limitations

`data.json` is a public-source snapshot collected 2026-11-18. Wasalt examples, counts, pricing and availability change frequently. Each answer links back to the publisher so current details can be checked. The app does not crawl source sites at request time and is not affiliated with either company. Refresh the snapshot from the linked public pages before relying on listings.

## Environment

- `PORT` (default `8080`)
- `OPENROUTER_API_KEY` (required for AI responses)
- `OPENROUTER_MODEL` (default `openrouter/free`)
- `APP_URL` (optional URL sent as OpenRouter referer metadata)
