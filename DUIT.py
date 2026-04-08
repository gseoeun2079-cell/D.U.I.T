import streamlit as st
import json
from datetime import datetime

# 페이지 디자인
st.set_page_config(
    page_title="학교 & 개인 일정 관리",
    page_icon="📚",
    layout="centered"
)

# 데이터 파일
DATA_FILE = "study_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# 데이터
schedules = {
    "2026-04-23": ["중간고사 시작"]
}

meals = {
    "2026-04-06": "발아현미밥, 어묵탕, 멸치볶음, 함박스테이크",
    "2026-04-07": "기장밥, 콩나물국, 오리불고기, 김치"
}

timetable = {
    '월': ['기초', 'A', '문학A', 'B', '영듣', 'C', '대수'],
    '화': ['영어', 'D', '대수', 'A', '기초', '문학B', '특색'],
    '수': ['영어', 'B', '진로', 'C', '자율', '동아리'],
    '목': ['기초', 'D', '스생', 'A', '대수', 'B'],
    '금': ['문학B', 'C', '문학A', 'D', '스생', '영어', '대수']
}

periods = ['1교시','2교시','3교시','4교시','5교시','6교시','7교시']

homeworks = {
    "화학 실험 보고서": "2026-04-15",
    "경제 수행평가": "2026-04-20",
    "영어 단어 시험": "2026-04-10"
}

# 제목
st.title("📚 학교 & 개인 일정 관리")
st.caption("시간표 · 수행평가 · 급식 · 공부 계획을 한 번에 관리")

# 메뉴
menu = st.sidebar.radio(
    "메뉴 선택",
    ["📅 학사 일정 & 급식", "🏫 시간표", "📝 수행평가", "📋 스터디 플래너"]
)

# 1️⃣ 학사 일정 & 급식
if menu == "📅 학사 일정 & 급식":
    st.subheader("📅 날짜별 정보")

    search_date = st.date_input("날짜 선택", value=datetime(2026, 4, 6))
    search_date_str = search_date.strftime("%Y-%m-%d")
    
    st.write("선택:", search_date_str)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📌 학사 일정")
        data = schedules.get(search_date_str)
        if data:
            for s in data:
                st.info(s)
        else:
            st.info("일정 없음")
    with col2:
        st.markdown("### 🍱 급식 메뉴")
        meal = meals.get(search_date_str)
        if meal:
            st.success(meal)
        else:
            st.success("급식 정보 없음")
# 2️⃣ 시간표
elif menu == "🏫 시간표":
    st.subheader("🏫 시간표")

    day = st.selectbox("요일 선택", list(timetable.keys()))

    for p, subject in zip(periods, timetable[day]):
        st.write(f"**{p}**  |  {subject}")

# 3️⃣ 수행평가
elif menu == "📝 수행평가":
    st.subheader("📝 수행평가 D-Day")

    today = datetime.now()

    for subject, deadline in homeworks.items():
        target = datetime.strptime(deadline, "%Y-%m-%d")
        d_day = (target - today).days + 1

        if d_day > 0:
            st.warning(f"{subject} → D-{d_day}")
        elif d_day == 0:
            st.error(f"{subject} → 오늘 마감!")
        else:
            st.success(f"{subject} → 완료됨")

# 4️⃣ 스터디 플래너
elif menu == "📋 스터디 플래너":
    st.subheader("📋 공부 계획 관리")

    tasks = load_data()

    # 입력
    with st.expander("➕ 할 일 추가"):
        task = st.text_input("할 일")
        priority = st.slider("우선순위", 1, 3, 2)

        if st.button("추가"):
            if task:
                tasks.append({
                    "task": task,
                    "priority": priority,
                    "done": False
                })
                save_data(tasks)
                st.rerun()

    # 목록
    st.markdown("### 📌 할 일 목록")

    for i, t in enumerate(tasks):
        col1, col2 = st.columns([5, 1])

        with col1:
            if t["done"]:
                st.write(f"~~{t['task']}~~ ✅")
            else:
                st.write(f"{t['task']} (⭐{t['priority']})")

        with col2:
            if not t["done"]:
                if st.button("완료", key=i):
                    tasks[i]["done"] = True
                    save_data(tasks)
                    st.rerun()

    # 진행률
    done = sum(1 for t in tasks if t["done"])
    total = len(tasks)

    st.markdown("### 📊 진행률")

    if total == 0:
        st.info("아직 할 일이 없습니다.")
    else:
        st.progress(done / total)
        st.write(f"{done} / {total} 완료")
