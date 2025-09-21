# Automated Resume Relevance Check System

## 📋 Problem Statement

At **Innomatics Research Labs**, resume evaluation is currently manual, inconsistent, and time-consuming. Every week, the placement team across Hyderabad, Bangalore, Pune, and Delhi NCR receives **18–20 job requirements**, with each posting attracting **thousands of applications**.

### Current Challenges:
- **Delays in shortlisting candidates** due to manual review process
- **Inconsistent judgments** as evaluators interpret role requirements differently
- **High workload for placement staff**, reducing their ability to focus on interview prep and student guidance
- **Fast and high-quality shortlists** expected by hiring companies

### System Objectives:
-  **Automate resume evaluation** against job requirements at scale
-  **Generate Relevance Score (0–100)** for each resume per job role
-  **Highlight gaps** such as missing skills, certifications, or projects
-  **Provide fit verdict** (High / Medium / Low suitability) to recruiters
-  **Offer personalized improvement feedback** to students
-  **Store evaluations** in a web-based dashboard accessible to the placement team
-  **Handle thousands of resumes weekly** with robust, scalable, flexible architecture

##  System Architecture

### Proposed Solution
The system implements an **AI-powered resume evaluation engine** that combines rule-based checks with LLM-based semantic understanding:

```
Job Description Upload → Resume Upload → Evaluation Pipeline → Results Dashboard
                                    ↓
                    [Hard Match + Soft Match + ATS Check]
                                    ↓
                    [Keyword Scoring + Semantic Analysis + ATS Compatibility]
                                    ↓
                    [Relevance Score + Missing Elements + Verdict + Feedback]
```

### Core Workflow
1. **Job Requirement Upload** - Placement team uploads job description (JD)
2. **Resume Upload** - Students upload resumes while applying
3. **Resume Parsing** - Extract and standardize text from PDF/DOCX
4. **JD Parsing** - Extract role title, skills, qualifications
5. **Relevance Analysis**:
   - **Hard Match** – Keyword & skill check (exact and fuzzy matches)
   - **Semantic Match** – Embedding similarity + LLM reasoning
   - **ATS Check** – Resume format compatibility analysis
6. **Scoring & Verdict** – Weighted scoring formula for final score
7. **Output Generation** – Scores, missing elements, verdict, feedback
8. **Storage & Access** – Results stored in searchable dashboard

## Technology Stack

### **Implemented Technologies**

#### **Core AI Framework & Scoring**
- **Python** - Primary programming language ✅
- **PyMuPDF** - PDF text extraction ✅
- **python-docx & docx2txt** - DOCX text extraction ✅
- **spaCy & NLTK** - Entity extraction and text normalization ✅
- **LangChain** - LLM workflow orchestration ✅
- **LangGraph** - Structured stateful pipelines ✅
- **ChromaDB** - Vector store for embeddings ✅ (with fallback)
- **OpenAI GPT** - Semantic matching & feedback generation ✅ (with fallback)
- **TF-IDF & scikit-learn** - Keyword matching and similarity ✅
- **Sentence Transformers** - Embeddings generation ✅ (with fallback)

#### **Web Application**
- **Flask** - Backend APIs and web framework ✅
- **HTML/CSS/JavaScript (Bootstrap)** - Frontend interface ✅
- **PostgreSQL** - Database for storing results ✅
- **SQLAlchemy** - ORM for database operations ✅

#### **Additional Features**
- **ATS Compatibility Service** - Resume format optimization ✅
- **Bulk Processing** - Multiple resume handling ✅
- **Semantic Search** - Vector-based similarity matching ✅
- **Comprehensive Scoring** - Multi-dimensional evaluation ✅

##  System Features

1. **Resume & Job Description Parsing**
   - PDF and DOCX text extraction
   - Skills, education, experience extraction
   - Job requirement parsing (must-have/good-to-have skills)

2. **Multi-Dimensional Evaluation**
   - **Keyword Score** (0-100) - Hard skill matching
   - **Semantic Score** (0-100) - Contextual understanding
   - **ATS Score** (0-100) - Resume format compatibility
   - **Final Score** (0-100) - Weighted combination

3. **Intelligent Analysis**
   - Missing skills identification
   - Resume strength analysis
   - ATS optimization tips
   - Personalized improvement feedback

4. **Web Dashboard**
   - Upload interface for JDs and resumes
   - Evaluation results display
   - Bulk processing capabilities
   - Search and filter functionality
   - Detailed result views

5. **API Endpoints**
   - `/api/evaluate` - Programmatic evaluation
   - `/api/similar-resumes` - Vector similarity search
   - `/api/ats-check` - ATS compatibility check

6. **Database Schema**
   - Job descriptions storage
   - Resume metadata storage
   - Comprehensive evaluation results
   - Bulk upload session tracking

### 🔄 **Fallback Implementations**

1. **Embedding Service**
   - **Primary**: Sentence Transformers + ChromaDB
   - **Fallback**: TF-IDF similarity calculation

2. **LLM Service**
   - **Primary**: OpenAI GPT-3.5-turbo
   - **Fallback**: Basic rule-based feedback generation

3. **Vector Storage**
   - **Primary**: ChromaDB with persistent storage
   - **Fallback**: In-memory storage for session

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.9+**
- **PostgreSQL** 
- **OpenAI API Key** 

### Step 1: Clone Repository
```bash
git clone https://github.com/SmrutiBhuyan/Automated-Resume-Relevance-Check-System.git
cd Resume-Relevance-automated-system
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Download NLP Models
```python
# Download NLTK data
import nltk
nltk.download('punkt')
nltk.download('stopwords')

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Step 5: Environment Configuration
Create a `.env` file in the root directory:
```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DB_URL=postgresql://username:password@localhost/database_name

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

### Step 6: Database Setup
#### For PostgreSQL:
```bash
# Run PostgreSQL migration
python migrate_postgresql.py
```

#### For SQLite:
```bash
# Initialize database
python migrate_database.py
```

### Step 7: Test System
```bash
# Run comprehensive tests
python test_system.py
```

### Step 8: Launch Application
```bash
# Start Flask application
python run.py
```

The application will be available at: `http://localhost:5000`

## 📖 Usage Guide

### Web Interface

#### 1. **Upload Job Description**
- Navigate to `/upload`
- Select "Job Description" tab
- Upload PDF/DOCX files with job requirements
- System automatically parses skills and qualifications

#### 2. **Upload Resumes**

**Single Resume Evaluation:**
- Select "Single Resume" tab
- Choose existing job description
- Upload resume file (PDF/DOCX)
- Get instant evaluation results

**Bulk Resume Evaluation:**
- Select "Bulk Upload" tab
- Choose job description
- Upload multiple resume files
- Process all resumes in batch
- View consolidated results

#### 3. **View Results**

**Dashboard (`/dashboard`):**
- Summary statistics
- List of all evaluations
- Filter by job role, score, verdict
- Search functionality

**Detailed Results:**
- Comprehensive scoring breakdown
- Missing skills and qualifications
- Resume strengths analysis
- ATS compatibility score and tips
- Personalized improvement feedback

### API Usage

#### Evaluate Resume Programmatically
```python
import requests

# API endpoint
url = "http://localhost:5000/api/evaluate"

# Request payload
payload = {
    "resume_text": "Akash Awasthi\nSoftware Engineer\nSkills: Python, Machine Learning...",
    "jd_text": "Software Engineer\nMust-have: Python, AI/ML\nGood-to-have: Cloud..."
}

# Send request
response = requests.post(url, json=payload)
result = response.json()

# Access results
print(f"Final Score: {result['final_score']}")
print(f"Verdict: {result['verdict']}")
print(f"Missing Skills: {result['missing_elements']['missing_skills']}")
```

#### Find Similar Resumes
```python
# Find resumes similar to a job description
url = "http://localhost:5000/api/similar-resumes"
payload = {"jd_text": "Software Engineer position...", "n_results": 10}
response = requests.post(url, json=payload)
```

#### Check ATS Compatibility
```python
# Check resume ATS compatibility
url = "http://localhost:5000/api/ats-check"
payload = {"resume_text": "Resume content..."}
response = requests.post(url, json=payload)
```

## 📈 System Performance

### ✅ **Current Status**
- **All Core Features**: ✅ Working
- **Database Operations**: ✅ Stable
- **Web Interface**: ✅ Fully functional
- **API Endpoints**: ✅ All operational
- **Test Suite**: ✅ 5/5 tests passing


### Data Validation
- File format validation (PDF/DOCX only)
- Text extraction error handling
- Database constraint validation
- API input validation

## 📁 Project Structure

```
Resume-Relevance-automated-system/
├── app/
│   ├── __init__.py                 # Flask app initialization
│   ├── models.py                   # Database models
│   ├── routes.py                   # Web routes and API endpoints
│   ├── services/                   # Core business logic
│   │   ├── ats_compatibility_service.py
│   │   ├── embedding_service.py
│   │   ├── evaluation_pipeline.py
│   │   ├── evaluation_service.py
│   │   ├── jd_parser.py
│   │   ├── llm_service.py
│   │   └── resume_parser.py
│   ├── templates/                  # HTML templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── index.html
│   │   ├── results.html
│   │   └── upload.html
│   └── utils/                      # Utility functions
│       ├── file_processor.py
│       └── text_normalizer.py
├── uploads/                        # Uploaded files storage
├── chroma_db/                      # ChromaDB persistence
├── instance/                       # SQLite database
├── config.py                       # Application configuration
├── requirements.txt                # Python dependencies
├── run.py                         # Application entry point
├── migrate_postgresql.py          # PostgreSQL migrations
├── migrate_database.py            # SQLite migrations
├── test_system.py                 # Test suite
└── README.md                      # This documentation
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and test: `python test_system.py`
4. Commit changes: `git commit -m "Add new feature"`
5. Push to branch: `git push origin feature/new-feature`
6. Submit pull request

### Testing
```bash
# Run full test suite
python test_system.py

# Run specific tests
python -m pytest tests/test_evaluation.py
```

## 📄 License

This project is developed for **Innomatics Research Labs** as part of the automated resume evaluation system initiative.

##  Acknowledgments

- **Innomatics Research Labs** for the problem statement and requirements
- **OpenAI** for GPT model integration
- **HuggingFace** for transformer models and embeddings
- **ChromaDB** for vector storage capabilities
- **Flask** and **SQLAlchemy** for web framework and ORM

---


**System Status**: ✅ **Production Ready** - All core features operational with comprehensive fallback mechanisms.
