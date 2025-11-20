# app/tools.py
from typing import Dict, Any


def _score_level(level: str) -> int:
    mapping = {"Low": 1, "Medium": 2, "High": 3}
    return mapping.get(level, 2)


def _level_from_score(score: int) -> str:
    if score <= 2:
        return "Low"
    elif score <= 5:
        return "Medium"
    return "High"


def assess_attacker_feasibility(
    attack_complexity: str,
    required_capability: str,
    operational_risk: str,
) -> Dict[str, Any]:
    """공격자 실현 가능성(Attacker Feasibility)을 정성적으로 점수화한다.

    이 도구는 MITRE ATT&CK, CAPEC, APT 보고서, PoC 타임라인 등의
    정보를 '참고해서 LLM이 평가했다'는 전제를 두고,
    LLM이 설정한 수준(High/Medium/Low)을 수치화하여 정리하는 역할만 한다.

    Args:
        attack_complexity (str): 공격 절차의 복잡도 (High/Medium/Low).
        required_capability (str): 공격자가 가져야 하는 기술/인프라 수준 (High/Medium/Low).
        operational_risk (str): 공격 수행 시 공격자가 감수해야 할 리스크 (High/Medium/Low).

    Returns:
        dict: 공격 실현 가능성 레벨 및 내부 스코어.
    """
    print("--- Tool: assess_attacker_feasibility called ---")

    c = _score_level(attack_complexity)
    r = _score_level(required_capability)
    o = _score_level(operational_risk)

    # 복잡도는 높을수록(High=3) feasibility를 낮추는 방향,
    # capability/operational_risk는 높을수록 공격자에게 불리하다고 보고 단순 가중치
    feasibility_score = (4 - c) + (4 - r) + (4 - o)
    feasibility_level = _level_from_score(feasibility_score)

    return {
        "status": "success",
        "feasibility_level": feasibility_level,
        "internal_score": feasibility_score,
        "note": "이 평가는 개념적 지표이며, 실제 위협 인텔리전스를 대체하지 않습니다.",
    }


def assess_defensive_readiness(
    detection_coverage: str,
    response_maturity: str,
    patch_latency: str,
) -> Dict[str, Any]:
    """방어자 대비 수준(Defensive Readiness)을 정성적으로 점수화한다.

    Args:
        detection_coverage (str): 주요 위협에 대한 탐지 커버리지 수준 (High/Medium/Low).
        response_maturity (str): IR/DFIR 프로세스 성숙도 (High/Medium/Low).
        patch_latency (str): 보안 패치 반영 지연 정도 (High/Medium/Low).

    Returns:
        dict: readiness 레벨 및 내부 스코어.
    """
    print("--- Tool: assess_defensive_readiness called ---")

    d = _score_level(detection_coverage)
    r = _score_level(response_maturity)
    p = _score_level(patch_latency)

    # 커버리지/성숙도는 높을수록 좋고, patch_latency는 높을수록 나쁨.
    readiness_score = d + r + (4 - p)
    readiness_level = _level_from_score(readiness_score)

    return {
        "status": "success",
        "readiness_level": readiness_level,
        "internal_score": readiness_score,
        "note": "조직의 평균적인 보안 성숙도를 전제로 한 개념적 평가입니다.",
    }


def assess_exploit_kinetics(
    time_to_poc_months: int,
    time_to_mass_exploit_months: int,
    vendor_patch_speed_months: int,
) -> Dict[str, Any]:
    """취약점 활용 속도(Exploit Kinetics)의 시간적 타당성을 정성적으로 점수화한다.

    Args:
        time_to_poc_months (int): CVE 공개 후 PoC가 등장하기까지의 기간(개월 단위 개념값).
        time_to_mass_exploit_months (int): PoC 이후 대규모 악용까지의 기간(개월 단위 개념값).
        vendor_patch_speed_months (int): 벤더가 패치를 제공하는 데 걸리는 기간(개월 단위 개념값).

    Returns:
        dict: kinetics 타당성 레벨 및 내부 스코어.
    """
    print("--- Tool: assess_exploit_kinetics called ---")

    # 단순히 '너무 짧거나 긴' 값에 페널티를 주는 개념적 로직
    def _penalty(x: int, ideal_min: int, ideal_max: int) -> int:
        if ideal_min <= x <= ideal_max:
            return 0
        return abs(ideal_min - x) + abs(x - ideal_max)

    penalty = 0
    penalty += _penalty(time_to_poc_months, 0, 12)
    penalty += _penalty(time_to_mass_exploit_months, 1, 24)
    penalty += _penalty(vendor_patch_speed_months, 0, 12)

    base_score = 9  # 최대 9점에서 페널티 차감
    score = max(1, base_score - penalty)
    level = _level_from_score(score)

    return {
        "status": "success",
        "kinetics_level": level,
        "internal_score": score,
        "note": "실제 통계가 아닌, 예측된 타임라인의 '현실감'을 대략적으로 평가한 개념적 지표입니다.",
    }


def assess_context_realism(
    sector_criticality: str,
    geo_tension_level: str,
    regulation_pressure: str,
) -> Dict[str, Any]:
    """산업/지리적 맥락(Context Realism)을 정성적으로 점수화한다.

    Args:
        sector_criticality (str): 산업 중요도(예: 금융, 에너지 등) (High/Medium/Low).
        geo_tension_level (str): 해당 지역의 지정학적 긴장 수준 (High/Medium/Low).
        regulation_pressure (str): 규제/컴플라이언스 압력 수준 (High/Medium/Low).

    Returns:
        dict: context realism 레벨 및 내부 스코어.
    """
    print("--- Tool: assess_context_realism called ---")

    s = _score_level(sector_criticality)
    g = _score_level(geo_tension_level)
    r = _score_level(regulation_pressure)

    # 중요 산업 + 높은 지정학적 긴장 + 규제 강도 -> 맥락상 공격/방어 모두 활성화될 가능성 높음.
    score = s + g + r
    level = _level_from_score(score)

    return {
        "status": "success",
        "context_realism_level": level,
        "internal_score": score,
        "note": "DBIR/ISAC/CERT를 참고한 것처럼, 산업/지역 맥락의 현실성을 개념적으로 평가한 지표입니다.",
    }


def estimate_risk_and_cost(
    impact_level: str,
    likelihood_level: str,
    mitigation_complexity: str,
) -> Dict[str, Any]:
    """리스크 및 비용 수준을 정성적으로 점수화한다.

    FAIR/ROSI 사고 방식과 사이버 보험 손실 데이터를 '참고했다'는 전제하에,
    LLM이 설정한 영향도/발생 가능성/대응 복잡도를 수치화하여 요약한다.

    Args:
        impact_level (str): 비즈니스 영향도 (High/Medium/Low).
        likelihood_level (str): 발생 가능성 (High/Medium/Low).
        mitigation_complexity (str): 완화 조치의 복잡도 (High/Medium/Low).

    Returns:
        dict: risk_level, estimated_cost_level, internal_score, note.
    """
    print("--- Tool: estimate_risk_and_cost called ---")

    impact = _score_level(impact_level)
    likelihood = _score_level(likelihood_level)
    complexity = _score_level(mitigation_complexity)

    risk_score = impact * likelihood
    cost_score = impact + complexity

    return {
        "status": "success",
        "risk_level": _level_from_score(risk_score),
        "estimated_cost_level": _level_from_score(cost_score),
        "internal_risk_score": risk_score,
        "internal_cost_score": cost_score,
        "note": "실제 재무 모델이 아닌, 리스크/비용을 비교하기 위한 개념적 정성 지표입니다.",
    }
