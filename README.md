# Meeting Transcription & Analyzer

A full-stack application for transcribing and analyzing meeting recordings using multiple AI models. Upload or download videos from Google Drive, transcribe them with Whisper or Google Speech-to-Text, and process the transcriptions with various LLMs to generate summaries, emails, and documentation.

![Tech Stack](https://img.shields.io/badge/Python-3.11+-blue)
![Tech Stack](https://img.shields.io/badge/FastAPI-0.109-green)
![Tech Stack](https://img.shields.io/badge/React-18-61DAFB)
![Tech Stack](https://img.shields.io/badge/TypeScript-5.3-3178C6)

## Features

### Media Management
- **Upload** MP4, MP3, WAV, M4A files (up to 500MB)
- **Google Drive Integration** - Download recordings by sharing with service account
- **Auto-conversion** - Convert videos to audio for faster transcription
- **Multi-select** operations with batch processing

### Transcription
- **Multiple Models**: Whisper (local), Whisper API (OpenAI), Google Speech-to-Text
- **Parallel Processing** with audio file prioritization
- **Direct Paste** - Import transcriptions from external sources
- **Language Support** - Multiple languages supported

### AI Processing
- **Built-in Prompts**: Meeting Summary, Partner Email, Training Documentation, Weekly Summary
- **Custom Prompts** - Create your own processing templates
- **Multiple LLMs**: OpenAI GPT-4/3.5, Google Gemini, Ollama (local models)
- **Personalization** - Apply writing personas to match individual styles
- **Templates** - Use email templates with placeholders

### Benchmarking
- **Model Comparison** - Compare transcription models side-by-side
- **LLM Evaluation** - Compare LLM outputs with LLM-as-judge scoring
- **Gemini Baseline** - Use Gemini as the baseline for fair comparisons

## Tech Stack

### Backend
- **Python 3.11+** with **FastAPI**
- **SQLAlchemy** ORM with **SQLite**
- **FFmpeg** for audio/video processing
- OpenAI, Google Cloud, Ollama integrations

### Frontend
- **React 18** with **TypeScript**
- **Vite** for fast development
- **Tailwind CSS** with custom gradients
- **Framer Motion** for animations
- **TanStack Query** for data fetching

## Color Scheme

The app features 8 beautiful gradient themes:
- **Solar** (Red-Orange) - CTAs and accents
- **Eclipse** (Dark Purple) - Default backgrounds
- **Lunar** (Cream-Pink) - Light mode
- **Celestial** (Cyan-Green) - Success states
- **Stratos** (Brown-Dark) - Cards
- **Cosmic** (Cream-Peach) - Light accents
- **Orbit** (Teal-Dark) - Navigation
- **Stardust** (Cream-Green) - Highlights

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- FFmpeg (for audio conversion)
- Ollama (optional, for local LLMs)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp env.example .env
# Edit .env with your API keys

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The app will be available at `http://localhost:5173`

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/app.db

# Storage
STORAGE_PATH=./storage
MAX_UPLOAD_SIZE_MB=500

# OpenAI (for GPT and Whisper API)
OPENAI_API_KEY=sk-your-key

# Google (for Gemini and Speech-to-Text)
GOOGLE_GEMINI_API_KEY=your-gemini-key
GOOGLE_APPLICATION_CREDENTIALS=./credentials/google-cloud.json

# Google Drive
GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/service-account.json
GOOGLE_DRIVE_SHARE_EMAIL=your-service@project.iam.gserviceaccount.com

# Ollama (local LLMs)
OLLAMA_HOST=http://localhost:11434

# Whisper
WHISPER_MODEL_SIZE=base
WHISPER_DEVICE=cpu
# Remote Whisper Server (e.g., via Tailscale: http://100.x.x.x:8001)
WHISPER_REMOTE_URL=
```

### Google Drive Setup

1. Create a Google Cloud project
2. Enable the Google Drive API
3. Create a service account and download the JSON key
4. Save as `credentials/service-account.json`
5. Share your Drive files with the service account email

### Ollama Setup (Optional)

For local LLM support:

```bash
# Install Ollama (macOS)
brew install ollama

# Pull models
ollama pull llama2
ollama pull mistral

# Start Ollama server
ollama serve
```

### Remote Whisper Server Setup (Optional)

Host Whisper on a separate server and connect via Tailscale for better performance or to offload processing:

#### On Your Remote Server:

1. **Install Tailscale** (if not already installed):
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://tailscale.com/install.sh | sh
   sudo tailscale up
   
   # macOS
   brew install tailscale
   tailscale up
   ```

2. **Note your Tailscale IP**:
   ```bash
   tailscale ip -4
   # Example output: 100.x.x.x
   ```

3. **Set up Whisper Server**:
   ```bash
   # Navigate to whisper-server directory
   cd whisper-server
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install FFmpeg (required)
   # Ubuntu/Debian:
   sudo apt install ffmpeg
   # macOS:
   brew install ffmpeg
   ```

4. **Run the Whisper server**:
   ```bash
   # Basic run
   python app.py
   
   # Or with specific host/port
   WHISPER_HOST=0.0.0.0 WHISPER_PORT=8001 python app.py
   ```

5. **Optional: Run as a systemd service** (see `whisper-server/README.md` for details)

#### On Your Main Application Server:

1. **Configure the remote URL** in your `.env` file:
   ```env
   WHISPER_REMOTE_URL=http://100.x.x.x:8001
   ```
   Replace `100.x.x.x` with your remote server's Tailscale IP.

2. **Restart your application** - Remote Whisper models will now appear in the transcription model selection.

3. **Test the connection**:
   ```bash
   curl http://100.x.x.x:8001/health
   ```

The remote Whisper models (`whisper-remote-base`, `whisper-remote-small`, etc.) will automatically appear in your transcription options when `WHISPER_REMOTE_URL` is configured.

**Benefits:**
- Offload CPU/GPU intensive transcription to a dedicated server
- Use GPU on remote server without needing GPU locally
- Share Whisper service across multiple applications
- Secure access via Tailscale private network

See `whisper-server/README.md` for detailed setup instructions and troubleshooting.

## Usage

### 1. Upload Media

Navigate to **Media Library** and:
- Drag & drop files or click to upload
- Paste Google Drive links to download recordings
- Select files for transcription

### 2. Transcribe

From **Media Library**:
- Select one or more files
- Click "Transcribe Selected"
- Choose transcription model
- Wait for processing

Or paste transcriptions directly in **Transcriptions** page.

### 3. Process with AI

Navigate to **Process**:
1. Select transcriptions from the sidebar
2. Choose a prompt type (Summary, Email, etc.)
3. Optionally enable persona/template
4. Select LLM model
5. Click "Generate Output"

### 4. Create Personas

In **Personas**, create writing style profiles:
- Add 3-5 sample emails
- Describe the writing style
- Apply to any processed output

### 5. Benchmark Models

In **Benchmark**:
- Compare transcription models (Whisper vs Google STT)
- Compare LLM outputs
- View scored results with judge reasoning

## API Documentation

When running, access the interactive API docs at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/media/upload` | POST | Upload media file |
| `/api/media/gdrive` | POST | Download from Google Drive |
| `/api/media` | GET | List all media |
| `/api/transcriptions/generate` | POST | Generate transcriptions |
| `/api/transcriptions/paste` | POST | Paste transcription |
| `/api/process` | POST | Process with LLM |
| `/api/personas` | CRUD | Manage personas |
| `/api/templates` | CRUD | Manage templates |
| `/api/benchmark/transcription` | POST | Run transcription benchmark |
| `/api/benchmark/llm` | POST | Run LLM benchmark |

## Project Structure

```
meeting_transcripot_and_analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Database setup
│   │   ├── models/              # SQLAlchemy models
│   │   ├── routers/             # API routes
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   │   ├── transcription/   # Whisper, Google STT
│   │   │   ├── llm/             # OpenAI, Gemini, Ollama
│   │   │   └── ...
│   │   └── utils/               # Utilities
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API client
│   │   ├── store/               # Zustand state
│   │   └── lib/                 # Utilities
│   ├── package.json
│   └── tailwind.config.js
├── storage/                     # File storage
│   ├── videos/
│   ├── audio/
│   └── transcriptions/
└── README.md
```

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Building for Production

```bash
# Frontend build
cd frontend
npm run build

# Backend with production server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

### FFmpeg not found
Install FFmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# Windows
choco install ffmpeg
```

### Whisper memory issues
Try a smaller model:
```env
WHISPER_MODEL_SIZE=tiny
```

### Ollama connection refused
Make sure Ollama is running:
```bash
ollama serve
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please open a GitHub issue.
