import streamlit as st
import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# ==============================
# CẤU HÌNH
# ==============================

API_KEY = "14ca543dd2310109fc8a0752d7909f51"
COUNTRY = "VN"
VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

EMAIL_SENDER = "247140210105@hpu2.edu.vn"
EMAIL_PASSWORD = "123456Aa@"
EMAIL_RECEIVER = "trai25262006@gmail.com"

# ==============================
# 34 TỈNH THÀNH VIỆT NAM SAU SÁP NHẬP (hiệu lực từ 12/6/2025)
# Dùng tọa độ GPS (lat, lon) để tránh lỗi 404 API
# ==============================
LOCATIONS = {
    # ── 6 THÀNH PHỐ TRỰC THUỘC TRUNG ƯƠNG ──
    "🏙️ Hà Nội": {
        "Phường Hoàn Kiếm":   (21.0285, 105.8542),
        "Phường Đống Đa":     (21.0245, 105.8412),
        "Phường Cầu Giấy":    (21.0372, 105.7903),
        "Phường Long Biên":   (21.0613, 105.8972),
        "Xã Đông Anh":        (21.1497, 105.8458),
        "Xã Gia Lâm":         (21.0012, 105.9281),
        "Xã Sóc Sơn":         (21.2585, 105.8439),
        "Xã Thường Tín":      (20.8677, 105.8689),
        "Xã Chương Mỹ":       (20.9147, 105.7131),
    },
    "🌊 TP. Đà Nẵng (+ Quảng Nam)": {
        "Phường Hải Châu":          (16.0471, 108.2062),
        "Phường Thanh Khê":         (16.0639, 108.1833),
        "Phường Sơn Trà":           (16.0942, 108.2469),
        "Phường Ngũ Hành Sơn":      (16.0023, 108.2535),
        "Xã Hòa Vang":              (15.9826, 108.1327),
        "Phường Liên Chiểu":        (16.0919, 108.1511),
        "Xã Hội An (cũ Quảng Nam)": (15.8801, 108.3380),
        "Xã Tam Kỳ (cũ Quảng Nam)": (15.5694, 108.4732),
        "Xã Điện Bàn":              (15.9013, 108.2572),
        "Xã Núi Thành":             (15.4456, 108.6181),
    },
    "🏙️ TP. Hồ Chí Minh (+ BR-VT, Bình Dương)": {
        "Phường Quận 1":              (10.7769, 106.7009),
        "Phường Bình Thạnh":          (10.8053, 106.7120),
        "Phường Thủ Đức":             (10.8577, 106.7714),
        "Xã Bình Chánh":              (10.6838, 106.5996),
        "Phường Tân Bình":            (10.8015, 106.6519),
        "Phường Quận 7":              (10.7324, 106.7218),
        "Xã Vũng Tàu (cũ BR-VT)":    (10.3460, 107.0843),
        "Xã Thủ Dầu Một (cũ BD)":    (10.9804, 106.6519),
        "Xã Dĩ An (cũ Bình Dương)":  (10.9052, 106.7658),
    },
    "🚢 TP. Hải Phòng (+ Hải Dương)": {
        "Phường Hồng Bàng":           (20.8628, 106.6831),
        "Phường Lê Chân":             (20.8489, 106.6951),
        "Phường Ngô Quyền":           (20.8706, 106.7100),
        "Xã Đồ Sơn":                  (20.7167, 106.7631),
        "Xã Cát Hải":                 (20.7281, 106.9231),
        "Xã Hải Dương (cũ HD)":       (20.9373, 106.3145),
        "Xã Chí Linh (cũ HD)":        (21.1298, 106.4028),
    },
    "🏔️ TP. Huế (giữ nguyên)": {
        "Phường Thuận Hóa":    (16.4637, 107.5909),
        "Xã Phú Vang":         (16.3821, 107.7323),
        "Xã Phong Điền":       (16.6413, 107.3580),
        "Xã Hương Trà":        (16.5272, 107.5085),
        "Xã Phú Lộc":          (16.2457, 107.8823),
        "Xã Nam Đông":         (16.1640, 107.6800),
    },
    "🌆 TP. Cần Thơ (giữ nguyên)": {
        "Phường Ninh Kiều":    (10.0341, 105.7877),
        "Phường Bình Thủy":    (10.0630, 105.7450),
        "Xã Phong Điền":       (10.0201, 105.7133),
        "Xã Vĩnh Thạnh":       (10.2276, 105.6527),
        "Phường Ô Môn":        (10.1233, 105.7395),
        "Xã Thốt Nốt":         (10.2580, 105.5937),
    },

    # ── 28 TỈNH ──
    "🌿 Tuyên Quang (+ Hà Giang)": {
        "TP. Tuyên Quang":     (21.8235, 105.2180),
        "Xã Sơn Dương":        (21.6788, 105.3823),
        "Xã Yên Sơn":          (21.9042, 105.2651),
        "TP. Hà Giang (cũ HG)":(22.8230, 104.9836),
        "Xã Đồng Văn (cũ HG)": (23.2741, 105.3601),
        "Xã Mèo Vạc (cũ HG)":  (23.1563, 105.4236),
    },
    "🏔️ Lào Cai (+ Yên Bái)": {
        "TP. Lào Cai":          (22.4856, 103.9754),
        "Xã Sa Pa":             (22.3364, 103.8438),
        "Xã Bắc Hà":            (22.5311, 104.2831),
        "Xã Bảo Thắng":         (22.3994, 104.1232),
        "TP. Yên Bái (cũ YB)":  (21.7225, 104.9113),
        "Xã Nghĩa Lộ (cũ YB)":  (21.5951, 104.5160),
        "Xã Mù Cang Chải":      (21.8270, 104.0980),
    },
    "⛰️ Thái Nguyên (+ Bắc Kạn)": {
        "TP. Thái Nguyên":      (21.5942, 105.8480),
        "Xã Phổ Yên":           (21.4786, 105.8942),
        "Xã Định Hóa":          (21.8827, 105.6206),
        "TP. Bắc Kạn (cũ BK)":  (22.1474, 105.8348),
        "Xã Ba Bể (cũ BK)":     (22.4082, 105.6229),
    },
    "🌾 Phú Thọ (+ Hòa Bình + Vĩnh Phúc)": {
        # === PHÚ THỌ CŨ ===
        "TP. Việt Trì":              (21.3227, 105.4019),
        "Xã Lâm Thao":               (21.2979, 105.3176),
        "Xã Phù Ninh":               (21.4001, 105.3523),
        "Xã Thanh Sơn":              (21.0948, 105.1912),
        "Xã Yên Lập":                (21.2603, 105.0822),
        "Xã Cẩm Khê":                (21.4432, 105.1476),
        "TX. Phú Thọ":               (21.4008, 105.2261),
        "Xã Tam Nông":               (21.2371, 105.1872),
        "Xã Thanh Thủy":             (21.1551, 105.3042),
        "Xã Hạ Hòa":                 (21.5243, 105.0291),
        "Xã Đoan Hùng":              (21.6115, 105.1712),
        # === HÒA BÌNH CŨ ===
        "TP. Hòa Bình (cũ HB)":      (20.8149, 105.3384),
        "Xã Mai Châu (cũ HB)":       (20.6534, 104.9897),
        "Xã Kim Bôi (cũ HB)":        (20.6437, 105.5002),
        "Xã Lạc Sơn (cũ HB)":        (20.4448, 105.5091),
        "Xã Lương Sơn (cũ HB)":      (20.8989, 105.5312),
        "Xã Kỳ Sơn (cũ HB)":         (20.8527, 105.4108),
        "Xã Đà Bắc (cũ HB)":         (20.9701, 105.0782),
        "Xã Tân Lạc (cũ HB)":        (20.6026, 105.2318),
        "Xã Cao Phong (cũ HB)":      (20.7021, 105.3481),
        "Xã Yên Thủy (cũ HB)":       (20.3514, 105.6173),
        "Xã Lạc Thủy (cũ HB)":       (20.4218, 105.6831),
        # === VĨNH PHÚC CŨ ===
        "TP. Vĩnh Yên (cũ VP)":      (21.3087, 105.5975),
        "TX. Phúc Yên (cũ VP)":      (21.2508, 105.7261),
        "Xã Vĩnh Tường (cũ VP)":     (21.2012, 105.5271),
        "Xã Yên Lạc (cũ VP)":        (21.2381, 105.5842),
        "Xã Tam Dương (cũ VP)":      (21.3532, 105.6253),
        "Xã Tam Đảo (cũ VP)":        (21.4680, 105.6432),
        "Xã Bình Xuyên (cũ VP)":     (21.2792, 105.6631),
        "Xã Lập Thạch (cũ VP)":      (21.4021, 105.4968),
        "Xã Sông Lô (cũ VP)":        (21.4891, 105.4273),
    },
    "🏭 Bắc Ninh (+ Bắc Giang)": {
        "TP. Bắc Ninh":         (21.1861, 106.0763),
        "Xã Từ Sơn":            (21.1219, 105.9791),
        "Xã Tiên Du":           (21.1745, 106.0201),
        "TP. Bắc Giang (cũ BG)":(21.2731, 106.1943),
        "Xã Lạng Giang (cũ BG)":(21.3723, 106.2582),
        "Xã Yên Thế (cũ BG)":   (21.5041, 106.0363),
    },
    "🌊 Hưng Yên (+ Thái Bình)": {
        "TP. Hưng Yên":         (20.6464, 106.0511),
        "Xã Mỹ Hào":            (20.9291, 106.0824),
        "Xã Văn Giang":         (20.9502, 105.9693),
        "TP. Thái Bình (cũ TB)":(20.4463, 106.3420),
        "Xã Đông Hưng (cũ TB)": (20.5038, 106.4521),
    },
    "🌸 Ninh Bình (+ Hà Nam + Nam Định)": {
        "TP. Ninh Bình":         (20.2580, 105.9750),
        "Xã Hoa Lư":             (20.2800, 105.8900),
        "Xã Nho Quan":           (20.3282, 105.7331),
        "TP. Phủ Lý (cũ HN)":   (20.5383, 105.9126),
        "TP. Nam Định (cũ NĐ)":  (20.4200, 106.1683),
        "Xã Giao Thủy (cũ NĐ)": (20.2269, 106.4635),
    },
    "🏝️ Quảng Ninh (giữ nguyên)": {
        "TP. Hạ Long":           (20.9514, 107.0791),
        "TP. Móng Cái":          (21.5225, 107.9694),
        "TP. Uông Bí":           (21.0350, 106.7730),
        "Xã Tiên Yên":           (21.3311, 107.3924),
        "Xã Vân Đồn":            (20.9648, 107.4151),
    },
    "🦅 Lạng Sơn (giữ nguyên)": {
        "TP. Lạng Sơn":          (21.8537, 106.7615),
        "Xã Đình Lập":           (21.5408, 107.1055),
        "Xã Cao Lộc":            (21.9212, 106.8312),
        "Xã Bắc Sơn":            (21.9162, 106.4005),
    },
    "⛰️ Cao Bằng (giữ nguyên)": {
        "TP. Cao Bằng":          (22.6657, 106.2578),
        "Xã Trùng Khánh":        (22.8276, 106.5241),
        "Xã Hà Quảng":           (22.8868, 106.0648),
        "Xã Bảo Lạc":            (22.9473, 105.6742),
    },
    "🏔️ Điện Biên (giữ nguyên)": {
        "TP. Điện Biên Phủ":     (21.3860, 103.0160),
        "Xã Điện Biên Đông":     (21.2748, 103.3218),
        "Xã Mường Ảng":          (21.4900, 103.2300),
        "Xã Tủa Chùa":           (21.9594, 103.4781),
    },
    "🏔️ Lai Châu (giữ nguyên)": {
        "TP. Lai Châu":          (22.3964, 103.4584),
        "Xã Sìn Hồ":             (22.3666, 103.2532),
        "Xã Phong Thổ":          (22.5260, 103.3479),
        "Xã Than Uyên":          (21.9810, 103.9003),
    },
    "🏔️ Sơn La (giữ nguyên)": {
        "TP. Sơn La":            (21.3272, 103.9144),
        "Xã Mộc Châu":           (20.8361, 104.6839),
        "Xã Thuận Châu":         (21.4241, 103.7151),
        "Xã Quỳnh Nhai":         (21.7652, 103.5595),
    },
    "🌳 Thanh Hóa (giữ nguyên)": {
        "TP. Thanh Hóa":         (19.8077, 105.7764),
        "TP. Sầm Sơn":           (19.7390, 105.9020),
        "Xã Ngọc Lặc":           (20.0947, 105.3931),
        "Xã Như Xuân":           (19.6188, 105.3881),
        "Xã Hậu Lộc":            (19.9610, 105.9101),
    },
    "🌾 Nghệ An (giữ nguyên)": {
        "TP. Vinh":              (18.6733, 105.6922),
        "TP. Cửa Lò":            (18.7959, 105.7314),
        "Xã Diễn Châu":          (18.9763, 105.5810),
        "Xã Con Cuông":          (19.0580, 104.8960),
        "Xã Quế Phong":          (19.5490, 104.8290),
    },
    "🌿 Hà Tĩnh (giữ nguyên)": {
        "TP. Hà Tĩnh":           (18.3557, 105.8877),
        "TP. Hồng Lĩnh":         (18.5148, 105.7281),
        "Xã Kỳ Anh":             (18.0742, 106.2762),
        "Xã Hương Sơn":          (18.4977, 105.3690),
        "Xã Đức Thọ":            (18.4688, 105.6236),
    },
    "🌊 Quảng Trị (+ Quảng Bình)": {
        "TP. Đông Hà":            (16.8163, 107.0996),
        "Xã Vĩnh Linh":           (17.0863, 107.1284),
        "Xã Cam Lộ":              (16.7643, 107.0147),
        "TP. Đồng Hới (cũ QB)":   (17.4831, 106.5991),
        "Xã Quảng Trạch (cũ QB)": (17.7523, 106.4271),
        "Xã Minh Hóa (cũ QB)":    (17.7512, 105.7895),
    },
    "🌊 Quảng Ngãi (+ Kon Tum)": {
        "TP. Quảng Ngãi":         (15.1214, 108.8048),
        "Xã Đức Phổ":             (14.8231, 108.9459),
        "Xã Sơn Tịnh":            (15.2128, 108.7281),
        "TP. Kon Tum (cũ KT)":    (14.3497, 108.0005),
        "Xã Đắk Hà (cũ KT)":     (14.5854, 107.9921),
        "Xã Ngọc Hồi (cũ KT)":   (14.3686, 107.7271),
    },
    "🌄 Gia Lai (+ Bình Định)": {
        "TP. Pleiku":              (13.9830, 108.0000),
        "TP. An Khê":              (13.9567, 108.6491),
        "Xã Chư Sê":               (13.6940, 108.0820),
        "TP. Quy Nhơn (cũ BĐ)":   (13.7829, 109.2196),
        "Xã Tuy Phước (cũ BĐ)":   (13.7081, 109.1470),
        "Xã An Nhơn (cũ BĐ)":     (13.8769, 109.0980),
    },
    "🏖️ Khánh Hòa (+ Ninh Thuận)": {
        "TP. Nha Trang":            (12.2388, 109.1967),
        "Xã Ninh Hòa":              (12.4887, 109.1260),
        "Xã Cam Lâm":               (12.0532, 109.1517),
        "Xã Vạn Ninh":              (12.6612, 109.2199),
        "TP. Phan Rang (cũ NT)":    (11.5639, 108.9881),
        "Xã Ninh Phước (cũ NT)":    (11.4813, 108.9564),
        "Xã Thuận Bắc (cũ NT)":     (11.9063, 108.8726),
    },
    "🌲 Đắk Lắk (+ Phú Yên)": {
        "TP. Buôn Ma Thuột":        (12.6833, 108.0500),
        "Xã Buôn Đôn":              (12.8127, 107.8474),
        "Xã Cư M'gar":              (12.8341, 108.0590),
        "TP. Tuy Hòa (cũ PY)":      (13.0953, 109.3183),
        "Xã Sông Cầu (cũ PY)":      (13.4381, 109.2218),
        "Xã Đông Hòa (cũ PY)":      (13.0112, 109.3321),
    },
    "🌺 Lâm Đồng (+ Đắk Nông + Bình Thuận)": {
        "TP. Đà Lạt":               (11.9404, 108.4583),
        "TP. Bảo Lộc":              (11.5469, 107.8073),
        "Xã Đức Trọng":             (11.7584, 108.3001),
        "TP. Gia Nghĩa (cũ ĐN)":    (11.9790, 107.6909),
        "TP. Phan Thiết (cũ BT)":   (10.9289, 108.1021),
        "Xã Mũi Né (cũ BT)":        (10.9433, 108.2876),
        "Xã Tuy Phong (cũ BT)":     (11.3236, 108.7409),
    },
    "🌆 Đồng Nai (+ Bình Phước)": {
        "TP. Biên Hòa":             (10.9574, 106.8426),
        "TP. Long Khánh":            (10.9327, 107.2428),
        "Xã Trảng Bom":             (10.9900, 107.0121),
        "TP. Đồng Xoài (cũ BP)":    (11.5353, 106.8912),
        "Xã Bình Long (cũ BP)":     (11.6444, 106.6056),
        "Xã Phước Long (cũ BP)":    (11.9880, 107.0040),
    },
    "🌴 Tây Ninh (+ Long An)": {
        "TP. Tây Ninh":             (11.3601, 106.0985),
        "Xã Hòa Thành":             (11.3002, 106.1203),
        "Xã Gò Dầu":                (11.1332, 106.2729),
        "TP. Tân An (cũ LA)":       (10.5353, 106.4082),
        "Xã Đức Hòa (cũ LA)":       (10.8875, 106.3074),
        "Xã Bến Lức (cũ LA)":       (10.6440, 106.4871),
    },
    "🌾 Vĩnh Long (+ Trà Vinh + Bến Tre)": {
        "TP. Vĩnh Long":            (10.2397, 105.9722),
        "Xã Long Hồ":               (10.2012, 105.9481),
        "TP. Trà Vinh (cũ TV)":     (9.9347,  106.3452),
        "Xã Cầu Ngang (cũ TV)":     (9.7874,  106.4218),
        "TP. Bến Tre (cũ BT)":      (10.2433, 106.3756),
        "Xã Mỏ Cày Nam (cũ BT)":    (10.0592, 106.3781),
    },
    "🌊 Đồng Tháp (+ Tiền Giang)": {
        "TP. Cao Lãnh":             (10.4595, 105.6312),
        "TP. Sa Đéc":               (10.2937, 105.7578),
        "Xã Tháp Mười":             (10.5601, 105.8521),
        "TP. Mỹ Tho (cũ TG)":       (10.3597, 106.3600),
        "Xã Cai Lậy (cũ TG)":       (10.4638, 106.0881),
        "Xã Gò Công (cũ TG)":       (10.3672, 106.6722),
    },
    "🦜 An Giang (+ Kiên Giang)": {
        "TP. Long Xuyên":           (10.3861, 105.4352),
        "TP. Châu Đốc":             (10.7012, 105.1168),
        "Xã Thoại Sơn":             (10.3210, 105.3192),
        "TP. Rạch Giá (cũ KG)":     (10.0121, 105.0809),
        "TP. Phú Quốc (cũ KG)":     (10.2897, 103.9840),
        "Xã Kiên Lương (cũ KG)":    (10.2763, 104.6510),
    },
    "🌿 Cà Mau (+ Sóc Trăng + Bạc Liêu)": {
        "TP. Cà Mau":               (9.1769,  105.1500),
        "Xã Năm Căn":               (8.9756,  105.0039),
        "Xã U Minh":                (9.3624,  104.9188),
        "TP. Sóc Trăng (cũ ST)":    (9.6027,  105.9739),
        "Xã Vĩnh Châu (cũ ST)":     (9.2764,  106.2974),
        "TP. Bạc Liêu (cũ BL)":     (9.2940,  105.7278),
        "Xã Giá Rai (cũ BL)":       (9.2321,  105.4418),
    },
}

# ==============================
# GỢI Ý TRANG PHỤC / ĐỒ DÙNG
# ==============================

def get_suggestions(weather_main, temp):
    suggestions = []
    icons = []

    # Gợi ý theo thời tiết
    weather_lower = weather_main.lower()

    if "rain" in weather_lower or "drizzle" in weather_lower or "thunderstorm" in weather_lower:
        suggestions += ["☂️ Mang ô hoặc áo mưa", "👟 Đi giày chống thấm hoặc dép", "🎒 Bọc túi bằng túi nylon"]
        icons.append("🌧️")
    elif "snow" in weather_lower:
        suggestions += ["🧥 Mặc áo bông dày", "🧤 Đeo găng tay & khăn quàng", "🥾 Đi ủng chống trơn trượt"]
        icons.append("❄️")
    elif "fog" in weather_lower or "mist" in weather_lower or "haze" in weather_lower:
        suggestions += ["😷 Đeo khẩu trang (bụi mù)", "🔦 Cẩn thận khi tham gia giao thông", "🧥 Mặc áo khoác nhẹ"]
        icons.append("🌫️")
    elif "clear" in weather_lower:
        suggestions += ["🕶️ Đeo kính mát", "🧴 Thoa kem chống nắng SPF 50+", "🎩 Đội nón/mũ rộng vành"]
        icons.append("☀️")
    elif "clouds" in weather_lower:
        suggestions += ["🌂 Mang theo ô đề phòng", "👕 Trang phục nhẹ nhàng, thoải mái"]
        icons.append("☁️")

    # Gợi ý theo nhiệt độ
    if temp is not None:
        if temp < 15:
            suggestions += ["🧣 Mặc áo khoác dày, khăn quàng cổ", "🧤 Đeo găng tay giữ ấm", "☕ Uống đồ ấm để giữ nhiệt"]
        elif 15 <= temp < 22:
            suggestions += ["🧥 Mặc áo khoác nhẹ hoặc áo len", "👖 Quần dài thoải mái"]
        elif 22 <= temp < 28:
            suggestions += ["👕 Trang phục thoáng mát", "💧 Uống đủ nước (2 lít/ngày)"]
        elif 28 <= temp < 35:
            suggestions += ["🩱 Mặc vải mỏng, thoáng khí", "💦 Bổ sung nước thường xuyên", "🌿 Tránh nắng giờ cao điểm 11h–14h"]
        else:
            suggestions += ["🆘 Nắng nóng gay gắt! Hạn chế ra ngoài", "🧊 Uống nhiều nước mát, tránh mất nước", "🏠 Ở trong nhà có điều hòa nếu có thể"]

    return suggestions

# ==============================
# LẤY DỮ LIỆU THỜI TIẾT
# ==============================

def get_weather_data(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric",
        "lang": "vi"
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        weather_main = data["weather"][0]["main"]
        weather_desc = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        feels_like = data["main"]["feels_like"]
        return weather_main, weather_desc, temperature, humidity, wind_speed, feels_like
    except Exception as e:
        st.error(f"❌ Lỗi lấy dữ liệu: {e}")
        return None, None, None, None, None, None


# ==============================
# THỜI GIAN VIỆT NAM
# ==============================

def get_vn_time(fmt="%H:%M:%S"):
    return datetime.now(VN_TZ).strftime(fmt)

def get_vn_datetime():
    return datetime.now(VN_TZ).strftime("%d/%m/%Y %H:%M")


# ==============================
# KIỂM TRA MƯA
# ==============================

def is_rain(main):
    if main is None:
        return False
    return any(x in main.lower() for x in ["rain", "drizzle", "thunderstorm"])


# ==============================
# GỬI EMAIL
# ==============================

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
# GIAO DIỆN CHÍNH
# ==============================

st.set_page_config(page_title="Theo dõi thời tiết", page_icon="🌦️", layout="wide")

st.title("🌦️ Theo dõi thời tiết & Gợi ý trang phục")

# --- Chọn tỉnh/thành ---
col_prov, col_dist = st.columns(2)
with col_prov:
    province = st.selectbox("🗺️ Chọn tỉnh / thành phố", list(LOCATIONS.keys()))
with col_dist:
    district_options = LOCATIONS[province]
    district_label = st.selectbox("📍 Chọn quận / huyện / thị xã", list(district_options.keys()))

lat, lon = district_options[district_label]

st.caption(f"🔎 Đang theo dõi: **{district_label}** | ⏰ Giờ Việt Nam: **{get_vn_time()}**")

# Auto refresh mỗi 30 giây
st_autorefresh(interval=30000, key="refresh")

# Lưu lịch sử nhiệt độ
if "history" not in st.session_state:
    st.session_state.history = []
if "last_location" not in st.session_state:
    st.session_state.last_location = district_label

# Reset lịch sử khi đổi địa điểm
if st.session_state.last_location != district_label:
    st.session_state.history = []
    st.session_state.last_location = district_label

# ==============================
# LẤY DỮ LIỆU
# ==============================

main, desc, temp, humidity, wind_speed, feels_like = get_weather_data(lat, lon)

if main:
    now_str = get_vn_time()
    now_full = get_vn_datetime()

    # --- Thẻ thông tin thời tiết ---
    st.markdown("### 🌡️ Thông tin thời tiết hiện tại")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌡️ Nhiệt độ", f"{temp}°C", f"Cảm giác {feels_like}°C")
    c2.metric("💧 Độ ẩm", f"{humidity}%")
    c3.metric("💨 Gió", f"{wind_speed} m/s")
    c4.metric("🌤️ Thời tiết", desc.capitalize())

    # --- Cảnh báo mưa ---
    if is_rain(main):
        st.warning(f"🌧️ **Cảnh báo:** Có khả năng mưa tại {district_label}! Hãy chuẩn bị ô và áo mưa.")
        if st.button("📧 Gửi email cảnh báo mưa"):
            msg_content = f"""
Thời gian: {now_full} (Giờ Việt Nam)
Địa điểm: {district_label}

Dự báo: {desc}
Nhiệt độ: {temp}°C | Cảm giác: {feels_like}°C
Độ ẩm: {humidity}% | Gió: {wind_speed} m/s

⚠️ Có khả năng mưa! Hãy mang ô và áo mưa!
"""
            if send_email(msg_content):
                st.success("📨 Đã gửi email cảnh báo!")
            else:
                st.error("❌ Gửi email thất bại. Kiểm tra lại cấu hình SMTP.")
    else:
        st.info(f"☀️ Không có mưa tại {district_label} vào lúc này.")

    # --- Gợi ý trang phục & đồ dùng ---
    st.markdown("---")
    st.markdown("### 👗 Gợi ý trang phục & đồ dùng")

    suggestions = get_suggestions(main, temp)

    if suggestions:
        cols = st.columns(min(len(suggestions), 3))
        for i, tip in enumerate(suggestions):
            with cols[i % 3]:
                st.success(tip)
    else:
        st.info("Không có gợi ý đặc biệt cho thời tiết hiện tại.")

    # Gợi ý mức độ hoạt động
    st.markdown("#### 🏃 Mức độ phù hợp để ra ngoài")
    if is_rain(main) or "thunderstorm" in main.lower():
        st.error("🚫 **Không nên ra ngoài** – mưa lớn hoặc dông sét, hãy ở trong nhà.")
    elif temp > 37:
        st.error("🔥 **Hạn chế ra ngoài** – nắng nóng nguy hiểm.")
    elif "fog" in main.lower() or "mist" in main.lower():
        st.warning("⚠️ **Thận trọng khi ra ngoài** – tầm nhìn kém do sương mù.")
    elif 20 <= temp <= 32 and "clear" in main.lower():
        st.success("✅ **Thời tiết lý tưởng** – thích hợp cho các hoạt động ngoài trời!")
    else:
        st.info("🌤️ **Bình thường** – có thể ra ngoài nhưng chú ý thời tiết.")

    # --- Lưu lịch sử ---
    st.session_state.history.append({"time": now_str, "temp": temp, "humidity": humidity})

    # --- Biểu đồ ---
    st.markdown("---")
    st.subheader("📊 Biểu đồ nhiệt độ & độ ẩm (30 giây / lần)")

    if len(st.session_state.history) > 1:
        df = pd.DataFrame(st.session_state.history).set_index("time")
        tab1, tab2 = st.tabs(["🌡️ Nhiệt độ (°C)", "💧 Độ ẩm (%)"])
        with tab1:
            st.line_chart(df["temp"])
        with tab2:
            st.line_chart(df["humidity"])
    else:
        st.info("⏳ Đang thu thập dữ liệu... Vui lòng chờ vài lần làm mới.")

    # --- Thời gian cập nhật ---
    st.caption(f"🕐 Cập nhật lần cuối: {now_full} (Giờ Việt Nam, GMT+7)")