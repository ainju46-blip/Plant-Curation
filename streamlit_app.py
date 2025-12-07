import streamlit as st
import json
import os 

# ====================================================
# 0. 페이지 기본 설정 및 이미지 폴더 경로
# ====================================================
st.set_page_config(
    page_title="성향 맞춤 실내 식물 큐레이터",       
    page_icon="🌿",                      
    layout="wide",                       
    initial_sidebar_state="expanded"     
)

# 이미지 파일이 저장된 폴더 경로
IMAGE_DIR = 'images' 

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
NUM_CONDITIONS = len(JSON_KEYS)

# ====================================================
# 2. 데이터 로드 및 UI 설정
# ====================================================

@st.cache_data
def load_data(file_name):
    """JSON 파일을 현재 작업 디렉토리에서 바로 로드하도록 단순화합니다."""
    try:
        file_path = file_name 
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("오류: plants_data.json 파일을 찾을 수 없습니다. JSON 파일 이름(plants_data.json)이 맞는지 확인해주세요.")
        return []

PLANT_DATA = load_data('plants_data.json') 

st.title("🌿 성향 맞춤 실내 식물 큐레이션")
st.markdown("당신의 관리 성향, 환경, 목적에 가장 적합한 식물을 찾아드립니다.")
st.markdown("---")

all_inputs_text = [] 

# 컬럼 3개로 나누어 질문 배치
col1, col2, col3 = st.columns(3)

with col1:
    
    st.markdown("## ✅ **관리 성향/환경**")

     # Q1: st.radio 적용 (크게, 버튼식)
    st.markdown("Q1. 관리 난이도") 
    q1_selection = st.radio(
        " ", options=list(DIFFICULTY_MAP.keys()), index=None, key='q1_radio'
    )
    all_inputs_text.append(q1_selection if q1_selection else '-- 선택 --')
    
    # ⭐ Q2도 st.radio로 통일
    st.markdown("Q2. 햇빛 량") 
    q2_selection = st.radio(" ", options=list(LIGHT_MAP.keys()), index=None, key='q2_radio')
    all_inputs_text.append(q2_selection if q2_selection else '-- 선택 --')


with col2:
    st.markdown("## 💡 **추가 조건**")
    st.markdown(" ") # 정렬을 위한 빈 줄 삽입
    
    # ⭐ Q3도 st.radio로 통일
    st.markdown("Q3. 식물 크기")
    q3_selection = st.radio(" ", options=list(SIZE_MAP.keys()), index=None, key='q3_radio')
    all_inputs_text.append(q3_selection if q3_selection else '-- 선택 --')
    
    # ⭐ Q4도 st.radio로 통일
    st.markdown("Q4. 공기정화 능력")
    q4_selection = st.radio(" ", options=list(AIR_MAP.keys()), index=None, key='q4_radio')
    all_inputs_text.append(q4_selection if q4_selection else '-- 선택 --')


with col3:
    st.markdown("## ⚠️ **생활 환경**")
    st.markdown(" ") # 정렬을 위한 빈 줄 삽입
    
    # ⭐ Q5도 st.radio로 통일
    st.markdown("Q5. 반려동물/아이 안전")
    q5_selection = st.radio(" ", options=list(PET_MAP.keys()), index=None, key='q5_radio')
    all_inputs_text.append(q5_selection if q5_selection else '-- 선택 --')
    
    # ⭐ Q6도 st.radio로 통일
    st.markdown("Q6. 생장 속도")
    q6_selection = st.radio(" ", options=list(GROWTH_MAP.keys()), index=None, key='q6_radio')
    all_inputs_text.append(q6_selection if q6_selection else '-- 선택 --')
    
st.markdown("---")

# ====================================================
# 4. 점수 기반 순위 매기기 로직 및 결과 출력
# ====================================================

# 모든 질문이 선택되었는지 확인
all_selected = all(val != '-- 선택 --' and val != None for val in all_inputs_text) # None 체크 추가

if PLANT_DATA and all_selected:
    
    # 4-1. 긴 문장 선택지를 짧은 코드로 변환 (매핑)
    filtered_values = []
    for i, selected_text in enumerate(all_inputs_text):
        # ALL_MAPS[i].get(selected_text)는 None을 반환할 수 있으므로, None 대신 '-- 선택 --'이 오도록 처리합니다.
        # 이 경우, None이 매핑되어 오는 것을 방지하기 위해 if/else문 대신 dict.get()을 사용합니다.
        # (단, st.radio는 '선택' 옵션이 없어 None이 반환될 수 있으므로, 이미 상단에서 처리됨)
        filtered_values.append(ALL_MAPS[i].get(selected_text))

    # ⭐ 핵심 로직: 부분 일치 점수를 저장할 리스트를 만듭니다.
    scored_plants = [] 

    # 4-2. 6가지 조건 순위 매기기 실행
    for plant in PLANT_DATA:
        match_count = 0
        
        for i, key in enumerate(JSON_KEYS):
            if plant.get(key) == filtered_values[i]:
                match_count += 1 
        
        # 1개 이상 조건이 일치하면 리스트에 추가합니다.
        if match_count > 0:
            scored_plants.append((match_count, plant))

    # 4-3. 순위 확정 및 결과 제한
    scored_plants.sort(key=lambda x: x[0], reverse=True) 
    final_recommendations = scored_plants[:3] # 최대 3개 제한
    
    # 4-4. 결과 출력
    st.header("✅ 추천 결과 (점수 순)")
    st.markdown("선택하신 **6가지 조건 중 가장 많이 일치**하는 식물을 순위별로 보여드립니다.")
    
    if len(final_recommendations) > 0:
        st.success("🎊 조건 일치 점수가 가장 높은 상위 {0}개 식물을 추천합니다!".format(len(final_recommendations)))
        
        for i, (score, plant) in enumerate(final_recommendations):
            # 5-1. 컬럼을 2개로 나누어 이미지와 텍스트를 배치
            col_img, col_text = st.columns([1, 3])
            
            with col_img:
                # ⭐⭐ 이미지 출력 부분 ⭐⭐
                image_file_name = plant.get('image_file') 
                if image_file_name:
                    image_path = "{0}/{1}".format(IMAGE_DIR, image_file_name)
                    try:
                        st.image(image_path, caption=plant['korean_name'], width=150)
                    except FileNotFoundError:
                        st.warning("이미지 파일 {0} 없음".format(image_file_name))
                else:
                    st.warning("이미지 경로 누락")
            
            with col_text:
                # 텍스트 정보 출력
                st.subheader("{0}. {1} (✅ {2}/6 조건 일치)".format(i + 1, plant['korean_name'], score))
                st.info("🌿 난이도: {0} | ☀️ 빛: {1} | 📏 크기: {2}".format(
                    plant['difficulty'], plant['light_level'], plant['size']))
                st.info("💨 공기정화: {0} | 🐶 안전성: {1} | 📈 생장 속도: {2}".format(
                    plant['air_purifying'], plant['pet_safe'], plant['growth_speed']))
            
            # 팁은 전체 너비로 출력
            st.warning("💡 일반 관리 팁: {0}".format(plant.get('management_tip', '팁 정보 없음')))
            st.error("⚠️ 잎 변색 시 대처법: {0}".format(plant.get('discoloration_tip', '대처 팁 정보 없음'))) 
            st.markdown("---")
            
    else:
        st.error("😭 선택하신 어떤 조건에도 일치하는 식물을 찾지 못했습니다. (0/6 조건 일치)")
        
elif not all_selected:
    st.info("모든 질문에 답변을 선택해주세요.") 
```
