# WriteFlow AI

WriteFlow AI is a Streamlit app that turns a topic into a polished blog post using Google Gemini. It creates an outline, writes a draft, and polishes the final post.

## Requirements

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/)
- A Google Gemini API key

## Setup

Clone the repository and install the locked dependencies:

```bash
uv sync
```

Create a `.env` file in the project root and add your API key:

```dotenv
GOOGLE_API_KEY=your_google_api_key
```

Start the app:

```bash
uv run streamlit run app.py
```

Use the sidebar to enter a topic and choose a tone. The generated post appears on the main page.

## Author

**SUMIT KUMAR** — [GitHub](https://github.com/SUMITK82) · [kumarsumit20050512@gmail.com](mailto:kumarsumit20050512@gmail.com)
