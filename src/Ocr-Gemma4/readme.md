# Terminal 1: make sure Ollama is serving

ollama serve

# Terminal 2: start the API

```bash
uvicorn --app-dir src/Ocr-Gemma4 scanner:app --reload --host 0.0.0.0
```

Or run it from inside this folder:

```bash
cd src/Ocr-Gemma4
uvicorn scanner:app --reload --host 0.0.0.0
```

## Health checks

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/health/ollama
```

Supported uploads:

- Image files for OCR
- PDF files, including scanned PDFs

Note: scanned PDFs require `PyMuPDF` for page rendering.

## Open the UI

Open `http://<your-machine-ip>:8000/` in your browser after starting uvicorn with `--host 0.0.0.0`.
