# HR AI Assistant - Deployment Guide

This repository contains a full-stack, production-grade HR AI Assistant using LangGraph, Qdrant Vector Store, and FastAPI.

## Prerequisites
1.  Python 3.11+
2.  Google Gemini API Key (`GOOGLE_API_KEY`)

---

## Free Deployment Options

Because we use **Qdrant** in local file-storage mode and **FastAPI** to serve both the frontend and backend, this application is perfectly suited for free, single-container deployment.

### Option 1: Render.com (Recommended Free Tier)

Render provides a completely free "Web Service" tier that builds and hosts Docker containers.

1.  Push this entire repository (including the `Dockerfile`) to a GitHub repository.
2.  Go to **[Render.com](https://render.com)** and sign in.
3.  Click **New +** -> **Web Service**.
4.  Connect your GitHub repository.
5.  **Important Settings:**
    *   **Runtime**: Docker
    *   **Instance Type**: Free
    *   **Environment Variables**: 
        *   Add `GOOGLE_API_KEY` and set it to your Gemini key.
6.  Click **Create Web Service**. 
7.  *(Note: On the free tier, Render wipes local storage if the container restarts. Since our Qdrant DB is generated via `ingest.py`, you may want to either execute `python ingest.py` periodically, or add a `RUN python ingest.py` statement inside your Dockerfile if you commit your raw PDF.)*

### Option 2: Hugging Face Spaces (Docker Space)

Hugging Face Spaces offers a highly capable free Docker tier specifically meant for AI applications.

1.  Create an account on **[Hugging Face](https://huggingface.co/)**.
2.  Create a **New Space**.
3.  Choose **Docker** as your Space SDK -> **Blank**.
4.  Upload your codebase to the space directly or clone it via Git.
5.  Go to the **Settings** tab of your space -> **Variables and secrets**.
6.  Add a New Secret:
    *   `Name`: `GOOGLE_API_KEY`
    *   `Value`: [Your Key]
7.  The space will automatically build your attached `Dockerfile` and expose port 8000. Your full-stack chat UI will be visible immediately.

---

## Running Locally

1. Create virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Generate the Qdrant local vector database from your PDF document:
   ```bash
   python ingest.py
   ```
3. Start the application:
   ```bash
   python main.py
   ```
4. Access the gorgeous Chat UI at `http://localhost:8000`
