
# ClearSpace AI

### AI-Powered Digital Organization & Intelligent Document Discovery

**Created by Shreya Gavande and Kavya Raval**

## 📌 Introduction

ClearSpace AI is an intelligent digital organization workspace that transforms scattered documents, research materials, notes, and PDFs into a clean, searchable digital library.

Using AI-powered document analysis, ClearSpace AI generates concise summaries, recommends relevant categories, extracts keywords, and suggests smarter ways to organize digital content.

Instead of manually sorting through endless folders and confusing filenames, users can upload documents, discover relevant information, detect duplicate files, and build a more organized digital workspace.

**Less time managing digital clutter, more time focusing on what matters.**

---

## 🎥 Demo

![ClearSpace AI Demo](Project%20Demo.gif)

---

## 🤔 Why ClearSpace AI?

Digital clutter makes it difficult to find information when it matters most. Important research gets buried, duplicate documents accumulate, and filenames rarely explain what a document actually contains.

ClearSpace AI helps solve these problems by:

- 📂 Bringing scattered documents into one organized workspace.
- 🤖 Generating meaningful summaries using AI when configured.
- 🔎 Helping users discover information through document search.
- 🧠 Recommending relevant categories and smart collections.
- 🔁 Identifying exact duplicate files using SHA-256 hashing.
- 🔒 Keeping users in control of their documents and organization decisions.

---

## 🚀 Features

### 📤 Intelligent File Import

- Upload multiple documents.
- Support `.txt`, `.md`, and text-based PDF files.
- Extract document text for analysis and discovery.
- Handle unsupported files and extraction errors gracefully.

### 🤖 AI-Powered Document Intelligence

When a hosted AI provider is configured, ClearSpace AI can:

- Generate concise document summaries.
- Recommend document categories and collections.
- Extract relevant keywords.
- Explain categorization recommendations.
- Support multiple AI providers through a modular service layer.

**Demo mode** is available without hosted AI credentials. It uses deterministic keyword rules and extracted text, not an AI model.

### 🔎 Smart Document Search

Search across filenames, extracted text, summaries, keywords, and categories to find information more easily.

Example searches:

- "Find my notes about photosynthesis."
- "Which document discusses climate change?"
- "Show me the project proposal with the budget."
- "Find my machine learning study materials."

The current search functionality is keyword-based. Embedding-based semantic search is a planned enhancement.

### 🔁 Duplicate Detection

- Identify exact duplicates using SHA-256 content hashes.
- Group files with identical contents.
- Display matching filenames and file sizes.
- Keep deletion decisions under the user's control.

### 🗂️ Smart Organization

- Recommend document categories and collections.
- Suggest meaningful collection names.
- Explain why a category was recommended.
- Allow users to review recommendations before applying changes.

### 📄 Document Details & Preview

- View document metadata and extracted text.
- Review summaries and keywords.
- Inspect document categories and suggested collections.
- Check analysis statuses and error messages.

### 🎨 User-Friendly Experience

- Clean dashboard and intuitive navigation.
- Overview metrics and smart collections.
- Dedicated views for files, duplicates, and recently analyzed documents.
- Organization planning and provider settings.
- Loading states, notifications, and error handling.

---

## ⚙️ How It Works

```text
       Document Upload
              ↓
   Text Extraction & Processing
              ↓
     Document Content Analysis
              ↓
   AI Summaries & Categorization
              ↓
     Search & Duplicate Detection
              ↓
    Organization Recommendations
              ↓
     A More Organized Workspace
```

ClearSpace AI separates document processing, AI analysis, search, and organization into modular services, making the application easier to maintain and extend.

---

## 🧠 AI Architecture

ClearSpace AI uses a provider-independent service layer to separate the application workflow from provider-specific API requests.

```text
             ClearSpace UI
                  ↓
          AI Service Interface
                  ↓
          Provider Selection
                  ↓
        ┌─────────┼─────────┐
        ↓         ↓         ↓
       Demo   Snowflake  DigitalOcean
              Cortex AI   Inference
```

### Supported Provider Modes

- **Demo:** Uses keyword rules and extracted text. No hosted AI model is called.
- **Snowflake:** Uses the Snowflake Cortex REST API when account access, authentication, and model configuration are set up correctly.
- **DigitalOcean:** Supports the configured DigitalOcean AI inference endpoint when valid credentials and a compatible model are available.

Actual AI analysis depends on valid credentials, model availability, account permissions, and successful API requests.

Provider-specific authentication, model requests, and response handling are isolated from the main application logic.

---

## 🔐 Privacy & Trust

ClearSpace AI is designed to give users control over document analysis and organization.

- **User consent:** The application asks for consent before sending document text to a hosted AI provider.
- **Limited text submission:** AI requests are limited to a maximum of 12,000 characters of document text.
- **Credential protection:** API credentials should be stored in environment variables or deployment secrets, never committed to source control.
- **Human-reviewed organization:** Users remain in control of organization recommendations and file deletion.
- **Transparent demo mode:** Demo results are distinguished from hosted AI analysis.
- **Error handling:** Failed requests should be reported rather than presented as successful analysis.

### Current Storage Limitations

The current application keeps its document library in Streamlit session state. It does not provide a persistent database-backed library, so documents and analysis results should not be assumed to survive a session reset or application restart.

When hosted AI is enabled, submitted document text is processed by the configured external provider and is subject to that provider's policies and retention practices. Avoid uploading sensitive documents unless you understand and accept those terms.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| User interface | Streamlit |
| Programming language | Python |
| PDF processing | pypdf |
| HTTP requests | httpx |
| Environment configuration | python-dotenv and Streamlit Secrets |
| AI service layer | Python provider adapters |
| AI platform options | Snowflake Cortex AI and DigitalOcean AI inference |
| Duplicate detection | SHA-256 hashing |
| Deployment option | Streamlit Community Cloud |

---

## 📂 Project Structure

```text
clearspace-AI/
├── app.py
├── services/
│   ├── ai_service.py
│   ├── file_reader.py
│   ├── search_service.py
│   ├── organizer.py
│   └── duplicates.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

The `services/` directory contains the application's processing and organization logic. The exact project structure may evolve as development continues.

---

## ⚡ Getting Started

### Prerequisites

- Python 3.10 or a compatible Python version for the installed dependencies.
- Git.
- Snowflake or DigitalOcean credentials if you want hosted AI analysis.
- No hosted AI credentials are required for demo mode.

### 1. Clone the Repository

```bash
git clone https://github.com/Clearspace-AI/clearspace-AI.git
cd clearspace-AI/clearspace-ai
```

If `app.py` is already in your current directory, skip the additional directory change.

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Your AI Provider

Copy `.env.example` to `.env` in the application directory and configure your preferred provider.

For Snowflake, use the following format:

```dotenv
AI_PROVIDER=snowflake
SNOWFLAKE_ACCOUNT_URL=https://YOUR_ACCOUNT_HOST.snowflakecomputing.com
SNOWFLAKE_PAT=YOUR_SNOWFLAKE_PROGRAMMATIC_ACCESS_TOKEN
SNOWFLAKE_MODEL=YOUR_AVAILABLE_MODEL_ID
```

Replace the placeholders with your actual Snowflake account hostname, programmatic access token, and a model supported by your account and the Cortex API.

**Important:**

- Use your Snowflake account's API hostname, not the Snowsight web application URL.
- Ensure your account permits the selected model and API access.
- Never commit `.env`, access tokens, or other secrets to GitHub.
- For demo mode, set `AI_PROVIDER=demo`.

For DigitalOcean, configure `DIGITALOCEAN_API_KEY` and `DIGITALOCEAN_MODEL` in your environment file.

### 5. Run the Application

From the directory containing `app.py`, run:

```bash
python -m streamlit run app.py
```

Open the local URL displayed in your terminal to access ClearSpace AI.

---

## ☁️ Deployment

### Streamlit Community Cloud

1. Push your project to GitHub.
2. Create a new app in Streamlit Community Cloud.
3. Select the repository, branch, and application entrypoint.
4. Add your AI provider configuration under the app's Secrets settings.
5. Deploy the app and test document upload and analysis.

Example Snowflake secrets configuration:

```toml
AI_PROVIDER = "snowflake"
SNOWFLAKE_ACCOUNT_URL = "https://YOUR_ACCOUNT_HOST.snowflakecomputing.com"
SNOWFLAKE_PAT = "YOUR_SNOWFLAKE_PROGRAMMATIC_ACCESS_TOKEN"
SNOWFLAKE_MODEL = "YOUR_AVAILABLE_MODEL_ID"
```

Use real values only in your deployment's secrets manager, not in README files or committed source code.

After deployment, verify demo mode and hosted AI analysis, if enabled.

---

## 🌱 Future Enhancements

- 🔍 Embedding-based semantic search.
- ☁️ Secure cloud-drive integrations.
- 🧩 Related-document discovery.
- 📁 User-approved filesystem organization.
- 💾 Persistent document libraries and database integration.
- 🔐 User authentication and workspace permissions.
- 📊 Advanced document insights and analytics.
- 🤖 Expanded AI provider integrations.
- 📱 Improved mobile experience.

---

## 👩‍💻 Built By

**Shreya Gavande and Kavya Raval**

ClearSpace AI was developed as a hackathon project exploring the intersection of **Artificial Intelligence, Productivity, and Intelligent Information Management**.

Our goal is to make digital organization easier by transforming scattered information into a workspace that is more searchable, understandable, and manageable.

### ✨ Less clutter. Better discovery. More clarity.

---

## 📄 License

MIT License.
