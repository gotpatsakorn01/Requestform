import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import requests

st.set_page_config(
    page_title=" Request Form For User",
    page_icon="📋",
    layout="centered"
)

def run():
    st.title("📋 Request Form For User")

# === CONFIG ===
EXCEL_FILE = "requests_full.xlsx"
SHEET_NAME = "Requests"
SIGNATURE_FOLDER = "signatures"
BOT_TOKEN = "7220616384:AAH8j1spxA-UUmihi0ivVLRBuKzZYTtmJuc"
CHAT_ID = "-1002320440146"

# === INITIALIZE ===
os.makedirs(SIGNATURE_FOLDER, exist_ok=True)

columns = [
    "Request Number", "Date", "Request Type", "Item", "Quantity",
    "Hotel", "Department", "Location",
    "Request Name", "Request Signature",
    "HOD", "HOD Signature",
    "IT Receiver", "IT Receiver Signature",
    "IT Manager", "IT Manager Signature",
    "Hotel Manager", "Hotel Manager Signature",
    "Status"
]

if not os.path.exists(EXCEL_FILE):
    pd.DataFrame(columns=columns).to_excel(EXCEL_FILE, index=False, sheet_name=SHEET_NAME)

df = pd.read_excel(EXCEL_FILE)

def generate_request_number():
    if df.empty:
        return "REQ-0001"
    last_request = df["Request Number"].iloc[-1]
    last_num = int(last_request.split("-")[1])
    return f"REQ-{last_num + 1:04d}"

def save_signature(canvas, filename):
    if canvas.image_data is not None:
        img = Image.fromarray((canvas.image_data).astype(np.uint8))
        path = os.path.join(SIGNATURE_FOLDER, filename)
        img.save(path)
        return path
    return ""

# === UI ===
st.title("📋 Request Form: Hardware / Software / Upgrade")
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"**🕒 Date:** `{now}`")

request_type = st.radio("📦 Request Type", ["Hardware", "Software", "Upgrade"])
item_options = {
    "Hardware": ["Computer", "Monitor", "Printer", "Computer+Monitor+UPS(COMSET)", "UPS", "Tablet/IPAD", "Access Point", "Laptop", "Pos Touchscreen", "Pos Printer", "POS Tablet", "Adapter/Charger", "CCTV"],
    "Software": ["ขอซื้อ Windows เพิ่ม", "ขอซื้อ License Windows เพิ่ม", "ขอเพิ่ม Microsoft Office"],
    "Upgrade": ["Computer", "Monitor", "Printer", "Computer+Monitor+UPS(COMSET)", "UPS", "Tablet/IPAD", "Access Point", "Laptop", "Pos Touchscreen", "Pos Printer", "POS Tablet", "Adapter/Charger", "CCTV"]
}
item = st.selectbox("🧾 Item", item_options[request_type])
quantity = st.number_input("🔢 Quantity", min_value=1, value=1)
hotel = st.selectbox("🏨 Hotel", ["The Sands", "The Little Shore", "The Leaf On Sands", "The Leaf Oceanside", "The Waters"])
department = st.selectbox("📁 Department", ["AC","CR","EN","ENS","EX","FB","FO","HK","IT","KC","MELON","SPA","SA&RSVN","TN","HR"])
location = st.text_input("📍 Location")
detail = st.text_area("📝 รายละเอียดเพิ่มเติม / เหตุผลที่ขอ")

# Requester Name + Signature
request_name = st.text_input("👤 Request Name")
st.write("✍️ Request Signature")
canvas_req = st_canvas(height=150, stroke_width=1, key="req_sig")

# HOD Name + Signature
hod = st.text_input("👤 HOD Name")
st.write("✍️ HOD Signature")
canvas_hod = st_canvas(height=150, stroke_width=1, key="hod_sig")

# IT Receiver
it_receiver = st.selectbox("🧑‍💻 IT Receiver", [
    "Siwat Kalasang", "Pongsith Raksanit", "Ratchanon Chada",
    "Nonthawat Saisawan", "IT Trainee"
])

if st.button("✅ Submit Request"):
    request_no = generate_request_number()
    sig_req_path = save_signature(canvas_req, f"{request_no}-req.png")
    sig_hod_path = save_signature(canvas_hod, f"{request_no}-hod.png")

    new_row = {
        "Request Number": request_no,
        "Date": now,
        "Request Type": request_type,
        "Item": item,
        "Quantity": quantity,
        "Hotel": hotel,
        "Department": department,
        "Location": location,
        "Detail": detail,
        "Request Name": request_name,
        "Request Signature": sig_req_path,
        "HOD": hod,
        "HOD Signature": sig_hod_path,
        "IT Receiver": it_receiver,
        "IT Receiver Signature": "",
        "IT Manager": "",
        "IT Manager Signature": "",
        "Hotel Manager": "",
        "Hotel Manager Signature": "",
        "Status": "Pending"
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False, sheet_name=SHEET_NAME)
    st.success(f"📄 Request {request_no} submitted successfully!")

    msg = f"""🆕 <b>New Request Submitted</b>
📄 No: {request_no}
📦 Type: {request_type}
🧾 Item: {item} x {quantity}
🏨 Hotel: {hotel}
📁 Department: {department}
👤 By: {request_name}
🕒 Date: {now}
"""
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
        )
        st.info("📬 แจ้งเตือน Telegram แล้ว")
    except Exception as e:
        st.warning(f"⚠️ ส่ง Telegram ไม่สำเร็จ: {e}")
