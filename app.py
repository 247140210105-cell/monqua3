import streamlit as st
import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

API_KEY = "14ca543dd2310109fc8a0752d7909f51"
VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")
EMAIL_SENDER = "247140210105@hpu2.edu.vn"
EMAIL_PASSWORD = "123456Aa@"
EMAIL_RECEIVER = "trai25262006@gmail.com"

LOCATIONS = {
    "🏙️ Hà Nội": {
        "Quận Hoàn Kiếm, Hà Nội":  (21.0285, 105.8542),
        "Quận Đống Đa, Hà Nội":     (21.0245, 105.8412),
        "Quận Cầu Giấy, Hà Nội":    (21.0372, 105.7903),
        "Quận Long Biên, Hà Nội":   (21.0613, 105.8972),
        "Huyện Đông Anh, Hà Nội":   (21.1497, 105.8458),
        "Huyện Gia Lâm, Hà Nội":    (21.0012, 105.9281),
        "Huyện Sóc Sơn, Hà Nội":    (21.2585, 105.8439),
    },
    "🌊 Đà Nẵng": {
        "Quận Hải Châu, Đà Nẵng":   (16.0471, 108.2062),
        "Quận Thanh Khê, Đà Nẵng":  (16.0639, 108.1833),
        "Quận Sơn Trà, Đà Nẵng":    (16.0942, 108.2469),
        "Quận Ngũ Hành Sơn, Đà Nẵng":(16.0023, 108.2535),
        "Huyện Hòa Vang, Đà Nẵng":  (15.9826, 108.1327),
        "Quận Liên Chiểu, Đà Nẵng": (16.0919, 108.1511),
    },
    "🏙️ TP. Hồ Chí Minh": {
        "Quận 1, TP.HCM":           (10.7769, 106.7009),
        "Quận Bình Thạnh, TP.HCM":  (10.8053, 106.7120),
        "Quận Thủ Đức, TP.HCM":     (10.8577, 106.7714),
        "Huyện Bình Chánh, TP.HCM": (10.6838, 106.5996),
        "Quận Tân Bình, TP.HCM":    (10.8015, 106.6519),
        "Quận 7, TP.HCM":           (10.7324, 106.7218),
    },
    "🌾 Phú Thọ": {
        "TP. Việt Trì, Phú Thọ":    (21.3227, 105.4019),
        "Thị xã Phú Thọ":           (21.4008, 105.2261),
        "Huyện Lâm Thao, Phú Thọ":  (21.2979, 105.3176),
        "Huyện Phù Ninh, Phú Thọ":  (21.4001, 105.3523),
        "Huyện Thanh Sơn, Phú Thọ": (21.0948, 105.1912),
        "Huyện Yên Lập, Phú Thọ":   (21.2603, 105.0822),
        "Huyện Cẩm Khê, Phú Thọ":   (21.4432, 105.1476),
    },
    "🏔️ Lào Cai": {
        "TP. Lào Cai":               (22.4856, 103.9754),
        "Huyện Sa Pa, Lào Cai":      (22.3364, 103.8438),
        "Huyện Bắc Hà, Lào Cai":    (22.5311, 104.2831),
        "Huyện Bảo Thắng, Lào Cai": (22.3994, 104.1232),
        "Huyện Văn Bàn, Lào Cai":   (22.1124, 104.1231),
    },
    "🌿 Cần Thơ": {
        "Quận Ninh Kiều, Cần Thơ":  (10.0341, 105.7877),
        "Quận Bình Thủy, Cần Thơ":  (10.0630, 105.7450),
        "Huyện Phong Điền, Cần Thơ":(10.0201, 105.7133),
        "Huyện Vĩnh Thạnh, Cần Thơ":(10.2276, 105.6527),
        "Quận Ô Môn, Cần Thơ":      (10.1233, 105.7395),
    },
    "🏖️ Khánh Hòa": {
        "TP. Nha Trang, Khánh Hòa":  (12.2388, 109.1967),
        "Thị xã Ninh Hòa, Khánh Hòa":(12.4887, 109.1260),
        "Huyện Cam Lâm, Khánh Hòa":  (12.0532, 109.1517),
        "Huyện Vạn Ninh, Khánh Hòa": (12.6612, 109.2199),
        "Huyện Khánh Vĩnh, Khánh Hòa":(12.2603, 108.9983),
    },
    "🌺 Thừa Thiên Huế": {
        "TP. Huế":                   (16.4637, 107.5909),
        "Huyện Phú Vang, Huế":      (16.3821, 107.7323),
        "Huyện Phong Điền, Huế":    (16.6413, 107.3580),
        "Huyện Hương Trà, Huế":     (16.5272, 107.5085),
        "Huyện Phú Lộc, Huế":       (16.2457, 107.8823),
    },
    "🏞️ Quảng Nam": {
        "TP. Tam Kỳ, Quảng Nam":    (15.5694, 108.4732),
        "TP. Hội An, Quảng Nam":    (15.8801, 108.3380),
        "Huyện Điện Bàn, Quảng Nam":(15.9013, 108.2572),
        "Huyện Đại Lộc, Quảng Nam": (15.8774, 107.9924),
        "Huyện Núi Thành, Quảng Nam":(15.4456, 108.6181),
    },
}

def get_suggestions(weather_main, temp):
    suggestions = []
    weather_lower = weather_main.lower()
    if "rain" in weather_lower or "drizzle" in weather_lower or "thunderstorm" in weather_lower:
        suggestions += ["☂️ Mang ô hoặc áo mưa", "👟 Đi giày chống thấm hoặc dép", "🎒 Bọc túi bằng túi nylon"]
    elif "snow" in weather_lower:
        suggestions += ["🧥 Mặc áo bông dày", "🧤 Đeo găng tay & khăn quàng", "🥾 Đi ủng chống trơn trượt"]
    elif "fog" in weather_lower or "mist" in weather_lower or "haze" in weather_lower:
        suggestions += ["😷 Đeo khẩu trang (bụi mù)", "🔦 Cẩn thận khi tham gia giao thông", "🧥 Mặc áo khoác nhẹ"]
    elif "clear" in weather_lower:
        suggestions += ["🕶️ Đeo kính mát", "🧴 Thoa kem chống nắng SPF 50+", "🎩 Đội nón/mũ rộng vành"]
    elif "clouds" in weather_lower:
        suggestions += ["🌂 Mang theo ô đề phòng", "👕 Trang phục nhẹ nhàng, thoải mái"]
    if temp is not None:
        if temp < 15:
            suggestions += ["🧣 Mặc áo khoác dày, khăn quàng cổ", "🧤 Đeo găng tay giữ ấm", "☕ Uống đồ ấm để giữ nhiệt"]
        elif temp < 22:
            suggestions += ["🧥 Mặc áo khoác nhẹ hoặc áo len", "👖 Quần dài thoải mái"]
        elif temp < 28:
            suggestions += ["👕 Trang phục thoáng mát", "💧 Uống đủ nước (2 lít/ngày)"]
        elif temp < 35:
            suggestions += ["🩱 Mặc vải mỏng, thoáng khí", "💦 Bổ sung nước thường xuyên", "🌿 Tránh nắng 11h–14h"]
        else:
            suggestions += ["🆘 Nắng nóng gay gắt! Hạn chế ra ngoài", "🧊 Uống nhiều nước mát", "🏠 Ở trong nhà có điều hòa"]
    return suggestions

def get_weather_data(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric", "lang": "vi"}
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        return (data["weather"][0]["main"], data["weather"][0]["description"],
                data["main"]["temp"], data["main"]["humidity"],
                data["wind"]["speed"], data["main"]["feels_like"])
    except Exception as e:
        st.error(f"❌ Lỗi lấy dữ liệu: {e}")
        return None, None, None, None, None, None

def get_vn_time(fmt="%H:%M:%S"):
    return datetime.now(VN_TZ).strftime(fmt)

def get_vn_datetime():
    return datetime.now(VN_TZ).strftime("%d/%m/%Y %H:%M")

def is_rain(main):
    if main is None: return False
    return any(x in main.lower() for x in ["rain", "drizzle", "thunderstorm"])

def send_email(message):
    try:
        msg = MIMEText(message, "plain", "utf-8")
        msg["Subject"] = "🌧️ Nhắc nhở thời tiết"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        return True
    except:
        return False

# ==============================
# GIAO DIỆN
# ==============================

st.set_page_config(page_title="Theo dõi thời tiết", page_icon="🌦️", layout="wide")
st.title("🌦️ Theo dõi thời tiết & Gợi ý trang phục")

col_prov, col_dist = st.columns(2)
with col_prov:
    province = st.selectbox("🗺️ Chọn tỉnh / thành phố", list(LOCATIONS.keys()))
with col_dist:
    district_options = LOCATIONS[province]
    district_label = st.selectbox("📍 Chọn quận / huyện", list(district_options.keys()))

lat, lon = district_options[district_label]
st.caption(f"🔎 Đang theo dõi: **{district_label}** | ⏰ Giờ VN: **{get_vn_time()}**")

st_autorefresh(interval=30000, key="refresh")

if "history" not in st.session_state:
    st.session_state.history = []
if "last_location" not in st.session_state:
    st.session_state.last_location = district_label
if st.session_state.last_location != district_label:
    st.session_state.history = []
    st.session_state.last_location = district_label

main, desc, temp, humidity, wind_speed, feels_like = get_weather_data(lat, lon)

if main:
    now_str = get_vn_time()
    now_full = get_vn_datetime()

    st.markdown("### 🌡️ Thông tin thời tiết hiện tại")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌡️ Nhiệt độ", f"{temp}°C", f"Cảm giác {feels_like}°C")
    c2.metric("💧 Độ ẩm", f"{humidity}%")
    c3.metric("💨 Gió", f"{wind_speed} m/s")
    c4.metric("🌤️ Thời tiết", desc.capitalize())

    if is_rain(main):
        st.warning(f"🌧️ **Cảnh báo:** Có khả năng mưa tại {district_label}! Hãy chuẩn bị ô và áo mưa.")
        if st.button("📧 Gửi email cảnh báo mưa"):
            msg_content = f"Thời gian: {now_full} (Giờ VN)\nĐịa điểm: {district_label}\n\nDự báo: {desc}\nNhiệt độ: {temp}°C | Cảm giác: {feels_like}°C\nĐộ ẩm: {humidity}% | Gió: {wind_speed} m/s\n\n⚠️ Có khả năng mưa! Hãy mang ô và áo mưa!"
            st.success("📨 Đã gửi email!") if send_email(msg_content) else st.error("❌ Gửi email thất bại.")
    else:
        st.info(f"☀️ Không có mưa tại {district_label} vào lúc này.")

    st.markdown("---")
    st.markdown("### 👗 Gợi ý trang phục & đồ dùng")
    suggestions = get_suggestions(main, temp)
    if suggestions:
        cols = st.columns(min(len(suggestions), 3))
        for i, tip in enumerate(suggestions):
            with cols[i % 3]:
                st.success(tip)

    st.markdown("#### 🏃 Mức độ phù hợp để ra ngoài")
    if is_rain(main) or "thunderstorm" in main.lower():
        st.error("🚫 **Không nên ra ngoài** – mưa lớn hoặc dông sét.")
    elif temp > 37:
        st.error("🔥 **Hạn chế ra ngoài** – nắng nóng nguy hiểm.")
    elif "fog" in main.lower() or "mist" in main.lower():
        st.warning("⚠️ **Thận trọng** – tầm nhìn kém do sương mù.")
    elif 20 <= temp <= 32 and "clear" in main.lower():
        st.success("✅ **Thời tiết lý tưởng** – thích hợp hoạt động ngoài trời!")
    else:
        st.info("🌤️ **Bình thường** – có thể ra ngoài nhưng chú ý thời tiết.")

    st.session_state.history.append({"time": now_str, "temp": temp, "humidity": humidity})

    st.markdown("---")
    st.subheader("📊 Biểu đồ nhiệt độ & độ ẩm")
    if len(st.session_state.history) > 1:
        df = pd.DataFrame(st.session_state.history).set_index("time")
        tab1, tab2 = st.tabs(["🌡️ Nhiệt độ (°C)", "💧 Độ ẩm (%)"])
        with tab1:
            st.line_chart(df["temp"])
        with tab2:
            st.line_chart(df["humidity"])
    else:
        st.info("⏳ Đang thu thập dữ liệu... Chờ vài lần làm mới.")

    st.caption(f"🕐 Cập nhật lần cuối: {now_full} (Giờ Việt Nam, GMT+7)")