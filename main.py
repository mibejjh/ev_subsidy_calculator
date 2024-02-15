import streamlit as st

st.title("2024 전기차 보조금 계산기")

col1, col2 = st.columns(2)
with col1:
    col11, col12 = st.columns(2)
    with col11:
        has_obd = st.checkbox("표준OBD")
        has_v2l = st.checkbox("V2L")
        is_taxi = st.checkbox("TAXI")
        long_assurance = st.checkbox("10년 50만km 보증")
        hot_distance = st.slider("상온주행거리", 50, 1000)
        cold_distance = st.slider("저온주행거리", 50, 1000)
        hot_distance_watt = st.slider("상온연비", 1.0, 8.0, step=0.1)
    with col12:
        batt_coef = st.slider("배터리 계수(에너지 밀도)", 0.6, 1.0, step=0.1)
        batt_recycle = st.slider("배터리 계수(자원 순환성)", 0.6, 1.0, step=0.1)
        service_center = st.slider("사후관리계수", 0.7, 1.0, step=0.1)

with col2:
    col21, col22 = st.columns(2)
    with col21:
        fast_chargable = st.radio("충전속도", ["200~", "150~199", "100~149", "~99"])
        car_type = st.radio("형태", options=["중/대형", "경/소형", "초소형"])
    with col22:
        price_dc = st.radio("기본가격", options=["~5499", "5500~8499", "8500~"])
        charger = st.radio("3년내 설치한 표준급속충전기 수", ["~99", "100~199", "200~"])
    이행보조금 = st.selectbox(
        "브랜드",
        [
            "현대/기아",
            "KGM",
            "르노",
            "GM",
            "벤츠",
            "BMW",
            "폭스바겐",
            "도요타",
            "혼다",
            "ETC",
        ],
    )
    max_local_subsidy = st.slider("지자체보조금", 50, 500)

support_energy = 200 if car_type == "중/대형" else 150

k_distance_watt = (
    (hot_distance_watt * 0.75)
    + (cold_distance / hot_distance) * hot_distance_watt * 0.25
) / 5.0

support_energy *= k_distance_watt

support_distance = 200 if car_type == "중/대형" else 150
k_distance = 1.0
distance = hot_distance * 0.75 + cold_distance * 0.25
if car_type == "중/대형":
    if distance >= 500:
        k_distance = 1.12
    elif distance >= 400:
        k_distance = 0.0014 * distance + 0.4214
    elif distance >= 150:
        k_distance = 0.0034 * distance - 0.3786
    else:
        k_distance = 0.13
else:
    # elif car_type == "경/소형":
    if distance > 300:
        k_distance = 1.15
    else:
        k_distance = 0.0030 * distance + 0.2500
support_distance *= k_distance


support = (support_distance + support_energy) if car_type != "초소형" else 250
support += 20 if has_obd else 0


support *= batt_coef * batt_recycle * service_center

support += 0 if 이행보조금 == "ETC" else 140
support += 0 if charger == "~99" else 20 if charger == "100~199" else 40
support += 20 if has_v2l else 0

match fast_chargable:
    case "200~":
        support += 30
    case "150~199":
        support += 26
    case "100~149":
        support += 22
    case "~99":
        support += 0

support += 250 if is_taxi else 0

support *= 1.0 if price_dc == "~5499" else 0.5 if price_dc == "5500~8499" else 0.0

st.header(f"예상 전기차 보조금(국고) : {support:.2f} 만원")

local_subsidy = max_local_subsidy * support / (650 if car_type == "중/대형" else 550)
st.header(f"예상 전기차 보조금(지자체) : {local_subsidy:.2f} 만원")
st.header(f"예상 총 전기차 보조금 : {local_subsidy + support:.2f} 만원")
