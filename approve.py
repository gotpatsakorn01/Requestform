import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import requests


st.set_page_config(
    page_title=" Approve For IT",
    page_icon="✅",
    layout="centered"
)


# === CONFIG ===
EXCEL_FILE = "requests_full.xlsx"
SHEET_NAME = "Requests"
SIGNATURE_FOLDER = "signatures"
BOT_TOKEN = "7220616384:AAH8j1spxA-UUmihi0ivVLRBuKzZYTtmJuc"
CHAT_ID = "-1002320440146"

AUTHORIZED_USERS = [
    "piyawat", "jukrit", "siwat", "pongsith", "ratchanon",
    "nonthawat", "patsakorn", "wannuwat", "paratthakorn"
]
PASSWORD = "0000"

# === LOGIN ===
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown(
        "<h2 style='text-align:center; color:#004d99;'>💻 Welcome to Approve Form Request<br>Hardware / Software / Upgrade</h2><br><br>",
        unsafe_allow_html=True
    )
    with st.sidebar:
        st.header("🔐 IT Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if username in AUTHORIZED_USERS and password == PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    st.stop()

# === LOGOUT ===
with st.sidebar:
    st.success(f"✅ Logged in as: {st.session_state.username}")
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

# === MAIN ===
st.title("✅ Approve Request")

os.makedirs(SIGNATURE_FOLDER, exist_ok=True)

if not os.path.exists(EXCEL_FILE):
    st.error("❌ ไม่พบไฟล์ Excel กรุณาส่งคำขอก่อน")
    st.stop()

df = pd.read_excel(EXCEL_FILE)
pending_requests = df[df["Status"] == "Pending"]

if pending_requests.empty:
    st.info("🎉 ไม่มีรายการที่รออนุมัติ")
    st.stop()

request_no = st.selectbox("📄 เลือก Request Number ที่ต้องการอนุมัติ", pending_requests["Request Number"].tolist())
request_data = df[df["Request Number"] == request_no].iloc[0]

# แสดงข้อมูลคำขอ
st.markdown(f"**🕒 Date:** `{request_data['Date']}`")
st.markdown(f"**📦 Type:** `{request_data['Request Type']}`")
st.markdown(f"**🧾 Item:** `{request_data['Item']}` x `{request_data['Quantity']}`")
st.markdown(f"**🏨 Hotel:** `{request_data['Hotel']}` / `{request_data['Department']}`")
st.markdown(f"**📍 Location:** `{request_data['Location']}`")
st.markdown(f"**📝 Detail:** `{request_data.get('Detail', '')}`")

# ลายเซ็น Request Name
st.markdown(f"**👤 Request Name:** `{request_data['Request Name']}`")
sig_req_path = str(request_data["Request Signature"]).strip()
if sig_req_path and os.path.exists(sig_req_path):
    st.image(sig_req_path, caption="🖋️ ลายเซ็น Request Name", width=200)

# ลายเซ็น HOD
st.markdown(f"**👤 HOD:** `{request_data['HOD']}`")
sig_hod_path = str(request_data["HOD Signature"]).strip()
if sig_hod_path and os.path.exists(sig_hod_path):
    st.image(sig_hod_path, caption="🖋️ ลายเซ็น HOD", width=200)

# เมนู Hotel Manager
hotel_manager = st.selectbox("👤 Hotel Manager", [
    "Suda Sedbuppha", "Puran Guatum (for)", "Nakanyarom Pattanapornpiriya (for)",
    "Wanta Supauan (for)", "Jeerapha Chuenchom (for)",
    "Piyaporn Kluamephon (for)", "Nipa Taepan (for)"
])
st.write("✍️ ลายเซ็น Hotel Manager")
canvas_htm = st_canvas(height=150, stroke_width=1, key="htm_sig")

# IT Receiver
it_receiver = st.selectbox("👤 IT Receiver", [
    "Siwat Kalasang", "Pongsith Raksanit", "Ratchanon Chada",
    "Nonthawat Saisawan", "IT Trainee"
])
st.write("✍️ ลายเซ็น IT Receiver")
canvas_it = st_canvas(height=150, stroke_width=1, key="it_sig")

# IT Manager
it_manager = st.selectbox("👤 IT Manager", ["Piyawat Nitiphatwatawong", "Jukrit Aungsakul"])
st.write("✍️ ลายเซ็น IT Manager")
canvas_itm = st_canvas(height=150, stroke_width=1, key="itm_sig")

status = st.radio("📌 เลือกสถานะ", ["Approved", "Rejected"])

# ฟังก์ชันบันทึกลายเซ็น
def save_signature(canvas, filename):
    if canvas.image_data is not None:
        img = Image.fromarray((canvas.image_data).astype(np.uint8))
        path = os.path.join(SIGNATURE_FOLDER, filename)
        img.save(path)
        return path
    return ""

# เมื่อกด Submit
if st.button("✅ ยืนยันการอนุมัติ"):
    sig_htm_path = save_signature(canvas_htm, f"{request_no}-htm.png")
    sig_it_path = save_signature(canvas_it, f"{request_no}-it.png")
    sig_itm_path = save_signature(canvas_itm, f"{request_no}-itm.png")

    idx = df[df["Request Number"] == request_no].index[0]
    df.at[idx, "Hotel Manager"] = hotel_manager
    df.at[idx, "Hotel Manager Signature"] = sig_htm_path
    df.at[idx, "IT Receiver"] = it_receiver
    df.at[idx, "IT Receiver Signature"] = sig_it_path
    df.at[idx, "IT Manager"] = it_manager
    df.at[idx, "IT Manager Signature"] = sig_itm_path
    df.at[idx, "Status"] = status
    df.to_excel(EXCEL_FILE, index=False, sheet_name=SHEET_NAME)

    st.success(f"📌 Request {request_no} อัปเดตเป็น {status} แล้ว")

    msg = f"""✅ <b>Request {request_no} has been {status}</b>
📦 Type: {request_data['Request Type']}
🧾 Item: {request_data['Item']} x {request_data['Quantity']}
🏨 Hotel: {request_data['Hotel']}
📁 Department: {request_data['Department']}
🧑‍💻 IT Receiver: {it_receiver}
🧑‍💼 IT Manager: {it_manager}
🏨 Hotel Manager: {hotel_manager}
🕒 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
        )
        st.info("📬 แจ้งเตือน Telegram แล้ว")
    except Exception as e:
        st.warning(f"⚠️ ส่ง Telegram ไม่สำเร็จ: {e}")
