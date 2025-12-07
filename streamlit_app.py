import streamlit as st
import json
import os

# ====================================================
# 0. 페이지 기본 설정
# ====================================================
st.set_page_config(
    page_title="성향 맞춤 실내 식물 큐레이터",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================================================
# 1. 매핑 딕셔너리 정의 및 JSON 키 설정
# ====================================================

DIFFICULTY_MAP = {
    '매우 귀찮음 (물 주기를 자주 잊어요) 😴': '하',
    '보통 (주 1~2회 정도는 봐줄 수 있어요) 🪴': '중',
    '열정적 (매일 상태를 확인하고 싶어요) ✨': '상'
}

LIGHT_MAP = {
    '빛이 하루 종일 잘 드는 창가 ☀️': '밝음',
    '간접광이 들어오는 실내 중간 🌥️': '중간',
    '어둡거나 빛이 거의 없는 곳 🌑': '낮음'
}

SIZE_MAP = {
    '15cm 이하 (책상 위, 작은 선반용) 🤏': '소',
    '15cm 초과 ~ 30cm 이하 (중형 스탠드) 📏': '중',
    '30cm 초과 (바닥 배치, 코너 공간) 🌳': '대'
}

AIR_MAP = {
    '공기 정화 능력이 높음': '높음',
    '일반적인 공기 정화 수준': '보통',
    '기능보다 관상 목적': '낮음'
}

PET_MAP = {
    '반려동물/아이에게 안전함 ✅': '안전',
    '섭취 시 주의 필요 ⚠️': '주의'
}

GROWTH_MAP = {
    '성장이 매우 느려 분갈이가 거의 필요 없음 🐌': '느림',
    '보통 속도로 관리하기 적당함 🌳': '보통',
    '성장이 빨라 자주 가지치기/분갈이가 필요함 🌱': '빠름'
}

ALL_MAPS = [DIFFICULTY_MAP, LIGHT_MAP, SIZE_MAP, AIR_MAP, PET_MAP, GROWTH_MAP]
JSON_KEYS = ['difficulty', 'light_level', 'size', 'air_purifying', 'pet_safe', 'growth_speed']

# ====================================================
# 2. 데이터 로드
# ====================================================

@st.cache_data
def load_data(file_name):
    try:
        file_path = file_name
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("❌ plants_data.json 파일을 찾을 수 없습니다.")
        return []

PLANT_DATA = load_data('plants_data.json')

# ====================================================
# UI
# ====================================================

st.title("🌿 성향 맞춤 실내 식물 큐레이션")
st.markdown("당신의 관리 성향, 환경, 목적에 가장 적합한 식물을 찾아드립니다.")
st.markdown("---")

all_inputs_text = []

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("## ✅ 관리 성향/환경")

    st.markdown("Q1. 관리 난이도")
    q1 = st.radio(" ", list(DIFFICULTY_MAP.keys()), index=None, key='q1')
    all_inputs_text.append(q1 if q1 else '-- 선택 --')

    st.markdown("Q2. 햇빛 량")
    q2 = st.radio(" ", list(LIGHT_MAP.keys()), index=None, key='q2')
    all_inputs_text.append(q2 if q2 else '-- 선택 --')

with col2:
    st.markdown("## 💡 추가 조건")
    st.markdown(" ")

    st.markdown("Q3. 식물 크기")
    q3 = st.radio(" ", list(SIZE_MAP.keys()), index=None, key='q3')
    all_inputs_text.append(q3 if q3 else '-- 선택 --')

    st.markdown("Q4. 공기정화 능력")
    q4 = st.radio(" ", list(AIR_MAP.keys()), index=None, key='q4')
    all_inputs_text.append(q4 if q4 else '-- 선택 --')

with col3:
    st.markdown("## ⚠️ 생활 환경")
    st.markdown(" ")

    st.markdown("Q5. 반려동물/아이 안전")
    q5 = st.radio(" ", list(PET_MAP.keys()), index=None, key='q5')
    all_inputs_text.append(q5 if q5 else '-- 선택 --')

    st.markdown("Q6. 생장 속도")
    q6 = st.radio(" ", list(GROWTH_MAP.keys()), index=None, key='q6')
    all_inputs_text.append(q6 if q6 else '-- 선택 --')

st.markdown("---")

# ====================================================
# 3. 추천 로직
# ====================================================

all_selected = all((v != '-- 선택 --' and v is not None) for v in all_inputs_text)

if PLANT_DATA and all_selected:

    # 선택값 → 코드 매핑
    filtered_values = []
    for i, selected_text in enumerate(all_inputs_text):
        mapped_value = ALL_MAPS[i].get(selected_text)
        filtered_values.append(mapped_value)

    scored_plants = []

    for plant in PLANT_DATA:
        match_count = 0
        for i, key in enumerate(JSON_KEYS):
            if plant.get(key) == filtered_values[i]:
                match_count += 1

        if match_count > 0:
            scored_plants.append((match_count, plant))

    scored_plants.sort(key=lambda x: x[0], reverse=True)
    recommendations = scored_plants[:3]

    st.header("✅ 추천 결과 (점수 순)")

    if len(recommendations) > 0:
        st.success("🎉 조건 일치 점수가 가장 높은 식물을 보여드립니다!")

        for i, (score, plant) in enumerate(recommendations):
            st.subheader(str(i + 1) + ". " + plant['korean_name'] + " (일치 " + str(score) + "/6)")
            st.info("난이도: " + plant['difficulty'] +
                    " | 빛: " + plant['light_level'] +
                    " | 크기: " + plant['size'])
            st.info("공기정화: " + plant['air_purifying'] +
                    " | 안전성: " + plant['pet_safe'] +
                    " | 생장 속도: " + plant['growth_speed'])

            st.warning("💡 관리 팁: " + plant.get('management_tip', '정보 없음'))
            st.error("⚠️ 잎 변색 대처: " + plant.get('discoloration_tip', '정보 없음'))
            st.markdown("---")

    else:
        st.error("😢 조건과 일치하는 식물이 없습니다.")

elif not all_selected:
    st.info("모든 질문에 답변을 선택해주세요.")

else:
    st.error("❌ 식물 데이터를 불러올 수 없습니다.")
