
import streamlit as st
import pdfplumber
import pandas as pd
import re

st.title("🦷 Medicare Dental & Hearing Comparison Tool")
st.write("Includes dental implants, preventive/restorative copays, and full benefit value.")

uploaded_files = st.file_uploader("Upload Summary of Benefits PDFs", type="pdf", accept_multiple_files=True)

keywords = {
    "Monthly premium": r"Monthly Plan Premium\s+\$\d+",
    "Medical deductible": r"Medical Deductible.*?(\$\d+|does not have a deductible)",
    "Max OOP": r"Maximum out-of-pocket.*?\$\d{1,3}(,\d{3})*",
    "Primary doctor": r"Primary care.*?\$\d+",
    "Specialist": r"Specialists?.*?\$\d+",
    "Hospital": r"(Inpatient Hospital|Hospital Coverage).+?\$\d+.+?day",
    "Dental Coverage (Total Value)": r"(Comprehensive|Annual|Maximum|Dental Allowance).*?(Benefit|Coverage)?.*?\$\d+(\.\d{2})?",
    "Dental Copay (Preventive)": r"(Preventive|Exam|Cleaning|X-rays).*?(copay)?.*?\$\d+(\.\d{2})?",
    "Dental Copay (Restorative)": r"(Filling|Crown|Root Canal|Endodontics|Restorative).*?\$\d+(\.\d{2})?",
    "Dental Implants": r"(Dental )?(Implants|Implant procedures).*?\$\d+(\.\d{2})?",
    "Hearing Aids": r"(Hearing Aid(s)?|Devices|Audiology).*?(coverage|copay|allowance)?.*?\$\d+(\.\d{2})?",
    "Vision": r"(Routine Eye Exam|Eyewear).+?\$\d+",
    "Transportation": r"(Transportation|non-emergency ride).*?\$?\d+.*?(one-way|trip|rides|miles)?",
    "MRI": r"MRI.*?\$\d+",
    "X-ray": r"X-ray.*?\$\d+",
    "Flex card": r"Flex (Benefit|Card).*?\$\d+.*?(month|quarter)?",
    "OTC Allowance": r"(Over[-\s]?the[-\s]?Counter (Card|Allowance|Benefit|Healthy Today)).*?\$\d+(\.\d{2})?.*?(month|quarter|year)?",
    "Living Needs Allowance": r"(Living Needs Allowance|Essential Needs|Utility|Home Support).*?\$\d+(\.\d{2})?",
    "Food/Utility Assistance": r"(food card|assistance|utility|groceries|support).*?\$\d+(\.\d{2})?",
    "Unspecified Allowance (Generic)": r"\$\d+(\.\d{2})?\s+(allowance|benefit|card|support)"
}

def extract_info(text):
    plan_data = {}
    for key, pattern in keywords.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        value = match.group(0) if match else "Not found"
        if "$" in value or "implant" in value.lower():
            plan_data[key] = value
    return plan_data

if uploaded_files:
    results = {}
    for file in uploaded_files:
        with pdfplumber.open(file) as pdf:
            full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            plan_info = extract_info(full_text)
            plan_name = file.name.replace(".pdf", "")
            results[plan_name] = plan_info

    if results:
        df = pd.DataFrame(results)
        st.subheader("🦷 Full Dental + Hearing + $ Benefit Comparison (with Implants)")
        st.dataframe(df)
        st.download_button("Download Full Table", df.to_csv().encode("utf-8"), "dental_with_implants_comparison.csv", "text/csv")
    else:
        st.info("No relevant data with dollar values or implant keywords detected.")
