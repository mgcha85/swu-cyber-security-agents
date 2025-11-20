# app/runner.py
from typing import Optional

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from .settings import get_app_name, get_user_id, get_session_id
from .agents import build_cyber_forecast_review_team

# 전역 SessionService (여러 Runner가 공유 가능)
session_service = InMemorySessionService()


def create_runner() -> Runner:
    """루트 팀 에이전트를 생성하고 Runner를 만든다."""
    root_agent = build_cyber_forecast_review_team()
    return Runner(
        agent=root_agent,
        app_name=get_app_name(),
        session_service=session_service,
    )


async def init_session(user_id: Optional[str] = None, session_id: Optional[str] = None):
    """세션 생성."""
    if user_id is None:
        user_id = get_user_id()
    if session_id is None:
        session_id = get_session_id()

    await session_service.create_session(
        app_name=get_app_name(),
        user_id=user_id,
        session_id=session_id,
    )


async def call_forecast_review_team(
    query: str,
    runner: Runner,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """사용자 질의를 멀티에이전트 팀에 전달하고 최종 응답을 반환한다."""
    if user_id is None:
        user_id = get_user_id()
    if session_id is None:
        session_id = get_session_id()
    """사용자 질의를 멀티에이전트 팀에 전달하고 최종 응답을 반환한다."""
    print(f"\n>>> User Query:\n{query}\n")

    content = types.Content(role="user", parts=[types.Part(text=query)])
    final_response_text = "Agent team did not produce a final response."

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        # 전체 이벤트 디버깅이 필요하면 아래 주석 해제
        # print(f"[Event] author={event.author}, final={event.is_final_response()}, content={event.content}")

        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )
            break

    print(f"\n<<< Multi-Agent Review Response:\n{final_response_text}\n")
    return final_response_text


async def run_demo():
    """36개월 예측에 대한 다중 에이전트 검증 데모."""
    await init_session()
    runner = create_runner()

    # 예시: 내부 모델이 산출한 36개월 랜섬웨어 공격 위험 예측을 문자열로 던진다고 가정
    forecast_text = """
우리 내부 위협 인텔리전스 모델은 향후 36개월 동안 중견 제조업(한국/동아시아 지역)을 대상으로 한
랜섬웨어 공격이 다음과 같은 양상을 보일 것으로 예측한다:

- 첫 12개월: 주로 피싱 기반 초기 침투 및 파일 암호화를 동반한 전통적인 랜섬웨어 캠페인이 증가한다.
- 12~24개월: 공급망 공격(SaaS/관리형 서비스)를 경유한 랜섬웨어가 주요 벡터가 된다.
- 24~36개월: OT 네트워크(생산 설비)를 직접 겨냥한 랜섬웨어 및 데이터 파괴형 공격이 두드러진다.

모델은 특히 18~24개월 구간에서 공격 건수가 피크를 이룬다고 예측하며,
대부분의 조직이 완전한 백업/복구 체계를 갖추지 못해 평균 피해 금액이 크게 증가할 것이라고 본다.
    """.strip()

    query = (
        "다음은 우리 예측 모델이 산출한 36개월 랜섬웨어 공격 예측이다.\n\n"
        f"{forecast_text}\n\n"
        "위 예측에 대해 다음 5가지 관점에서 검증하고 보정해줘:\n"
        "1. 공격자 실현 가능성(Attacker Feasibility)\n"
        "2. 방어자 대비 수준(Defensive Readiness)\n"
        "3. 취약점 활용 속도(Exploit Kinetics)\n"
        "4. 산업/지리적 맥락(Sector/Geo Context)\n"
        "5. 위험 및 비용 영향(Risk & Cost Impact)\n\n"
        "각 에이전트는 자신의 관점에서 예측을 평가하고, 마지막 에이전트는 "
        "관점별 합의/불일치와 리스크-비용 관점의 최종 로드맵을 정리해줘."
    )

    await call_forecast_review_team(query=query, runner=runner)
