import streamlit as st
import pdfplumber
import io
from skills import SKILLS
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="ResumeAI Pro", page_icon="📄")

# -------------------------------
# UI STYLE
# -------------------------------
st.markdown("""
<style>
.stApp {background-color:#ffffff; color:#000000;}
h1 {text-align:center;}
.stButton>button {border-radius:10px;}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# FUNCTIONS
# -------------------------------
def extract_text_from_pdf(file):
    text = ""
    try:
        pdf_bytes = file.read()
        pdf_stream = io.BytesIO(pdf_bytes)

        with pdfplumber.open(pdf_stream) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content + " "
    except:
        return ""
    
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
    content.append(Paragraph(f"Matched Skills: {', '.join(matched)}", styles['Normal']))
    content.append(Paragraph(f"Missing Skills: {', '.join(missing)}", styles['Normal']))

    doc.build(content)
    return file

# -------------------------------
# ROLES (MULTI-DOMAIN)
# -------------------------------
roles = {

    # 💻 TECH
    "Software Engineer":["python","java","c++","git"],
    "Data Scientist":["python","machine learning","pandas","numpy","sql"],
    "AI Engineer":["python","deep learning","tensorflow"],
    "Cyber Security Analyst":["networking","cyber security","linux"],

    # 🏭 CORE
    "Mechanical Engineer":["cad","solidworks","manufacturing"],
    "Civil Engineer":["autocad","construction","surveying"],
    "Electrical Engineer":["circuits","electronics","control systems"],

    # 💼 MANAGEMENT
    "Business Analyst":["excel","sql","communication"],
    "Marketing Manager":["seo","marketing","analytics"],
    "HR Manager":["recruitment","communication","management"],
    "Finance Analyst":["finance","excel","accounting"],

    # 🎨 CREATIVE
    "UI/UX Designer":["figma","design","prototyping"],
    "Graphic Designer":["photoshop","illustrator","design"],
    "Content Writer":["writing","seo","communication"]
}

# -------------------------------
# HEADER
# -------------------------------
st.markdown("""
# 📄 ResumeAI Pro  
### 🚀 Multi-Domain Resume Analyzer  
---
""")

# -------------------------------
# INPUT
# -------------------------------
file = st.file_uploader("📤 Upload Resume (PDF)", type=["pdf"])
role = st.selectbox("🎯 Select Job Role", list(roles.keys()))

# -------------------------------
# MAIN
# -------------------------------
if file:

    st.success("✅ File uploaded successfully")

    with st.spinner("🔄 Analyzing resume..."):
        text = extract_text_from_pdf(file)

    if not text.strip():
        st.error("❌ Could not read PDF. Try another file.")
    else:
        found = extract_skills(text)

        st.subheader("✅ Extracted Skills")
        st.success(", ".join(found) if found else "No skills found")

        required = roles[role]
        score, matched = match_score(found, required)
        missing = set(required) - set(found)

        # Dashboard
        c1, c2, c3 = st.columns(3)
        c1.metric("📊 Score", f"{score}%")
        c2.metric("✅ Skills Found", len(found))
        c3.metric("❌ Missing", len(missing))

        st.progress(int(score))

        # Skills
        st.subheader("🎯 Matched Skills")
        st.write(list(matched) if matched else "None")

        st.subheader("💡 Missing Skills")
        st.write(list(missing))

        # Graph
        st.subheader("📊 Skill Gap Analysis")
        df = pd.DataFrame({
            "Category":["Matched","Missing"],
            "Count":[len(matched),len(missing)]
        })
        st.bar_chart(df.set_index("Category"))

        # Suggestions
        st.subheader("🤖 Suggestions")

        if score > 80:
            st.success("Excellent! You are job-ready 🎉")
        elif score > 50:
            st.info("Good, improve missing skills")
        else:
            st.error("Needs improvement for this role")

        for s in missing:
            st.write(f"👉 Learn {s} & add projects")

        # PDF
        pdf = generate_pdf(role, score, matched, missing)

        with open(pdf,"rb") as f:
            st.download_button("📄 Download Report", f, file_name="resume_report.pdf")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("""
---
### 👨‍💻 Developed by AMUDHA APOORVA  
🚀 AI Resume Analyzer Project  
""")
