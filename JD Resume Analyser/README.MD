# JD Resume Analyzer

## Overview

This project demonstrates an end-to-end AI-driven workflow for **candidate role-fit analysis** using a resume and a job description.

The system follows a structured and explainable pipeline:

**Job Description → Resume Retrieval → Candidate Fit Analysis**

The focus is on:
- Clean, structured JSON outputs
- Explainable candidate–JD matching
- Model-independent integration
- Simple and clear UI-driven workflow

---

## Workflow Summary

1. User provides a **Job Description (JD)**
2. User uploads a **Resume (PDF)**
3. User clicks **Analyze**
4. System processes the resume and JD
5. System outputs:
   - Structured candidate profile (JSON)
   - JD match score
   - Strengths
   - Gaps
   - Detailed role-fit explanation

All results are displayed directly in the UI in a clean and explainable format.

---

## System Capabilities

### 1. Resume Processing
- Extracts raw text from uploaded PDF resumes
- Handles unstructured resume formats

### 2. Structured Candidate Profile Extraction
- Converts resume text into a structured JSON profile
- Extracted fields include:
  - Skills
  - Total experience
  - Roles
  - Projects
  - Education

### 3. JD Match Analysis
- Evaluates alignment between candidate profile and job description
- Produces:
  - Overall match score (0–100)
  - Candidate fit level (High / Medium / Low)
  - Strengths aligned with JD
  - Gaps against JD requirements
  - Explainable role-fit reasoning

### 4. Explainable Outputs
- All outputs are structured JSON
- Designed for easy UI rendering and downstream automation
- No resume improvement suggestions are provided

---

## Project Structure

