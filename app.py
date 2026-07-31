import streamlit as st
import pandas as pd
import tempfile
import os

from llm import parse_job_description
from resume_parser import evaluate_all_resumes

st.set_page_config(
    page_title="AI Resume Evaluator",
    page_icon="🤖",
    layout="wide"
)
st.markdown(
"""
<style>
[data-testid="stSidebar"] {
    width: 320px !important;
    min-width: 320px !important;
    max-width: 320px !important;
}

[data-testid="stSidebar"] > div:first-child {
    width: 320px !important;
}

/* Disable the drag-to-resize handle so the sidebar width stays fixed */
[data-testid="stSidebarResizeHandle"] {
    display: none !important;
    pointer-events: none !important;
}

/* Evaluate Candidates button */
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #4338CA 0%, #7C3AED 100%);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    font-weight: 600;
    font-size: 1rem;
    letter-spacing: 0.01em;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
    transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
}

[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(99, 102, 241, 0.5);
    opacity: 0.95;
    color: #ffffff;
}

[data-testid="stSidebar"] .stButton > button:active {
    transform: translateY(0px);
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
}

[data-testid="stSidebar"] .stButton > button:focus:not(:active) {
    color: #ffffff;
    border: none;
}

.hero {
    background: linear-gradient(135deg, #4338CA 0%, #7C3AED 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    color: #ffffff;
    margin-bottom: 1rem;
}

.hero h1 {
    margin: 0;
    font-size: 2.2rem;
}

.hero p {
    margin: 0.4rem 0 0 0;
    font-size: 1.05rem;
    opacity: 0.9;
}

.candidate-card {
    background: rgba(99, 102, 241, 0.06);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

.candidate-card h2 {
    margin: 0;
    font-size: 1.3rem;
}

.candidate-card .score {
    font-size: 1.6rem;
    font-weight: 700;
    color: #4338CA;
}

.badge {
    display: inline-block;
    background: #ECFDF5;
    color: #047857;
    border: 1px solid #A7F3D0;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    font-size: 0.85rem;
    margin: 0.2rem 0.3rem 0.2rem 0;
}

.badge.missing {
    background: #FEF2F2;
    color: #B91C1C;
    border-color: #FECACA;
}

.verdict {
    background: rgba(99, 102, 241, 0.06);
    border-left: 4px solid #6366F1;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-top: 0.5rem;
}

</style>
""",
unsafe_allow_html=True
)

st.markdown(
"""
<div class="hero">

<h1>
🤖 AI Resume Evaluator
</h1>

<p>
LLM-powered resume screening and intelligent candidate ranking system
</p>

</div>

""",
unsafe_allow_html=True
)

st.write("")

with st.sidebar:
    st.header("⚙️ Configuration")
    uploaded_files = st.file_uploader(
        "📄 Upload Resumes",
        type=[
            "pdf",
            "docx"
        ],
        accept_multiple_files=True
    )

    job_description = st.text_area(
        "💼 Job Description",
        height=300,
        placeholder=
        """
Example:
Software Engineer Intern
Required Skills:
- Java
- Python
- DSA
- SQL
- REST APIs
- Git

Experience:
0-2 years
        """
    )
  
    st.divider()

    evaluate_button = st.button(
        "📋 Evaluate Candidates",
        use_container_width=True
    )

def save_uploaded_files(files):
    temp_dir = tempfile.mkdtemp()

    for file in files:
        file_path = os.path.join(
            temp_dir,
            file.name
        )

        with open(
            file_path,
            "wb"
        ) as f:

            f.write(
                file.getbuffer()
            )

    return temp_dir

if evaluate_button:

    if not uploaded_files:
        st.warning(
            "⚠️ Please upload at least one resume."
        )
        st.stop()

    if not job_description.strip():
        st.warning(
            "⚠️ Please enter a job description."
        )
        st.stop()

    try:

        with st.spinner(
            "🤖 AI is analyzing resumes..."
        ):

            resume_folder = save_uploaded_files(
                uploaded_files
            )

            job = parse_job_description(
                job_description
            )

            results = evaluate_all_resumes(
                job,
                resume_folder

            )

        if not results:
            st.error(
                "No resumes could be processed."
            )
            st.stop()

        st.success(
            "✅ Evaluation completed successfully!"
        )

        st.divider()
        total_candidates = len(results)
        best_score = results[0]["score"]

        average_score = int(
            sum(
                candidate["score"]
                for candidate in results
            )
            /
            total_candidates
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="👥 Candidates",
                value=total_candidates
            )

        with col2:
            st.metric(
                label="🏆 Best Score",
                value=f"{best_score}%"
            )
          
        with col3:
            st.metric(
                label="📊 Average Score",
                value=f"{average_score}%"
            )
          
        st.divider()

        st.subheader(
            "🏆 Candidate Ranking"
        )

        for index, candidate in enumerate(results):
            details = candidate.get(
                "details",
                {}
            )

            name = candidate.get(
                "name",
                "Unknown Candidate"
            )

            score = candidate.get(
                "score",
                0
            )

            if index == 0:
                rank = "🥇"
            elif index == 1:
                rank = "🥈"
            elif index == 2:
                rank = "🥉"
            else:
                rank = "👤"

            st.markdown(
                f"""
                <div class="candidate-card">
                <h2>
                {rank} {name}
                </h2>
                <div class="score">
                {score}%
                </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.progress(
                score / 100
            )
            matching_skills = details.get(
                "matching_skills",
                []
            )

            if matching_skills:
                st.write(
                    "### ✅ Matching Skills"
                )

                skills_html = ""
                for skill in matching_skills:
                    skills_html += (
                        f"""
                        <span class="badge">
                        {skill}
                        </span>
                        """
                    )

                st.markdown(
                    skills_html,
                    unsafe_allow_html=True
                )

            missing_skills = details.get(
                "missing_important_skills",
                []
            )

            if missing_skills:
                st.write(
                    "### ❌ Missing Skills"
                )

                missing_html = ""
                for skill in missing_skills:
                    missing_html += (
                        f"""
                        <span class="badge missing">
                        {skill}
                        </span>
                        """
                    )
                st.markdown(
                    missing_html,
                    unsafe_allow_html=True
                )

            st.write(
                "### 📌 Candidate Analysis"
            )

            experience = details.get(
                "experience_requirement_met",
                False
            )

            education = details.get(
                "education_requirement_met",
                False
            )
          
            if experience:
                st.success(
                    "✅ Experience requirement satisfied"
                )
            else:
                st.warning(
                    "⚠️ Experience requirement not satisfied"
                )

            if education:
                st.success(
                    "✅ Education requirement satisfied"
                )
            else:
                st.warning(
                    "⚠️ Education requirement not satisfied"
                )


            verdict = details.get(
                "final_verdict",
                "No verdict available."
            )


            st.markdown(
                f"""
                <div class="verdict">
                <b>🤖 AI Verdict</b>
                <br><br>
                {verdict}
                </div>
                """,
                unsafe_allow_html=True
            )


            st.divider()
        csv_data = []


        for candidate in results:
            csv_data.append({
                "Candidate":
                candidate["name"],

                "Score":

                candidate["score"],

                "Verdict":
                candidate["details"].get(
                    "final_verdict",
                    ""
                )

            })



        df = pd.DataFrame(
            csv_data
        )

        csv = df.to_csv(
            index=False
        )

        st.download_button(
            label="📥 Download Evaluation Report",
            data=csv,
            file_name="resume_evaluation_report.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(
            "❌ Something went wrong while evaluating resumes."
        )
        st.exception(e)
