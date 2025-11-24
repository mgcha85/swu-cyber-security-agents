# app/agents.py
from typing import Dict, Any

from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.agents.invocation_context import InvocationContext

from .settings import get_config, create_model
from .tools import (
    assess_attacker_feasibility,
    assess_defensive_readiness,
    assess_exploit_kinetics,
    assess_context_realism,
    estimate_risk_and_cost,
)


def print_agent_prompt(context: InvocationContext, prompt: str):
    """에이전트에 전달되는 프롬프트를 출력하는 콜백 함수."""
    print(f"\n[DEBUG] Agent: {context.agent_name}")
    print(f"[DEBUG] Prompt:\n{prompt}\n")


def build_forecast_interpreter_agent(agent_cfg: Dict[str, Any]) -> Agent:
    model = create_model(agent_cfg["model"])
    return Agent(
        name=agent_cfg["name"],
        model=model,
        description=agent_cfg["description"],
        instruction=agent_cfg["instruction"],
        # No tools needed for interpretation, it just reads the input (CSV)
        output_key=agent_cfg.get("output_key", "forecast_interpretation"),
        before_model_callback=print_agent_prompt,
    )


def build_attacker_feasibility_agent(agent_cfg: Dict[str, Any]) -> Agent:
    model = create_model(agent_cfg["model"])
    return Agent(
        name=agent_cfg["name"],
        model=model,
        description=agent_cfg["description"],
        instruction=agent_cfg["instruction"],
        tools=[assess_attacker_feasibility],
        output_key=agent_cfg.get("output_key", "attacker_feasibility_analysis"),
        before_model_callback=print_agent_prompt,
    )


def build_defensive_readiness_agent(agent_cfg: Dict[str, Any]) -> Agent:
    model = create_model(agent_cfg["model"])
    return Agent(
        name=agent_cfg["name"],
        model=model,
        description=agent_cfg["description"],
        instruction=agent_cfg["instruction"],
        tools=[assess_defensive_readiness],
        output_key=agent_cfg.get("output_key", "defensive_readiness_analysis"),
        before_model_callback=print_agent_prompt,
    )


def build_exploit_kinetics_agent(agent_cfg: Dict[str, Any]) -> Agent:
    model = create_model(agent_cfg["model"])
    return Agent(
        name=agent_cfg["name"],
        model=model,
        description=agent_cfg["description"],
        instruction=agent_cfg["instruction"],
        tools=[assess_exploit_kinetics],
        output_key=agent_cfg.get("output_key", "exploit_kinetics_analysis"),
        before_model_callback=print_agent_prompt,
    )


def build_sector_geo_context_agent(agent_cfg: Dict[str, Any]) -> Agent:
    model = create_model(agent_cfg["model"])
    return Agent(
        name=agent_cfg["name"],
        model=model,
        description=agent_cfg["description"],
        instruction=agent_cfg["instruction"],
        tools=[assess_context_realism],
        output_key=agent_cfg.get("output_key", "sector_geo_context_analysis"),
        before_model_callback=print_agent_prompt,
    )


def build_risk_cost_impact_agent(agent_cfg: Dict[str, Any]) -> Agent:
    model = create_model(agent_cfg["model"])
    return Agent(
        name=agent_cfg["name"],
        model=model,
        description=agent_cfg["description"],
        instruction=agent_cfg["instruction"],
        tools=[estimate_risk_and_cost],
        output_key=agent_cfg.get("output_key", "risk_cost_impact_summary"),
        before_model_callback=print_agent_prompt,
    )


def build_synthesis_report_agent(agent_cfg: Dict[str, Any]) -> Agent:
    model = create_model(agent_cfg["model"])
    return Agent(
        name=agent_cfg["name"],
        model=model,
        description=agent_cfg["description"],
        instruction=agent_cfg["instruction"],
        # No specific tools needed for synthesis, it uses the state
        output_key=agent_cfg.get("output_key", "final_report"),
        before_model_callback=print_agent_prompt,
    )


def build_cyber_forecast_review_team() -> SequentialAgent:
    """
    구조:
      1. Forecast Interpreter (CSV 해석)
      2. Parallel Analysis (5개 관점 동시 분석)
      3. Synthesis Report (최종 종합)
    """
    config = get_config()
    agents_cfg = config["agents"]

    # 1. Interpreter
    interpreter = build_forecast_interpreter_agent(agents_cfg["forecast_interpreter"])

    # 2. Parallel Analysts
    attacker = build_attacker_feasibility_agent(agents_cfg["attacker_feasibility"])
    defender = build_defensive_readiness_agent(agents_cfg["defensive_readiness"])
    kinetics = build_exploit_kinetics_agent(agents_cfg["exploit_kinetics"])
    context = build_sector_geo_context_agent(agents_cfg["sector_geo_context"])
    risk_cost = build_risk_cost_impact_agent(agents_cfg["risk_cost_impact"])

    parallel_analysts = ParallelAgent(
        name="parallel_analysts_group",
        sub_agents=[attacker, defender, kinetics, context, risk_cost],
        description="5개의 전문 에이전트가 병렬적으로 위협을 분석합니다."
    )

    # 3. Synthesis
    synthesis = build_synthesis_report_agent(agents_cfg["synthesis_report"])

    # Root Sequential Pipeline
    root = SequentialAgent(
        name="cyber_forecast_review_team_root",
        sub_agents=[interpreter, parallel_analysts, synthesis],
    )
    return root
