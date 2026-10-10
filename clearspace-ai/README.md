# ClearSpace

A calm document workspace for a two-person hackathon team. Built with Python, Streamlit, pypdf and small, independent service modules. No database or account setup is required to try it.

## Run on your Mac

Install Python 3.11 or 3.12 first. Unzip the project, then open Terminal in the `clearspace-ai` folder. Run these commands one at a time:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m streamlit run app.py
```

Open http://localhost:8501. Keep Terminal open while using the app. Stop it with Control+C. To run again, open the project folder in Terminal, run `source .venv/bin/activate`, then `python -m streamlit run app.py`.

Windows activation: `.venv\Scripts\activate` (use `python` instead of `python3` if necessary). Copy `.env.example` to `.env` using File Explorer or `copy .env.example .env` in Command Prompt.

**The initial workspace contains eight fictional files, including one exact duplicate pair. All initial analysis is labeled Demo.** Demo analysis uses deterministic keyword rules and extracts, not an AI model.

## Why this stack

Streamlit gives two beginner-to-intermediate developers a working Python UI without a separate frontend build or API server. pypdf extracts text locally on the app host. SHA-256 and search run without paid services. Dedicated provider adapters keep cloud-specific configuration out of the UI.

The trade-off: Streamlit reruns Python on interactions, provides less layout control than React, and this prototype uses session memory rather than durable accounts. Custom CSS makes both themes cohesive, but should be rechecked if upgrading Streamlit. The pinned version is the version tested for this delivery.

## Project structure

```text
clearspace-ai/
  app.py                       # Navigation and page workflows
  components/
    ui.py                      # Themes, cards, headings, grid
  services/
    models.py                  # Document state
    file_reader.py             # TXT/MD/PDF validation and extraction
    ai_service.py              # Demo, DigitalOcean, Snowflake adapters
    search_service.py          # Ranked keyword matching and excerpts
    duplicates.py              # Exact SHA-256 groups
    organizer.py               # Proposals and in-app approvals
    demo.py                    # Repeatable fictional dataset
  data/demo_files/              # 8 sample documents, safe to commit
  tests/
    test_services.py
    test_app.py
  .streamlit/config.toml
  .env.example
  .gitignore
  requirements.txt
  requirements-dev.txt
  Dockerfile
  .dockerignore
  README.md
```

## What works

- Overview, all files, collections, duplicates, recent analysis, plan, upload, and settings navigation.
- Visible dark/light toggle, responsive native layout, reusable document cards and detail view.
- Counts calculated from current state; analysis count explicitly separates demo and genuine AI results.
- Multiple TXT, UTF-8 Markdown, and text-based PDF uploads. Errors are shown per file.
- Full extracted text remains searchable. Search matches all meaningful query terms across filename, category, keywords, summary, and text, displaying the match source.
- Exact duplicate groups use original file bytes, not filenames, extracted text, or AI guesses.
- Review and approve individual organization suggestions. Only in-app collection assignments change.
- Editable summaries and categories; category edits update the proposed collection.
- Pending, Demo, AI analyzed, and Failed statuses. Failed items can be retried.
- Provider-specific adapters, environment configuration, network timeouts, HTTP error handling, and strict response validation.
- JSON downloads of the organization plan and workspace index.

## Configure real analysis

All credentials stay in `.env` on the app server. Restart Streamlit after changing it. The UI never asks for or displays secrets. Settings lets you select a provider without rewriting UI or extraction code.

### DigitalOcean

1. Obtain access to DigitalOcean serverless inference and a valid model access key or supported API token.
2. Copy the exact ID of a model enabled in your model catalog.
3. Set:

```dotenv
AI_PROVIDER=digitalocean
DIGITALOCEAN_API_KEY=your-key-here
DIGITALOCEAN_MODEL=your-enabled-model-id
```

The adapter calls the documented `https://inference.do-ai.run/v1/chat/completions` endpoint with bearer authentication.

### Snowflake

1. Obtain the HTTPS account URL, a Programmatic Access Token (PAT), and an enabled model ID.
2. Have your account administrator ensure your default role can use Cortex REST inference. Model availability and network policies vary by account and region.
3. Set:

```dotenv
AI_PROVIDER=snowflake
SNOWFLAKE_ACCOUNT_URL=https://your-account.snowflakecomputing.com
SNOWFLAKE_PAT=your-token-here
SNOWFLAKE_MODEL=your-enabled-model-id
```

The Snowflake adapter calls the documented `/api/v2/cortex/v1/chat/completions` endpoint on your account URL. This is an explicitly documented Chat Completions API, not an assumption that an older Cortex API has the same response format.

### Use either provider

Restart the app, import a document, select it, check the hosted-analysis consent box, and click Analyze. Existing sample results remain labeled Demo until re-analyzed. To re-analyze any existing file, open its detail page.

No live provider calls were verified during development because no account credentials were supplied. Adapter request/response paths were tested with simulated HTTP responses. A successful live call is still necessary to confirm your account permissions, model behavior, and hackathon eligibility. An error never silently switches to demo mode.

Official integration references checked for this build:

- https://docs.digitalocean.com/products/inference/how-to/use-chat-completions-api/
- https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-rest-api
- https://docs.streamlit.io/develop/api-reference/app-testing

## Two-minute demonstration

1. **0:00–0:20:** Open Overview. Explain the eight scattered fictional documents and identify the Demo label.
2. **0:20–0:40:** Add files. Upload `data/demo_files/project_v3.md` and run demo analysis (or your verified provider with consent).
3. **0:40–1:00:** Search `project proposal with budget`. Open the result and show the source text, summary and suggested collection.
4. **1:00–1:20:** Clear the search. Open Duplicate files and show the matching names and SHA-256 verification.
5. **1:20–1:45:** Open Organization plan. Select two files and approve their in-app destinations.
6. **1:45–2:00:** Return to Overview and switch themes. Close with “A little more space to think.”

Use Settings → Reset to fictional sample files to repeat the demo. Reset requires explicit confirmation and replaces the current in-app workspace. Original files are untouched.

## Test

From the project folder with the virtual environment active:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests cover exact duplicates, invalid/oversized files, empty PDFs, natural-language-style keyword searches, organization approval, missing credentials, structured responses, provider HTTP errors, navigation, search, themes and detail opening.

Validation for this delivery: 14 automated tests passed. Browser-based visual QA could not be completed because the browser binary download failed in the build environment. Live AI and container deployment were not exercised.

## Deploy

The app can run on a Python-capable server or container. For a Docker-capable host:

```bash
docker build -t clearspace .
docker run --rm -p 8501:8501 --env-file .env clearspace
```

Point your host's HTTPS route to container port 8501 and enable WebSocket forwarding. Inject environment variables through the host's secret configuration rather than committing `.env`. The Docker image excludes local environment files, uploaded files, and exports. This project has not been deployed or assigned a public URL.

For a hackathon, local demo mode is immediately repeatable. Before exposing live analysis publicly, put the deployment behind access control and add rate limits so strangers cannot spend your provider credits. There is no application authentication in this MVP.

## Limits and privacy

- Documents and metadata live only in the active Streamlit session. Reset/restart can lose them. Downloaded workspace JSON is an export, not a restorable backup; JSON re-import is not implemented.
- This app does not write uploaded originals to disk. File bytes are sent to the app host; “local extraction” means the machine running Streamlit, which may be a remote server when deployed.
- Hosted analysis sends the filename and the first 12,000 extracted characters only after consent. Longer files are analyzed from this excerpt, not their entire contents. Full extracted text remains available to search in-session.
- Limits: 10 MB per file, 100 PDF pages, 200,000 extracted characters per file, 100 imported documents per workspace. Very complex PDF pages are rejected. This is a trusted-user prototype, not a hardened public document parser.
- OCR, semantic embeddings, original-file downloads, durable accounts, cross-session syncing, real filesystem moves, deletion, and cloud-drive connections are not included.
- Search is lexical, not semantic: synonyms without shared words may not match. The explanation appears in the search UI.
- Sample documents are fictional. Files are not globally cached. Credentials and document text are not intentionally logged.
- Clear the search field to return to page navigation content.

## Two-person next steps

- **Developer 1:** Run the UI, rehearse the demo, adjust copy/colors in `components/ui.py`, and test uploads with your own non-sensitive sample files.
- **Developer 2:** Configure one provider, verify a real analysis, test quota/auth failures, and prepare the host configuration.
- **Together:** Verify the hackathon's platform requirement, record a successful end-to-end demo, and keep an offline demo-mode fallback ready.
