# NovaRAG 🚀

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Microsoft Foundry Local](https://img.shields.io/badge/AI-Microsoft%20Foundry%20Local-0078D4.svg)](https://github.com/microsoft/foundry-local)

NovaRAG is a **100% offline**, privacy-first Retrieval-Augmented Generation (RAG) assistant. It allows you to query your private documents locally without sending any data to cloud APIs.

## 🌟 Key Features
- **Total Privacy**: Runs entirely on your local machine using **Microsoft Foundry Local**.
- **Multi-Model Support**: Switch seamlessly between models like phi-3.5-mini and qwen2.5-1.5b.
- **Hybrid Search**: Uses SQLite and local embeddings (CPU) for fast cosine & BM25 similarity searches.
- **Beautiful UI**: Modern, responsive frontend served via Flask with live architecture metrics.

## 🚀 Quick Start

1. **Install Dependencies**
   `ash
   pip install -r requirements.txt
   `

2. **Run the Application**
   `ash
   python app.py
   `

3. **Use the App**
   Open your browser and navigate to http://127.0.0.1:5000. Upload your .txt, .md, or .pdf files from the left sidebar, click **Re-Ingest**, and start asking questions!

## 🛠️ Architecture
- **Backend**: Python, Flask, SQLite
- **AI/LLM**: Microsoft Foundry Local SDK (oundry-local-sdk)
- **Embeddings**: sentence-transformers
- **Frontend**: HTML5, Vanilla JS, Custom CSS
