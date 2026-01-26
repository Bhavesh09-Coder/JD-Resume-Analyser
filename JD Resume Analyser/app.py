import os
import streamlit as st
from dotenv import load_dotenv
from pdf2image import convert_from_path
import pytesseract
import pdfplumber
from docx import Document
from langchain_groq import ChatGroq

# ---------------- LOAD ENV ----------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------------- TEXT EXTRACTION ----------------
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text()
        if text.strip():
            return text.strip()
    except Exception:
        pass

    # OCR fallback
    try:
        images = convert_from_path(pdf_path)
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
    except Exception:
        pass

    return text.strip()


def extract_text_from_docx(docx_path):
    text = ""
    doc = Document(docx_path)
    for para in doc.paragraphs:
        if para.text:
            text += para.text + "\n"
    return text.strip()


# ---------------- AI RESPONSE ----------------
def ai_response(user_query, resume_text=None):
    model = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.1-8b-instant",
        temperature=0
    )

    if resume_text:
        prompt = f"""
You are an expert Resume & Job Description evaluator.

USER QUERY:
{user_query}

RESUME CONTENT:
{resume_text}

INSTRUCTIONS:
- Answer the user's query using resume evidence
- If JD is mentioned, evaluate candidate fit
- Be objective, professional, and structured
- Do NOT assume missing information
"""
    else:
        prompt = f"""
You are a helpful AI assistant.
Answer the user's question clearly and concisely.

QUESTION:
{user_query}
"""

    response = model.invoke(prompt)
    return response.content.strip()


# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="AI Resume Assistant", layout="wide")

st.title("🤖 AI Resume Assistant")
st.write("Ask anything. Upload a resume only if analysis is needed.")

st.markdown("---")

col1, col2 = st.columns([2, 1])

# ---------------- QUERY BOX ----------------
with col1:
    user_query = st.text_area(
        "Ask your question",
        placeholder=(
            "Examples:\n"
            "- Is this candidate suitable for a Data Scientist role?\n"
            "- Analyze this resume according to below JD...\n"
            "- What is GenAI?\n"
        ),
        height=180
    )

# ---------------- RESUME UPLOAD ----------------
with col2:
    uploaded_file = st.file_uploader(
        "Upload Resume (Optional)",
        type=["pdf", "docx"]
    )

resume_text = None

if uploaded_file:
    st.success("Resume uploaded")

    ext = uploaded_file.name.split(".")[-1].lower()
    file_path = f"uploaded_resume.{ext}"

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if ext == "pdf":
        resume_text = extract_text_from_pdf(file_path)
    else:
        resume_text = extract_text_from_docx(file_path)

    if not resume_text.strip():
        st.error("Failed to extract resume text")
        resume_text = None


# ---------------- SUBMIT ----------------
if st.button("Ask"):
    if not user_query.strip():
        st.warning("Please enter a question")
    else:
        with st.spinner("Processing..."):
            answer = ai_response(user_query, resume_text)
            st.success("Response")
            st.write(answer)


# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center;'>Powered by Streamlit & ChatGroq</p>",
    unsafe_allow_html=True
)
