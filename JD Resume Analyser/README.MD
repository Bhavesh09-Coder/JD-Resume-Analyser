# AI JD–Resume Analyzer

An AI-powered web application that analyzes a candidate’s resume against a given Job Description (JD) and produces a **structured, explainable, and recruiter-ready alignment report**.  
The system supports PDF and DOCX resumes, handles scanned resumes via OCR, and uses **Groq’s LLaMA 3.1 model** through LangChain for fast and deterministic analysis.

---

## 🚀 Features

- Upload resumes in **PDF or DOCX format**
- Automatic text extraction from:
  - Text-based PDFs
  - Scanned/image-based PDFs (OCR fallback)
  - DOCX files
- Manual Job Description (JD) input
- AI-driven JD–Resume alignment analysis
- Deterministic scoring and professional output
- Clear breakdown of:
  - Match score
  - Matched skills
  - Partial matches
  - Missing skills / gaps
  - Strengths and weaknesses
  - Role fit assessment
- Interactive and easy-to-use **Streamlit UI**
- Secure API key management using `.env`

---

## 🧠 How It Works (High-Level Flow)

1. User uploads a resume (PDF or DOCX)
2. User enters the Job Description
3. Resume text is extracted:
   - Direct parsing for text-based files
   - OCR for scanned PDFs
4. Resume text and JD are sent to Groq LLM
5. AI performs structured JD–Resume analysis
6. Results are displayed in the UI

---

## 🛠️ Technology Stack

### Frontend / UI
- **Streamlit**

### Backend / Core Logic
- **Python**

### Document Processing
- `pdfplumber` – PDF text extraction
- `pdf2image` – Convert PDF pages to images
- `pytesseract` – OCR for scanned PDFs
- `python-docx` – DOCX parsing

### AI / LLM
- **Groq**
- **LLaMA 3.1 (8B Instant)**
- **LangChain (ChatGroq)**

### Configuration
- `python-dotenv` – Environment variable management

---

## 📂 Project Structure

```text
.
├── app.py                # Main Streamlit application
├── requirements.txt      # Project dependencies
├── .env                  # Environment variables (not committed)
├── README.md             # Project documentation
