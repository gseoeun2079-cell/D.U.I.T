import streamlit as st
import json
from datetime import datetime
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="학교 & 개인 일정 관리",
    page_icon="📚",
    layout="centered"
)

DATA_FILE = "study_data.json"

# 데이터 저장/불러오기
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

# =========================
# 1️⃣ 학사 일정 & 급식
# =========================
if menu == "📅 학사 일정 & 급식":

    # ✅ CSV 링크로 변경
    sheet_url = "https://docs.google.com/spreadsheets/d/14b1ZOcAatDx8gP-vFzktP45zHS2A3jR9FuOKKPMVhlM/export?format=csv"

    try:
        df = pd.read_csv(sheet_url)
        df.columns = df.columns.str.strip()
    except:
        st.error("구글 시트를 불러올 수 없습니다.")
        st.stop()

    # ✅ 여기로 빼야 함
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    search_date = st.date_input("날짜 선택")
    search_date = pd.to_datetime(search_date)
    
    col1, col2 = st.columns(2)

    # 📌 학사 일정
    with col1:
        st.markdown("### 📌 학사 일정")

        if "날짜" in df.columns and "학사일정" in df.columns:
            row = df[df["날짜"] == search_date]

            if not row.empty:
                schedule = row["학사일정"].values[0]
                if schedule == "없음":
                    st.info("일정 없음")
                else:
                    st.info(schedule)
            else:
                st.info("일정 없음")
        else:
            st.error("시트에 '날짜' 또는 '학사일정' 컬럼이 없습니다")

    # 🍱 급식 메뉴
    with col2:
        st.markdown("### 🍱 급식 메뉴")

        if "날짜" in df.columns and "급식" in df.columns:
            row = df[df["날짜"] == search_date]

            if not row.empty:
                meal = row["급식"].values[0]
                if meal == "급식 없음":
                    st.success("급식 정보 없음")
                else:
                    st.success(meal)
            else:
                st.success("급식 정보 없음")
        else:
            st.error("시트에 '급식' 컬럼이 없습니다")

# =========================
# 2️⃣ 시간표
# =========================
elif menu == "🏫 시간표":
    st.subheader("🏫 시간표")

    day = st.selectbox("요일 선택", list(timetable.keys()))

    for p, subject in zip(periods, timetable[day]):
        st.write(f"**{p}** | {subject}")

# =========================
# 3️⃣ 수행평가
# =========================
elif menu == "📝 수행평가":
    st.subheader("📝 수행평가 관리")

    tasks = load_data()

    # 📅 기준 날짜 선택
    selected_date = st.date_input("기준 날짜 선택")
    selected_date = datetime.combine(selected_date, datetime.min.time())

    # 👉 session_state 초기화
    if "subject_input" not in st.session_state:
        st.session_state.subject_input = ""

    if "deadline_input" not in st.session_state:
        st.session_state.deadline_input = datetime.today()

    # ➕ 수행평가 추가
    with st.expander("➕ 수행평가 추가"):
        subject = st.text_input("과목 / 수행평가 이름", key="subject_input")
        deadline = st.date_input("마감일", key="deadline_input")

        if st.button("추가"):
            if subject:
                tasks.append({
                    "task": subject,
                    "deadline": str(deadline),
                    "done": False
                })
                save_data(tasks)

                # 입력창 초기화
                st.session_state.subject_input = ""
                st.session_state.deadline_input = datetime.today()

                st.success("추가 완료!")
                st.rerun()

    st.markdown("### 📅 수행평가 캘린더")

    hw_tasks = [t for t in tasks if "deadline" in t]

    if not hw_tasks:
        st.info("등록된 수행평가가 없습니다.")
    else:
        # 🔥 완료 여부 + 날짜 기준 정렬
        hw_tasks.sort(
            key=lambda x: (
                x["done"],  # False(미완료) 먼저
                datetime.strptime(x["deadline"], "%Y-%m-%d")
            )
        )

        current_date = None

        for i, t in enumerate(hw_tasks):
            deadline_date = datetime.strptime(t["deadline"], "%Y-%m-%d")
            d_day = (deadline_date - selected_date).days

            if current_date != t["deadline"]:
                st.markdown(f"## 📆 {t['deadline']}")
                current_date = t["deadline"]

            col1, col2, col3 = st.columns([6,1,1])

            with col1:
                if t["done"]:
                    st.write(f"~~{t['task']}~~ ✅ (완료)")
                else:
                    if d_day <= 3 and d_day > 0:
                        st.error(f"🔥 {t['task']} → D-{d_day}")
                    elif d_day == 0:
                        st.error(f"🚨 {t['task']} → 오늘 마감!")
                    elif d_day < 0:
                        st.success(f"{t['task']} → 기한 지남")
                    else:
                        st.warning(f"{t['task']} → D-{d_day}")

            with col2:
                if not t["done"]:
                    if st.button("완료", key=f"done_{i}"):
                        for j in range(len(tasks)):
                            if tasks[j].get("task") == t["task"] and tasks[j].get("deadline") == t["deadline"]:
                                tasks[j]["done"] = True
                                break
                        save_data(tasks)
                        st.rerun()

            with col3:
                if st.button("삭제", key=f"del_{i}"):
                    for j in range(len(tasks)):
                        if tasks[j].get("task") == t["task"] and tasks[j].get("deadline") == t["deadline"]:
                            tasks.pop(j)
                            break
                    save_data(tasks)
                    st.rerun()
# =========================
# 4️⃣ 스터디 플래너
# =========================
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
