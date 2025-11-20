# app/settings.py
import os
import warnings
import logging
from typing import Dict, Any, Optional

import yaml
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

_config: Optional[Dict[str, Any]] = None
APP_NAME: Optional[str] = None
APP_ID: Optional[str] = None
USER_ID: Optional[str] = None
SESSION_ID: Optional[str] = None


def init_environment(config_path: str = "config.yaml") -> None:
    """환경 변수(.env), 로그, ADK 관련 공통 설정을 초기화한다."""
    global _config, APP_NAME, APP_ID

    # .env 로드
    load_dotenv()

    # 워닝/로그 설정
    warnings.filterwarnings("ignore")
    logging.basicConfig(level=logging.ERROR)

    # ADK가 Vertex 대신 직접 API 키를 사용하도록 설정
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

    # config.yaml 로드
    _config = load_config(config_path)
    APP_NAME = _config["app"]["name"]
    APP_ID = _config["app"].get("app_id", "ctf_review_001")
    global USER_ID, SESSION_ID
    USER_ID = _config["app"].get("user_id", "demo_user_1")
    SESSION_ID = _config["app"].get("session_id", "cyber_forecast_session_001")

    print(f"[settings] APP_NAME={APP_NAME}, APP_ID={APP_ID}, USER_ID={USER_ID}, SESSION_ID={SESSION_ID}")


def load_config(path: str = "config.yaml") -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_config() -> Dict[str, Any]:
    if _config is None:
        raise RuntimeError("config is not initialized. Call init_environment() first.")
    return _config


def get_app_name() -> str:
    if APP_NAME is None:
        raise RuntimeError("APP_NAME is not initialized. Call init_environment() first.")
    return APP_NAME


def get_app_id() -> str:
    if APP_ID is None:
        raise RuntimeError("APP_ID is not initialized. Call init_environment() first.")
    return APP_ID


def get_user_id() -> str:
    if USER_ID is None:
        raise RuntimeError("USER_ID is not initialized. Call init_environment() first.")
    return USER_ID


def get_session_id() -> str:
    if SESSION_ID is None:
        raise RuntimeError("SESSION_ID is not initialized. Call init_environment() first.")
    return SESSION_ID


def create_model(model_name: str):
    """
    ADK에서는:
      - Gemini 계열: 문자열 그대로 사용
      - 기타(OpenAI, Anthropic 등): LiteLlm(model="provider/model") 사용
    """
    if model_name.startswith("gemini"):
        return model_name
    return LiteLlm(model=model_name)
