import streamlit as st
import pdfplumber
import google.generativeai as genai

# --- Setup ---
st.set_page_config(layout="wide")
genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# --- Session State Initialization ---
for key in ["user_type", "resume_text", "submit_clicked", "career_response"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "submit_clicked" else False

st.title("🎯 Career Path AI")
st.subheader("Upload your resume or enter your information manually to get personalized career insights (Do both for the most precise results)")

# --- User Type Selection ---
user_type = st.radio("Who are you?", ["Current Job Seeker", "High School Student"], key="user_type")

# --- Upload Resume Option ---
st.markdown("### Upload Resume")
uploaded_pdf = st.file_uploader("Upload your resume (PDF)", type="pdf")

if uploaded_pdf is not None:
    try:
        with pdfplumber.open(uploaded_pdf) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            st.session_state.resume_text = text
            st.success("✅ Resume text extracted.")
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        st.session_state.resume_text = ""

# --- Step 2: Manual Input Based on User Type ---
st.html("<br>")
st.html("<hr>")
st.html("<br>")
st.markdown("### Manually Information Input")

inputs = {}

if user_type == "Current Job Seeker":
    # Mandatory
    inputs["Highest Education Level"] = st.text_input("What is your highest level of education?")
    inputs["Education Place"] = st.text_input("Where did you study?")
    inputs["Major"] = st.text_input("What did you major in?")
    inputs["Previous Jobs"] = st.text_area("List your previous jobs/experiences")

    # Optional
    with st.expander("Optional Info"):
        inputs["Age"] = st.text_input("What is your age?")
        inputs["Test Scores"] = st.text_input("Relevant test scores (LSAT, MCAT, etc.)")
        inputs["Technical Skills"] = st.text_input("List your technical skills")
        inputs["Interests"] = st.text_input("What are your personal interests?")
        inputs["Values"] = st.text_input("What are your core values?")
        inputs["Legal Status"] = st.text_input("What is your work authorization status?")
        inputs["Willing to Relocate"] = st.selectbox("Would you relocate for work?", ["Yes", "No"])

elif user_type == "High School Student":
    # Mandatory
    inputs["Age"] = st.text_input("What is your age?")
    inputs["Planned Education Level"] = st.text_input("What is the highest level of education you plan to achieve?")
    inputs["Planned Study Location"] = st.text_input("Where do you plan to study?")
    inputs["Planned Major"] = st.text_input("What do you want to major in?")

    # Optional
    with st.expander("Optional Info"):
        inputs["Extracurriculars"] = st.text_input("List your extracurriculars")
        inputs["Volunteering"] = st.text_input("List your volunteering experiences")
        inputs["Awards"] = st.text_input("List any awards or recognitions")

# --- Step 3: Generate Career Paths ---
def build_prompt(inputs, resume_text, user_type):
    prompt = f"""
    You are a Career and Salary Forecasting AI.

    Analyze the following background and generate personalized career advice. If resume content is available, prioritize it.

    --- USER TYPE: {user_type.upper()} ---

    Resume Content:
    {resume_text if resume_text else '[No resume provided]'}

    Manual Inputs:
    """ + "\n".join([f"- {k}: {v}" for k, v in inputs.items() if v]) + """

    Generate the following:
    1. 3–5 personalized career paths relevant to the user's profile.
    2. Estimated salary ranges for each career (entry, mid, senior level).
    
    Use bullet points and clear formatting.
    """
    return prompt

def generate_results():
    st.session_state.submit_clicked = True
    prompt = build_prompt(inputs, st.session_state.resume_text, user_type)

    with st.spinner("🔍 Analyzing your background..."):
        try:
            response = model.generate_content(prompt)
            if response and response.candidates:
                st.session_state.career_response = response.candidates[0].content.parts[0].text
            else:
                st.error("❌ No response generated. Try again.")
        except Exception as e:
            st.error(f"Error generating response: {e}")

st.markdown("---")
st.button("Generate Career Insight", on_click=generate_results)

# --- Output Display ---
if st.session_state.submit_clicked:
    st.markdown("## 🧭 Your Personalized Career Report")
    if st.session_state.career_response:
        st.markdown(st.session_state.career_response)
    else:
        st.warning("No career response generated. Try refining your input or uploading a resume.")
