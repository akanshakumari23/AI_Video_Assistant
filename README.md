# 🎙️ Verbatim AI — Meeting Intelligence Platform

**Live Demo:** [Verbatim AI Demo](https://verbatim-ai-production.up.railway.app/)

Verbatim AI is an AI-powered Meeting Intelligence Platform that transforms meeting recordings, lectures, interviews, and video content into structured, actionable insights. It automates transcription, summarization, decision extraction, action item generation, and conversational Q&A using Retrieval-Augmented Generation (RAG).

The platform combines speech recognition, LLM-powered analysis, vector search, and an intuitive Streamlit interface to help users save time and improve productivity.

---

## 🚀 Features

### 🎧 Multi-Source Audio Processing

* YouTube URL support
* MP3, MP4, WAV file processing
* Automatic audio conversion and chunking
* Long-form meeting support

### 🗣️ AI-Powered Transcription

* Whisper-based speech recognition
* Sarvam AI integration
* English and Hinglish support
* Automatic transcript generation

### 📝 Intelligent Meeting Analysis

* AI-generated meeting summaries
* Automatic meeting title generation
* Key decisions extraction
* Action items identification
* Open questions detection

### 🔍 RAG-Powered Chat

* Ask questions about any uploaded meeting
* Semantic search over transcripts
* Context-aware responses
* Meeting knowledge retrieval

### 🌐 Modern UI

* Dark futuristic interface
* Responsive Streamlit dashboard
* Real-time processing feedback
* Interactive analytics cards

---

## 🛠️ Tech Stack

### Frontend

* Streamlit
* Custom CSS
* Interactive Components

### AI & NLP

* Mistral AI
* Whisper
* Sarvam AI
* LangChain
* HuggingFace Embeddings

### RAG & Vector Database

* ChromaDB
* Sentence Transformers
* LangChain Retrieval

### Audio Processing

* yt-dlp
* FFmpeg
* Pydub

### Deployment

* Railway
* GitHub

---

## 🏗️ System Architecture

```text
YouTube/File Input
        │
        ▼
 Audio Processing
        │
        ▼
 Transcription
(Whisper / Sarvam)
        │
        ▼
 Transcript
        │
 ┌──────┼──────┐
 ▼      ▼      ▼
Summary Decisions Actions
        │
        ▼
 Vector Store
   (ChromaDB)
        │
        ▼
 RAG Chat System
        │
        ▼
 User Insights
```

---

## 📸 Core Capabilities

### Meeting Summarization

Generate concise summaries from lengthy meetings automatically.

### Action Item Detection

Identify tasks, owners, and responsibilities discussed during meetings.

### Decision Tracking

Extract important decisions and resolutions made during discussions.

### Intelligent Search

Ask questions such as:

* What decisions were made?
* What are the pending action items?
* What deadlines were discussed?
* Who is responsible for each task?

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/akanshakumari23/AI_Video_Assistant.git
cd AI_Video_Assistant
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
MISTRAL_API_KEY=your_mistral_api_key
SARVAM_API_KEY=your_sarvam_api_key
```

---

## ▶️ Run Application

```bash
streamlit run app.py
```

Application will be available at:

```text
http://localhost:8501
```

---

## 🌐 Live Deployment

**Railway Deployment**

Demo Link:

https://verbatim-ai-production.up.railway.app/

---

## 📂 Project Structure

```text
AI_Video_Assistant/
│
├── app.py
├── main.py
├── requirements.txt
│
├── core/
│   ├── extractor.py
│   ├── rag_engine.py
│   ├── summarizer.py
│   ├── transcriber.py
│   └── vector_store.py
│
├── utils/
│   └── audio_processor.py
│
├── vector_db/
├── streamlit/
└── .env
```

---

## 🎯 Use Cases

* Business Meetings
* Team Standups
* Client Calls
* Online Lectures
* Interviews
* Podcasts
* Research Discussions
* Corporate Documentation

---

## 🔮 Future Enhancements

* Speaker Diarization
* Meeting Sentiment Analysis
* Multi-language Summaries
* Email Integration
* Calendar Integration
* Team Collaboration Dashboard
* PDF Report Export
* Meeting Analytics

---

## 👩‍💻 Author

**Akansha Kumari**

B.Tech Electrical Engineering
MNNIT Allahabad

GitHub: https://github.com/akanshakumari23

---

## ⭐ Support

If you found this project useful:

⭐ Star the repository

🍴 Fork the project

📝 Share feedback and suggestions

---

Built with ❤️ using Streamlit, LangChain, Mistral AI, Sarvam AI, Whisper, and ChromaDB.
