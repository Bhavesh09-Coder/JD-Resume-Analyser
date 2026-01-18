import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import pdfplumber
from docx import Document
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Fetch Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        # Try direct text extraction
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

        if text.strip():
            return text.strip()
    except Exception as e:
        print(f"Direct text extraction failed: {e}")

    # Fallback to OCR
    print("Falling back to OCR for image-based PDF.")
    try:
        images = convert_from_path(pdf_path)
        for image in images:
            page_text = pytesseract.image_to_string(image)
            text += page_text + "\n"
    except Exception as e:
        print(f"OCR failed: {e}")

    return text.strip()


def extract_text_from_docx(docx_path):
    text = ""
    try:
        doc = Document(docx_path)
        for para in doc.paragraphs:
            if para.text:
                text += para.text + "\n"
    except Exception as e:
        print(f"DOCX extraction failed: {e}")

    return text.strip()


# Function to analyze resume using ChatGroq
def analyze_resume(resume_text, job_description):
    if not resume_text or not job_description:
        return "Both resume text and job description are required for analysis."

    # Initialize ChatGroq model
    model = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.1-8b-instant",
        temperature=0
    )


    # ---------------- SYSTEM PROMPT ----------------
    base_prompt = f"""
You are an AI system designed to perform precise Job Description (JD) and Resume alignment analysis.

PURPOSE:
Evaluate how well a candidate’s resume aligns with a given Job Description using current industry expectations, role responsibilities, and technical standards.

ANALYSIS GUIDELINES:
- Base the evaluation strictly on evidence present in the resume
- Compare required skills, experience level, tools, technologies, and role responsibilities mentioned in the JD
- Consider both explicit matches (clearly stated skills) and implicit matches (demonstrated experience or responsibilities)
- Maintain an objective, neutral, and assessment-focused tone
- Provide clear, detailed, and structured insights suitable for professional review

ANALYSIS SCOPE:
- Skill alignment (core, secondary, and supporting skills)
- Experience relevance (years, domain exposure, role similarity)
- Tooling and technology match
- Functional responsibilities alignment
- Seniority and role-fit consistency

OUTPUT FORMAT (STRICTLY FOLLOW THIS STRUCTURE):

1. JD MATCH SCORE:
- Provide a percentage score between 0 and 100
- The score should reflect overall alignment considering skills, experience, tools, and role responsibilities & brief explanation

2. MATCHED SKILLS & REQUIREMENTS (STRUCTURED):

Present this section in a clean, structured TABLE format.

Extract and present only the candidate’s resume evidence that directly aligns with the JD, structured under Skills, Experience, Roles, Projects, and Education, clearly mapping each item to the corresponding JD requirement.

SUMMARY (MAX 2 LINES PER CATEGORY):
- Provide a short 1–2 line summary for each category highlighting alignment strength
- Do NOT repeat table content verbatim
- Focus on relevance and depth of match


3. PARTIAL MATCHES:
- Identify skills or requirements that are partially met
- Briefly explain what is present and what is lacking

4. MISSING SKILLS / GAPS:
- List required or preferred JD elements that are absent or insufficiently demonstrated in the resume

5. STRENGTHS:
- Highlight the most relevant strengths of the candidate in relation to the JD
- Focus on areas that significantly contribute to role suitability

6. WEAKNESSES / LIMITATIONS:
- Identify areas where the resume shows limited alignment with the JD
- Focus only on JD-related gaps or inconsistencies

7. ROLE FIT ASSESSMENT:
- Assess how well the candidate fits the role overall (e.g., strong fit, moderate fit, limited fit)
- Base this assessment on evidence from the resume and JD alignment

8. SCORE EXPLANATION:
- Provide a concise but clear explanation of how the score was derived
- Mention key factors that positively influenced the score
- Mention key factors that reduced the score

---------------------------------------
JOB DESCRIPTION:
{job_description}

---------------------------------------
RESUME:
{resume_text}

Ensure the output is well-structured, clearly labeled, and written in professional language &
Return the analysis in clean, professional way.
"""

    # Invoke Groq LLM
    response = model.invoke(base_prompt)

    return response.content.strip()


# ---------------- Streamlit App ----------------

st.set_page_config(page_title="Resume Analyzer", layout="wide")

st.title("AI JD Resume Analyzer")
st.write("Analyze your resume and match it with job descriptions using ChatGroq AI.")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader(
    "Upload your resume (PDF or DOCX)",
    type=["pdf", "docx"]
)

with col2:
    job_description = st.text_area(
        "Enter Job Description:",
        placeholder="Paste the job description here..."
    )

if uploaded_file is not None:
    st.success("Resume uploaded successfully!")
else:
    st.warning("Please upload a resume in PDF/Docx format.")

st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)

if uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    file_path = f"uploaded_resume.{file_extension}"

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if file_extension == "pdf":
        resume_text = extract_text_from_pdf(file_path)
    elif file_extension == "docx":
        resume_text = extract_text_from_docx(file_path)
    else:
        resume_text = ""

    # SAFETY CHECK 
    if not resume_text.strip():
        st.error("Could not extract text from the resume.")
        st.stop()

    if st.button("Analyze Resume"):
        with st.spinner("Analyzing resume..."):
            try:
                analysis = analyze_resume(resume_text, job_description)
                st.success("Analysis complete!")
                st.write(analysis)
            except Exception as e:
                st.error(f"Analysis failed: {e}")


# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center;'>Powered by <b>Streamlit</b> and <b>ChatGroq AI</b></p>",
    unsafe_allow_html=True
)
