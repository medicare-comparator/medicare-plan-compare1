
import streamlit as st
import pdfplumber
import pandas as pd
import re

st.title("📋 Medicare Plan Comparison Tool")
st.write("Upload Summary of Benefits PDFs for clean, card-specific comparison.")

uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

keywords = {
    "Monthly premium": r"Monthly Plan Premium\s+\$\d+",
    "Medical deductible": r"Medical Deductible.*?(\$\d+|does not have a deductible)",
    "Max OOP": r"Maximum out-of-pocket.*?\$\d{1,3}(,\d{3})*",
    "Primary doctor": r"Primary care.*?\$\d+",
    "Specialist": r"Specialists?.*?\$\d+",
    "Hospital": r"(Inpatient Hospital|Hospital Coverage).+?\$\d+.+?day",
    "Dental": r"(Dental Allowance|Preventive and Comprehensive Dental).+?\$\d+",
    "Hearing": r"Hearing Aids?.+?\$\d+",
    "Vision": r"(Routine Eye Exam|Eyewear).+?\$\d+",
    "Transportation": r"(Transportation|non-emergency ride).*?\$?\d+.*?(one-way|trip|rides|miles)?",
    "MRI": r"MRI.*?\$\d+",
    "X-ray": r"X-ray.*?\$\d+",
    "Flex card": r"Flex (Benefit|Card).*?\$\d+.*?(month|quarter)?",
    "OTC": r"(OTC (Card|Allowance|Benefit|Healthy Today).*?\$\d+(\.\d{2})?.*?(month|quarter|year)?)",
    "Giveback": r"Part B.*?\$\d+\.\d{2}"
}

def extract_info(text):
    plan_data = {}
    for key, pattern in keywords.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        plan_data[key] = match.group(0) if match else "Not found"
    return plan_data

if uploaded_files:
    results = {}
    for file in uploaded_files:
        with pdfplumber.open(file) as pdf:
            full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            plan_info = extract_info(full_text)
            plan_name = file.name.replace(".pdf", "")
            results[plan_name] = plan_info

    df = pd.DataFrame(results)
    st.subheader("📊 Medicare Plan Comparison by Feature")
    st.dataframe(df)
    st.download_button("Download as CSV", df.to_csv().encode("utf-8"), "fixed_comparison.csv", "text/csv")
