# app/agents.py
from typing import Dict, Any

from google.adk.agents import Agent, SequentialAgent

from .settings import get_config, create_model
from .tools import (
    assess_attacker_feasibility,
    assess_defensive_readiness,
    assess_exploit_kinetics,
    assess_context_realism,
    estimate_risk_and_cost,
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
    )


def build_cyber_forecast_review_team() -> SequentialAgent:
    """5개 관점 에이전트를 순차적으로 실행하는 루트 SequentialAgent 생성."""
    config = get_config()
    agents_cfg = config["agents"]

    attacker = build_attacker_feasibility_agent(agents_cfg["attacker_feasibility"])
    defender = build_defensive_readiness_agent(agents_cfg["defensive_readiness"])
    kinetics = build_exploit_kinetics_agent(agents_cfg["exploit_kinetics"])
    context = build_sector_geo_context_agent(agents_cfg["sector_geo_context"])
    risk_cost = build_risk_cost_impact_agent(agents_cfg["risk_cost_impact"])

    # 순서:
    #  1) 공격자 실현 가능성
    #  2) 방어자 대비 수준
    #  3) Exploit kinetics
    #  4) 산업/지리 맥락
    #  5) 리스크 & 비용 + 합의/불일치/설명
    root = SequentialAgent(
        name="cyber_forecast_review_team_root",
        sub_agents=[attacker, defender, kinetics, context, risk_cost],
    )
    return root
