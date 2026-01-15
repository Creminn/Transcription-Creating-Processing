# Product Requirements Document (PRD)
## Meeting Transcription & Analyzer Application

**Version:** 1.0  
**Last Updated:** January 15, 2026  
**Status:** Draft

---

## 1. Executive Summary

### 1.1 Product Vision
A comprehensive meeting transcription and analysis platform that enables users to transcribe audio/video recordings using multiple AI models, process transcriptions with customizable prompts, personalize outputs with personas and templates, and benchmark different AI models for quality comparison.

### 1.2 Target Users
- Business professionals managing meeting documentation
- Teams needing automated meeting summaries and follow-up emails
- Organizations wanting to evaluate and compare AI transcription/processing models
- Trainers creating educational documentation from recorded sessions

### 1.3 Key Value Propositions
- Multi-source media input (upload, Google Drive, direct paste)
- Flexible transcription with multiple AI model support
- Customizable output generation with personas and templates
- Built-in benchmarking for model comparison

---

## 2. Product Overview

### 2.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│
│  │  Media   │ │Transcript│ │ Process  │ │ Personas │ │Benchmark││
│  │ Library  │ │  Menu    │ │  Center  │ │Templates │ │  Page  ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      API Layer                            │  │
│  │  /media  /transcriptions  /process  /personas  /benchmark │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Service Layer                          │  │
│  │  GDrive │ Whisper │ Google STT │ OpenAI │ Gemini │ Ollama │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Data Layer                             │  │
│  │              SQLite + File Storage                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Tech Stack
| Component | Technology |
|-----------|------------|
| Frontend | React 18 + TypeScript + Vite |
| Styling | Tailwind CSS + Framer Motion |
| Backend | Python 3.11+ + FastAPI |
| Database | SQLite + SQLAlchemy |
| File Storage | Local filesystem |
| Transcription | Whisper (local/API), Google STT |
| LLM Processing | OpenAI GPT, Google Gemini, Ollama |

---

## 3. Feature Requirements

### 3.1 Media Library (FR-100)

#### FR-101: File Upload
- **Description:** Users can upload MP4 and MP3 files from their local machine
- **Acceptance Criteria:**
  - Drag-and-drop upload support
  - File picker button alternative
  - Progress indicator during upload
  - Supported formats: MP4, MP3, WAV, M4A
  - Maximum file size: 500MB (configurable)
  - Automatic format detection and categorization

#### FR-102: Google Drive Download
- **Description:** Users can download video recordings from Google Drive
- **Acceptance Criteria:**
  - User shares file to configured service email
  - User pastes shareable link in the application
  - Backend validates link and initiates download
  - Download progress shown to user
  - Automatic MP4 to MP3 conversion option
  - Error handling for invalid/inaccessible links

#### FR-103: Media List View
- **Description:** Display all uploaded/downloaded media files
- **Acceptance Criteria:**
  - Separate tabs for MP4 and MP3 files
  - Card view showing: filename, source icon, date, duration, status
  - Search and filter capabilities
  - Sorting by date, name, size
  - Pagination for large libraries

#### FR-104: Media Management
- **Description:** Users can manage their media files
- **Acceptance Criteria:**
  - Delete individual files with confirmation
  - Bulk delete selected files
  - Multi-select with checkboxes
  - "Select All" / "Deselect All" options

#### FR-105: Transcription Queue
- **Description:** Users can queue selected media for transcription
- **Acceptance Criteria:**
  - Multi-select files across MP4 and MP3 tabs
  - "Transcribe Selected" action button
  - MP3 files prioritized but processed in parallel with MP4
  - Model selector for transcription (Whisper local, Whisper API, Google STT)
  - Queue status display

---

### 3.2 Transcription Management (FR-200)

#### FR-201: Transcription from Media
- **Description:** Generate transcriptions from media files
- **Acceptance Criteria:**
  - Support for Whisper local model
  - Support for OpenAI Whisper API
  - Support for Google Speech-to-Text
  - Parallel processing capability
  - Progress tracking per file
  - Automatic timestamp generation

#### FR-202: Direct Transcription Paste
- **Description:** Users can paste transcriptions from external sources
- **Acceptance Criteria:**
  - Large text area for pasting content
  - Metadata fields: title, date, source
  - Validation for minimum content length
  - Save as standalone transcription

#### FR-203: Transcription List
- **Description:** View and manage all transcriptions
- **Acceptance Criteria:**
  - List view with preview snippets
  - Filter by source (model name or "pasted")
  - Filter by date range
  - Search within transcription content
  - Link to original media (if applicable)

#### FR-204: Transcription Selection
- **Description:** Select multiple transcriptions for processing
- **Acceptance Criteria:**
  - Multi-select checkboxes
  - Selected count indicator
  - "Process Selected" action button
  - Selection persists across page navigation

---

### 3.3 Prompt Processing (FR-300)

#### FR-301: Built-in Prompt Templates
- **Description:** Pre-configured prompt types for common use cases
- **Acceptance Criteria:**
  - Meeting Summary: Concise bullet-point summary
  - Partner Email: Formal meeting notes email
  - Training Documentation: Educational material format
  - Weekly Summary: Aggregated summary for multiple meetings
  - Custom Prompt: Free-form user input

#### FR-302: Transcription Combining
- **Description:** Combine multiple transcriptions for processing
- **Acceptance Criteria:**
  - Select 1 or more transcriptions
  - Automatic chronological ordering
  - Combined context sent to LLM
  - Individual transcription metadata preserved

#### FR-303: LLM Model Selection
- **Description:** Choose which LLM to use for processing
- **Acceptance Criteria:**
  - OpenAI GPT-4 / GPT-3.5 options
  - Google Gemini options
  - Ollama local models (dynamic list from running instance)
  - Model availability indicators

#### FR-304: Output Generation
- **Description:** Generate and display processed output
- **Acceptance Criteria:**
  - Real-time streaming output display
  - Copy to clipboard button
  - Export as text/markdown file
  - Save to history
  - Regenerate option

---

### 3.4 Persona Management (FR-400)

#### FR-401: Persona Creation
- **Description:** Create writing style personas based on sample content
- **Acceptance Criteria:**
  - Name field for persona identification
  - Text area for sample emails (minimum 3 recommended)
  - Auto-generated style description from samples
  - Manual style description override option
  - Guidance tooltip explaining best practices

#### FR-402: Persona Application
- **Description:** Apply persona to output generation
- **Acceptance Criteria:**
  - Toggle switch: "Personalize the email"
  - Persona selector dropdown (when toggle enabled)
  - Preview of persona style
  - Persona context injected into LLM prompt

#### FR-403: Persona Management
- **Description:** Edit and delete existing personas
- **Acceptance Criteria:**
  - List view of all personas
  - Edit functionality for all fields
  - Delete with confirmation
  - Duplicate persona option

---

### 3.5 Email Template Management (FR-500)

#### FR-501: Template Creation
- **Description:** Create reusable email templates with placeholders
- **Acceptance Criteria:**
  - Name and category fields
  - Template content editor
  - Supported placeholders: `{{meeting_date}}`, `{{attendees}}`, `{{summary}}`, `{{action_items}}`, `{{next_steps}}`
  - Placeholder reference guide
  - Template preview with sample data

#### FR-502: Template Application
- **Description:** Apply template to output generation
- **Acceptance Criteria:**
  - Toggle switch: "Use email template"
  - Template selector dropdown (when toggle enabled)
  - Template preview
  - Placeholder auto-fill from transcription data

#### FR-503: Template Management
- **Description:** Edit and delete existing templates
- **Acceptance Criteria:**
  - List view filtered by category
  - Full edit capability
  - Delete with confirmation
  - Duplicate template option

---

### 3.6 Benchmarking (FR-600)

#### FR-601: Transcription Model Benchmark
- **Description:** Compare transcription quality across models
- **Acceptance Criteria:**
  - Select audio file for testing
  - Select models to compare (minimum 2)
  - Google STT as baseline reference
  - Side-by-side output display
  - LLM-as-judge quality scoring
  - Detailed reasoning for scores
  - Save benchmark results

#### FR-602: LLM Processing Benchmark
- **Description:** Compare LLM output quality for prompt processing
- **Acceptance Criteria:**
  - Select transcription input
  - Select prompt type
  - Select models to compare (minimum 2)
  - Google Gemini as baseline reference
  - Side-by-side output display
  - LLM-as-judge quality scoring
  - Metrics: accuracy, coherence, completeness, style
  - Save benchmark results

#### FR-603: Benchmark History
- **Description:** View past benchmark results
- **Acceptance Criteria:**
  - List of all benchmark runs
  - Filter by benchmark type
  - Filter by date range
  - Detailed view for each result
  - Export results as JSON/CSV

---

## 4. User Interface Requirements

### 4.1 Design System

#### 4.1.1 Color Palette (Gradients)
| Name | Start Color | End Color | Usage |
|------|-------------|-----------|-------|
| Solar | #E92E2F | #FF6126 | Primary CTAs, highlights |
| Eclipse | #261A28 | #18181B | Dark backgrounds, headers |
| Lunar | #EFEBE4 | #D0C2C7 | Light backgrounds |
| Celestial | #2EDFE2 | #71F3A7 | Success states, accents |
| Stratos | #44221E | #18181B | Secondary dark elements |
| Cosmic | #EFEBE4 | #F0CABF | Warm light surfaces |
| Orbit | #23423D | #18181B | Navigation, sidebars |
| Stardust | #EFEBE4 | #CFEBDD | Cards, panels |

#### 4.1.2 Animation Requirements
- Page transitions: Smooth fade/slide (300ms)
- Card hover effects: Subtle scale and shadow
- Button interactions: Press feedback with scale
- Loading states: Skeleton loaders with shimmer
- Toast notifications: Slide-in from top-right
- Modal dialogs: Fade backdrop + scale content
- List items: Staggered entrance animation
- Progress indicators: Smooth progress with glow effect

### 4.2 Page Layouts

#### 4.2.1 Navigation
- Sidebar navigation with icon + label
- Collapsible on mobile
- Active state indicator with gradient accent
- Pages: Media Library, Transcriptions, Process, Personas, Templates, Benchmark, Settings

#### 4.2.2 Responsive Design
- Desktop: Full sidebar + content area
- Tablet: Collapsible sidebar
- Mobile: Bottom navigation bar

---

## 5. Data Models

### 5.1 Media
```
Media {
  id: Integer (PK, auto-increment)
  filename: String (required)
  original_filename: String (required)
  filepath: String (required)
  file_type: Enum ['mp4', 'mp3', 'wav', 'm4a']
  source: Enum ['upload', 'gdrive', 'converted']
  file_size: Integer (bytes)
  duration: Integer (seconds, nullable)
  gdrive_link: String (nullable)
  is_processed: Boolean (default: false)
  created_at: DateTime
  updated_at: DateTime
}
```

### 5.2 Transcription
```
Transcription {
  id: Integer (PK, auto-increment)
  media_id: Integer (FK -> Media, nullable)
  title: String (required)
  content: Text (required)
  model_used: String (nullable, e.g., 'whisper-large', 'google-stt')
  source_type: Enum ['model', 'pasted']
  language: String (default: 'en')
  duration_seconds: Integer (nullable)
  word_count: Integer
  created_at: DateTime
  updated_at: DateTime
}
```

### 5.3 Persona
```
Persona {
  id: Integer (PK, auto-increment)
  name: String (required, unique)
  sample_emails: JSON (array of strings)
  style_description: Text (required)
  is_active: Boolean (default: true)
  created_at: DateTime
  updated_at: DateTime
}
```

### 5.4 EmailTemplate
```
EmailTemplate {
  id: Integer (PK, auto-increment)
  name: String (required)
  category: Enum ['meeting_notes', 'follow_up', 'summary', 'training', 'custom']
  template_content: Text (required)
  placeholders: JSON (array of used placeholders)
  is_active: Boolean (default: true)
  created_at: DateTime
  updated_at: DateTime
}
```

### 5.5 ProcessedOutput
```
ProcessedOutput {
  id: Integer (PK, auto-increment)
  prompt_type: String (required)
  transcription_ids: JSON (array of integers)
  persona_id: Integer (FK -> Persona, nullable)
  template_id: Integer (FK -> EmailTemplate, nullable)
  llm_model: String (required)
  input_tokens: Integer
  output_tokens: Integer
  output_content: Text (required)
  created_at: DateTime
}
```

### 5.6 BenchmarkResult
```
BenchmarkResult {
  id: Integer (PK, auto-increment)
  benchmark_type: Enum ['transcription', 'llm_processing']
  test_name: String (required)
  input_reference: String (media_id or transcription_id)
  model_a: String (required)
  model_b: String (required)
  output_a: Text (required)
  output_b: Text (required)
  score_a: Float
  score_b: Float
  judge_model: String (required)
  judge_reasoning: Text
  metrics: JSON (detailed scores)
  created_at: DateTime
}
```

---

## 6. API Specifications

### 6.1 Media Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/media/upload` | Upload media file |
| POST | `/api/media/gdrive` | Download from Google Drive |
| GET | `/api/media` | List media with filters |
| GET | `/api/media/{id}` | Get media details |
| DELETE | `/api/media/{id}` | Delete media file |
| POST | `/api/media/convert/{id}` | Convert MP4 to MP3 |

### 6.2 Transcription Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/transcriptions/generate` | Generate from media |
| POST | `/api/transcriptions/paste` | Create from pasted text |
| GET | `/api/transcriptions` | List transcriptions |
| GET | `/api/transcriptions/{id}` | Get transcription details |
| DELETE | `/api/transcriptions/{id}` | Delete transcription |

### 6.3 Processing Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/process` | Process transcriptions |
| GET | `/api/process/history` | Get processing history |
| GET | `/api/process/prompts` | Get available prompt types |

### 6.4 Persona Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/personas` | Create persona |
| GET | `/api/personas` | List personas |
| GET | `/api/personas/{id}` | Get persona details |
| PUT | `/api/personas/{id}` | Update persona |
| DELETE | `/api/personas/{id}` | Delete persona |

### 6.5 Template Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/templates` | Create template |
| GET | `/api/templates` | List templates |
| GET | `/api/templates/{id}` | Get template details |
| PUT | `/api/templates/{id}` | Update template |
| DELETE | `/api/templates/{id}` | Delete template |

### 6.6 Benchmark Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/benchmark/transcription` | Run transcription benchmark |
| POST | `/api/benchmark/llm` | Run LLM benchmark |
| GET | `/api/benchmark/results` | List benchmark results |
| GET | `/api/benchmark/results/{id}` | Get result details |

### 6.7 Settings Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/settings` | Get current settings |
| PUT | `/api/settings` | Update settings |
| GET | `/api/settings/models` | Get available models |

---

## 7. Non-Functional Requirements

### 7.1 Performance
- File upload: Handle files up to 500MB
- Transcription: Process 1 hour of audio in < 10 minutes (local Whisper)
- API response: < 200ms for list operations
- UI: 60fps animations, < 3s initial load

### 7.2 Security
- API key storage: Environment variables, never in code
- File validation: Type checking, size limits
- Input sanitization: All user inputs sanitized
- CORS: Configured for frontend origin only

### 7.3 Reliability
- Database: Automatic backups daily
- File storage: Organized directory structure
- Error handling: Graceful degradation, user-friendly messages
- Logging: Structured logging for debugging

### 7.4 Scalability
- Async processing: Background task queue for transcription
- Database: SQLite suitable for single-user, upgrade path to PostgreSQL
- File storage: Local with configurable path

---

## 8. Configuration Requirements

### 8.1 Environment Variables
```
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Database
DATABASE_URL=sqlite:///./data/app.db

# Storage
STORAGE_PATH=./storage
MAX_UPLOAD_SIZE_MB=500

# Google Drive
GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/service-account.json
GOOGLE_DRIVE_SHARE_EMAIL=service@project.iam.gserviceaccount.com

# OpenAI
OPENAI_API_KEY=sk-...

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=./credentials/google-cloud.json
GOOGLE_GEMINI_API_KEY=...

# Ollama
OLLAMA_HOST=http://localhost:11434

# Whisper
WHISPER_MODEL_SIZE=large-v3
WHISPER_DEVICE=cuda  # or cpu
```

---

## 9. Implementation Phases

### Phase 1: Foundation (Core Infrastructure)
1. Project setup (backend + frontend scaffolding)
2. Database models and migrations
3. File storage system
4. Basic API structure
5. Frontend routing and layout

### Phase 2: Media Management
1. File upload functionality
2. Google Drive integration
3. Media list with tabs
4. Delete and multi-select
5. MP4 to MP3 conversion

### Phase 3: Transcription
1. Whisper local integration
2. Whisper API integration
3. Google STT integration
4. Parallel processing
5. Direct paste functionality
6. Transcription list and management

### Phase 4: Prompt Processing
1. Built-in prompt templates
2. Multi-transcription combining
3. LLM service integrations (OpenAI, Gemini, Ollama)
4. Output generation and display
5. Processing history

### Phase 5: Personalization
1. Persona CRUD operations
2. Persona application to processing
3. Template CRUD operations
4. Template application to processing
5. Guidance and help system

### Phase 6: Benchmarking
1. Transcription benchmark system
2. LLM benchmark system
3. LLM-as-judge implementation
4. Results storage and display
5. Export functionality

### Phase 7: Polish
1. Full animation implementation
2. Color scheme application
3. Responsive design
4. Error handling improvements
5. Documentation

---

## 10. Success Metrics

| Metric | Target |
|--------|--------|
| Transcription accuracy | > 95% WER on clear audio |
| Processing time | < 2 minutes for 30-min meeting |
| User task completion | Upload to output in < 5 clicks |
| System uptime | 99% availability |

---

## Appendix A: Glossary

- **WER**: Word Error Rate - measure of transcription accuracy
- **LLM**: Large Language Model
- **STT**: Speech-to-Text
- **Persona**: Writing style profile based on sample content
- **Template**: Reusable content structure with placeholders

---

## Appendix B: References

- OpenAI Whisper: https://github.com/openai/whisper
- Google Speech-to-Text: https://cloud.google.com/speech-to-text
- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- Framer Motion: https://www.framer.com/motion
