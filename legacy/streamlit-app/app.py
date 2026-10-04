import os
import streamlit as st
from dotenv import load_dotenv
from google.genai.errors import APIError

from src.extractor import extract_resume
from src.heuristics import analyze_heuristics
from src.gemini_analyzer import analyze_with_gemini

load_dotenv()

st.set_page_config(page_title="CVAlchemy", page_icon="⚗️", layout="wide")
st.title("⚗️ CVAlchemy")
st.caption("Turn experience into evidence. Evidence into interviews.")
st.info(
    "CVAlchemy uses an explainable Role Evidence Score—not a proprietary ATS score. "
    "Its goal is to improve job alignment without keyword stuffing or fabricated experience."
)

with st.sidebar:
    st.header("About CVAlchemy")
    st.markdown(
        "**Evidence-first resume optimization**\n\n"
        "• JD requirement decomposition\n"
        "• Evidence-backed skill mapping\n"
        "• ClaimCheck / Truth Guard\n"
        "• Recruiter 10-second scan\n"
        "• Truth-preserving rewrites"
    )
    st.divider()
    st.header("Configuration")
    st.write(f"Gemini model: `{os.getenv('GEMINI_MODEL', 'gemini-3.8-flash')}`")
    st.write("The API key is read from `GEMINI_API_KEY` and is never displayed.")

resume_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])
job_description = st.text_area(
    "Paste the target job description",
    height=280,
    placeholder="Paste the full job description here...",
)

if st.button("Analyze role fit", type="primary", disabled=not (resume_file and job_description.strip())):
    try:
        with st.spinner("Extracting resume and building the evidence map..."):
            document = extract_resume(resume_file.getvalue(), resume_file.name)
            if not document.text.strip():
                st.error("No extractable text found. If this is a scanned PDF, OCR support will be needed.")
                st.stop()
            result = analyze_heuristics(
                document.text,
                job_description,
                document.page_count,
                document.fonts,
                document.font_sizes,
            )

        readiness_label = {
            "ready_to_apply": "🟢 Ready to apply",
            "improve_before_applying": "🟡 Improve before applying",
            "weak_fit": "🔴 Weak fit",
        }[result["readiness"]]

        st.subheader("Role Evidence Score")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Overall", f"{result['role_evidence_score']}/100")
        c2.metric("Requirement coverage", f"{result['requirement_coverage_score']}%")
        c3.metric("Evidence strength", f"{result['evidence_strength_score']}%")
        c4.metric("Impact quality", f"{result['impact_score']}%")
        c5.metric("ATS parsability", f"{result['formatting_score']}%")
        st.markdown(f"### {readiness_label}")

        tab1, tab2, tab3, tab4 = st.tabs([
            "Evidence Map", "Resume Health", "ClaimCheck", "AI Recruiter Review"
        ])

        with tab1:
            st.markdown("#### Requirement → evidence map")
            st.caption("This deterministic first pass shows where important JD terms are actually evidenced in the resume.")
            for item in result["evidence_map"]:
                icon = {"strong": "🟢", "moderate": "🟡", "weak": "🟠", "missing": "🔴"}[item["status"]]
                with st.expander(f"{icon} {item['requirement']} — {item['status'].title()}"):
                    if item["evidence"]:
                        for evidence in item["evidence"]:
                            st.markdown(f"> {evidence}")
                    else:
                        st.write("No direct evidence found in the resume.")

        with tab2:
            left, right = st.columns(2)
            with left:
                st.markdown("#### Matched role language")
                st.write(", ".join(result["matched_keywords"]) or "No strong matches detected")
                st.markdown("#### Missing / underrepresented")
                st.write(", ".join(result["missing_keywords"]) or "None in the top requirement set")
            with right:
                st.markdown("#### Document checks")
                st.json({
                    "file_type": document.file_type,
                    "pages": result["page_count"] if result["page_count"] else "renderer-dependent for DOCX",
                    "sections": result["sections"],
                    "top_fonts": result["fonts"],
                    "top_font_sizes": result["font_sizes"],
                    "formatting_flags": result["formatting_flags"],
                    "quantified_lines": result["stats"]["quantified_lines"],
                    "action_lines": result["stats"]["action_lines"],
                })

        with tab3:
            st.markdown("#### Deterministic Truth Guard")
            if result["subjective_claims"]:
                st.warning("These lines contain subjective/inflated wording. Prefer measurable evidence where possible.")
                for claim in result["subjective_claims"]:
                    st.markdown(f"- {claim}")
            else:
                st.success("No obvious subjective/inflated claims detected by the deterministic checker.")

            if result["weakly_supported_mentions"]:
                st.markdown("#### Skills/terms needing stronger evidence")
                st.write(", ".join(result["weakly_supported_mentions"]))

        with tab4:
            try:
                with st.spinner("Decomposing the JD and validating claims with Gemini..."):
                    review = analyze_with_gemini(document.text, job_description, result)

                st.markdown("#### What this role is really asking for")
                st.write(review.role_summary)

                st.markdown("#### JD decomposition")
                for req in review.requirements:
                    priority_icon = {"must_have": "🔴", "important": "🟡", "nice_to_have": "🟢"}[req.priority]
                    st.markdown(f"- {priority_icon} **{req.requirement}** · {req.category.replace('_', ' ').title()} · {req.priority.replace('_', ' ').title()}")

                st.markdown("#### AI evidence map")
                for item in review.evidence_map:
                    icon = {"strong": "🟢", "moderate": "🟡", "weak": "🟠", "missing": "🔴"}[item.status]
                    with st.expander(f"{icon} {item.requirement} — {item.status.title()}"):
                        st.write(item.explanation)
                        if item.evidence:
                            st.markdown("**Evidence found**")
                            for evidence in item.evidence:
                                st.markdown(f"> {evidence}")
                        st.markdown(f"**Recommendation:** {item.recommendation}")

                st.markdown("#### ClaimCheck™")
                supported = sum(c.status == "supported" for c in review.claim_checks)
                confirmation = sum(c.status == "needs_confirmation" for c in review.claim_checks)
                unsupported = sum(c.status == "unsupported" for c in review.claim_checks)
                subjective = sum(c.status == "subjective" for c in review.claim_checks)
                cc1, cc2, cc3, cc4 = st.columns(4)
                cc1.metric("Supported", supported)
                cc2.metric("Need confirmation", confirmation)
                cc3.metric("Unsupported", unsupported)
                cc4.metric("Subjective", subjective)
                for claim in review.claim_checks:
                    icon = {
                        "supported": "✅", "needs_confirmation": "⚠️", "unsupported": "❌", "subjective": "📝"
                    }[claim.status]
                    with st.expander(f"{icon} {claim.claim[:110]}"):
                        st.write(claim.explanation)
                        if claim.evidence:
                            st.markdown("**Evidence**")
                            for evidence in claim.evidence:
                                st.markdown(f"> {evidence}")
                        if claim.safer_rewrite:
                            st.markdown(f"**Safer wording:** {claim.safer_rewrite}")

                left, right = st.columns(2)
                with left:
                    st.markdown("#### Strengths")
                    for item in review.strengths:
                        st.markdown(f"- {item}")
                    st.markdown("#### Material gaps")
                    for item in review.material_gaps:
                        st.markdown(f"- {item}")
                with right:
                    st.markdown("#### Recruiter 10-second scan")
                    for item in review.recruiter_10_second_scan:
                        st.markdown(f"- {item}")
                    st.markdown("#### Interview focus")
                    for item in review.interview_focus:
                        st.markdown(f"- {item}")

                st.markdown("#### Truth-preserving rewrites")
                for suggestion in review.rewrite_suggestions:
                    with st.expander(suggestion.original[:120]):
                        st.markdown("**Original**")
                        st.write(suggestion.original)
                        st.markdown("**Suggested**")
                        st.write(suggestion.suggested)
                        st.markdown(f"**Why:** {suggestion.reason}")
                        if suggestion.requires_confirmation:
                            st.warning("This rewrite requires candidate confirmation before use.")

                ai_readiness = {
                    "ready_to_apply": "🟢 Ready to apply",
                    "improve_before_applying": "🟡 Improve before applying",
                    "weak_fit": "🔴 Weak fit",
                }[review.readiness]
                st.markdown(f"### {ai_readiness}")
                st.write(review.final_recommendation)
            except RuntimeError as exc:
                st.warning(f"Core evidence analysis completed. Gemini review skipped: {exc}")
            except APIError as exc:
                if exc.code == 503:
                    st.warning(
                        "Core evidence analysis completed, but Gemini is temporarily at capacity. "
                        "Your local scores and evidence map are still available. Please try Analyze role fit again in a few minutes."
                    )
                else:
                    st.error(f"Gemini request failed (HTTP {exc.code}): {exc.message}")
    except Exception as exc:
        st.exception(exc)
