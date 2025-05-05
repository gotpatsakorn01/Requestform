import streamlit as st
import pandas as pd
import os
import base64


st.set_page_config(
    page_title=" Form For IT",
    page_icon="📄",
    layout="centered"
)

# === CONFIG ===
EXCEL_FILE = "requests_full.xlsx"
SIGNATURE_FOLDER = "signatures"
LOGO_PATH = "KTNC-Logo.jpg"

# === CSS: ปรับขนาดฟอนต์ และซ่อน selectbox, checkbox เวลา print ===
st.markdown("""
    <style>
        * { font-size: 16px; }
        .print-field { font-size: 18px; margin-bottom: 8px; }
        .signature-label {
            text-align: center;
            border-top: 1px solid #000;
            width: 220px;
            margin: 5px auto 20px;
            padding-top: 3px;
        }
        @media print {
            .stSelectbox, .stCheckbox {
                display: none !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# === LOGO CENTER ===
def show_centered_logo(image_path, width=140):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{encoded}' width='{width}'></div>", unsafe_allow_html=True)

# === DISPLAY FIELD ===
def render_field(label, value, icon=""):
    st.markdown(f"<p class='print-field'><b>{icon} {label}:</b> {value}</p>", unsafe_allow_html=True)

# === DISPLAY SIGNATURE ===
def render_signature(name, role, path):
    if isinstance(path, str) and os.path.exists(path):
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <div style="text-align: center;">
                <img src="data:image/png;base64,{encoded}" width="220"/><br>
                <div class="signature-label">{role}: {name}</div>
            </div>
        """, unsafe_allow_html=True)

# === START ===
show_centered_logo(LOGO_PATH)
st.markdown("<h2 style='text-align:center;'> Request Hardware/Software/Upgrade Form</h2>", unsafe_allow_html=True)

# === LOAD DATA ===
if not os.path.exists(EXCEL_FILE):
    st.error("❌ ไม่พบไฟล์ Excel")
    st.stop()

df = pd.read_excel(EXCEL_FILE)
approved_df = df[df["Status"] != "Pending"]

if approved_df.empty:
    st.info("ไม่มีรายการที่อนุมัติหรือถูกปฏิเสธ")
    st.stop()

# === SELECT MODE (Normal View vs Print View) ===
print_mode = st.checkbox("🖨️ เปิดโหมดสำหรับพิมพ์หรือเซฟ PDF")

# === REQUEST NUMBER ===
if print_mode:
    request_no = st.selectbox("📄 เลือก Request ที่อนุมัติแล้ว", approved_df["Request Number"])
    st.markdown(f"<p class='print-field'><b>📄 Request Number:</b> {request_no}</p>", unsafe_allow_html=True)
else:
    request_no = st.selectbox("📄 เลือก Request ที่อนุมัติแล้ว", approved_df["Request Number"])

data = approved_df[approved_df["Request Number"] == request_no].iloc[0]

# === DISPLAY FIELDS ===
render_field("Date", str(data["Date"]), "🕒")
render_field("Type", data["Request Type"], "📦")
render_field("Item", f"{data['Item']} x {data['Quantity']}", "🧾")
render_field("Hotel", f"{data['Hotel']} / {data['Department']}", "🏨")
render_field("Location", data["Location"], "📍")
render_field("Detail", data.get("Detail", ""), "📝")

# === SIGNATURE BLOCK (Request Name, HOD, Hotel Manager)
with st.container():
    cols1 = st.columns(3)
    with cols1[0]:
        render_signature(data["Request Name"], "Request Name", data["Request Signature"])
    with cols1[1]:
        render_signature(data["HOD"], "HOD", data["HOD Signature"])
    with cols1[2]:
        render_signature(data["Hotel Manager"], "Hotel Manager", data["Hotel Manager Signature"])

# === SIGNATURE BLOCK (IT Receiver, IT Manager) + STATUS (รวมอยู่ในบล็อกเดียวกัน)
st.markdown("""
    <div style="page-break-inside: avoid;">
""", unsafe_allow_html=True)

with st.container():
    cols2 = st.columns(2)
    with cols2[0]:
        render_signature(data["IT Receiver"], "IT Receiver", data["IT Receiver Signature"])
    with cols2[1]:
        render_signature(data["IT Manager"], "IT Manager", data["IT Manager Signature"])

render_field("Status", data["Status"], "📌")

st.markdown("</div>", unsafe_allow_html=True)

