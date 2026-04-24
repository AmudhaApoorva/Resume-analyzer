import streamlit as st
import pdfplumber
from skills import SKILLS
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="AI Resume Analyzer Pro", page_icon="📄")

# -------------------------------
# CLEAN LIGHT UI STYLE
# -------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #ffffff;
    color: #000000;
}
h1, h2, h3 {
    color: #2c3e50;
}
.stButton>button {
    border-radius: 10px;
    padding: 8px 12px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# FUNCTIONS
# -------------------------------
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + " "
    return text.lower()

def extract_skills(text):
    found = []
    for skill in SKILLS:
        if all(word in text for word in skill.split()):
            found.append(skill)
    return list(set(found))

def match_score(found, required):
    matched = set(found).intersection(set(required))
    score = (len(matched)/len(required))*100 if required else 0
    return round(score,2), matched

def generate_pdf(role, score, matched, missing):
    file = "report.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("AI Resume Analysis Report", styles['Title']))
    content.append(Paragraph(f"Role: {role}", styles['Normal']))
    content.append(Paragraph(f"Score: {score}%", styles['Normal']))
    content.append(Paragraph(f"Matched: {', '.join(matched)}", styles['Normal']))
    content.append(Paragraph(f"Missing: {', '.join(missing)}", styles['Normal']))

    doc.build(content)
    return file

# -------------------------------
# JOB ROLES
# -------------------------------
roles = {
    "Data Scientist":["python","machine learning","pandas","numpy","sql"],
    "Web Developer":["html","css","javascript","react"],
    "Software Engineer":["java","c++","python","git"],
    "Data Analyst":["excel","sql","python","pandas"],
    "AI Engineer":["python","deep learning","tensorflow"],
    "DevOps Engineer":["docker","kubernetes","aws","linux"],
    "Cloud Engineer":["aws","azure","cloud","linux"],
    "Cyber Security Analyst":["networking","cyber security","linux"],
    "Full Stack Developer":["html","css","javascript","react","nodejs"]
}

# -------------------------------
# UI
# -------------------------------
st.title("📄 AI Resume Analyzer Pro")
st.write("🚀 Upload resume → get score → improve instantly")

file = st.file_uploader("Upload Resume", type=["pdf"])
role = st.selectbox("🎯 Select Job Role", list(roles.keys()))

# -------------------------------
# MAIN LOGIC
# -------------------------------
if file:
    text = extract_text_from_pdf(file)
    found = extract_skills(text)

    st.subheader("✅ Extracted Skills")
    st.success(", ".join(found) if found else "No skills found")

    required = roles[role]
    score, matched = match_score(found, required)
    missing = set(required) - set(found)

    # Dashboard
    c1,c2,c3 = st.columns(3)
    c1.metric("Score", f"{score}%")
    c2.metric("Skills Found", len(found))
    c3.metric("Missing", len(missing))

    # Progress
    st.progress(int(score))

    # Skills
    st.subheader("🎯 Matched Skills")
    st.write(list(matched) if matched else "None")

    st.subheader("💡 Missing Skills")
    st.write(list(missing))

    # Graph (professional)
    st.subheader("📊 Skill Gap Analysis")
    df = pd.DataFrame({
        "Category":["Matched","Missing"],
        "Count":[len(matched),len(missing)]
    })
    st.bar_chart(df.set_index("Category"))

    # AI Suggestions
    st.subheader("🤖 Suggestions")

    if score > 80:
        st.success("Excellent resume! 🎉")
    elif score > 50:
        st.info("Good, but improve missing skills")
    else:
        st.error("Needs improvement")

    for s in missing:
        st.write(f"👉 Learn {s} & add projects")

    # PDF
    pdf = generate_pdf(role, score, matched, missing)

    with open(pdf,"rb") as f:
        st.download_button("📄 Download PDF", f, file_name="report.pdf")