import streamlit as st
from google import genai
from google.genai import types

# ---------------------------
# 페이지 설정
# ---------------------------
st.set_page_config(
    page_title="연애상담 챗봇",
    page_icon="💕",
    layout="centered"
)

st.title("💕 연애상담 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반")

# ---------------------------
# API Key 로드
# ---------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)

except Exception:
    st.error(
        "GEMINI_API_KEY를 불러올 수 없습니다. "
        "Streamlit Secrets 설정을 확인하세요."
    )
    st.stop()

# ---------------------------
# 시스템 프롬프트
# ---------------------------
SYSTEM_PROMPT = """
당신은 전문 연애상담 코치입니다.

규칙:
- 공감적이고 친절하게 답변한다.
- 사용자의 감정을 존중한다.
- 관계 개선을 위한 현실적인 조언을 제공한다.
- 단정적인 판단을 하지 않는다.
- 상대방을 비난하도록 유도하지 않는다.
- 답변은 자연스럽고 읽기 쉽게 작성한다.
- 필요하면 구체적인 대화 예시를 제공한다.
- 한국어로 답변한다.
"""

# ---------------------------
# 세션 상태 초기화
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# 이전 대화 표시
# ---------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------
# 사용자 입력
# ---------------------------
user_input = st.chat_input("연애 고민을 입력해보세요...")

if user_input:

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        # 대화 기록 생성
        conversation = SYSTEM_PROMPT + "\n\n"

        for msg in st.session_state.messages:
            role = "사용자" if msg["role"] == "user" else "상담사"
            conversation += f"{role}: {msg['content']}\n"

        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):

                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=conversation,
                    config=types.GenerateContentConfig(
                        temperature=0.8,
                        max_output_tokens=1000,
                    ),
                )

                answer = response.text

                st.markdown(answer)

        # 응답 저장
        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    except Exception as e:
        error_message = (
            "죄송합니다. 응답 생성 중 오류가 발생했습니다.\n\n"
            f"오류 내용: {str(e)}"
        )

        st.error(error_message)

# ---------------------------
# 대화 초기화 버튼
# ---------------------------
st.divider()

if st.button("대화 초기화"):
    st.session_state.messages = []
    st.rerun()
