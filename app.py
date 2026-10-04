import os
import streamlit as st
from dotenv import load_dotenv

from src.extractor import extract_pdf
from src.heuristics import analyze_heuristics
from src.gemini_analyzer import analyze_with_gemini

load_dotenv()

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")
st.title("📄 TechCV — AI Resume Coach")
st.caption("Transparent ATS-style heuristics + Google Gemini recruiter feedback")
st.info("The ATS score in this project is a custom heuristic for learning and comparison. It does not reproduce any commercial ATS or employer screening system.")

with st.sidebar:
    st.header("Configuration")
    st.write(f"Gemini model: `{os.getenv('GEMINI_MODEL', 'gemini-3.8-flash')}`")
    st.write("API key is read from `GEMINI_API_KEY` and is never shown in the UI.")

resume_file = st.file_uploader("Upload resume (PDF)", type=["pdf"])
job_description = st.text_area("Paste the target job description", height=260, placeholder="Paste the full JD here...")

if st.button("Analyze resume", type="primary", disabled=not (resume_file and job_description.strip())):
    try:
        with st.spinner("Extracting resume and computing transparent heuristics..."):
            document = extract_pdf(resume_file.getvalue())
            if not document.text.strip():
                st.error("No extractable text found. This PDF may be scanned/image-only. OCR support is a good next extension.")
                st.stop()
            result = analyze_heuristics(
                document.text,
                job_description,
                document.page_count,
                document.fonts,
                document.font_sizes,
            )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ATS-style score", f"{result['ats_score']}/100")
        c2.metric("Keyword match", f"{result['keyword_score']}%")
        c3.metric("Section completeness", f"{result['section_score']}%")
        c4.metric("Impact evidence", f"{result['impact_score']}%")

        left, right = st.columns(2)
        with left:
            st.subheader("Matched JD keywords")
            st.write(", ".join(result["matched_keywords"]) or "No strong matches detected")
            st.subheader("Missing / underrepresented keywords")
            st.write(", ".join(result["missing_keywords"]) or "None in the top keyword set")
        with right:
            st.subheader("Document checks")
            st.json({
                "pages": result["page_count"],
                "sections": result["sections"],
                "top_fonts": result["fonts"],
                "top_font_sizes": result["font_sizes"],
                "formatting_flags": result["formatting_flags"],
            })

        st.subheader("Gemini recruiter review")
        try:
            with st.spinner("Generating grounded recruiter feedback with Gemini..."):
                review = analyze_with_gemini(document.text, job_description, result)
            st.success(review.fit_summary)
            r1, r2 = st.columns(2)
            with r1:
                st.markdown("#### Strengths")
                for item in review.strengths:
                    st.markdown(f"- {item}")
                st.markdown("#### Gaps")
                for item in review.gaps:
                    st.markdown(f"- {item}")
            with r2:
                st.markdown("#### Rewrite suggestions")
                for item in review.rewrite_suggestions:
                    st.markdown(f"- {item}")
                st.markdown("#### Interview focus")
                for item in review.interview_focus:
                    st.markdown(f"- {item}")
            st.markdown("#### Recommendation")
            st.write(review.final_recommendation)
        except RuntimeError as exc:
            st.warning(f"Heuristic analysis completed. Gemini review skipped: {exc}")
    except Exception as exc:
        st.exception(exc)
