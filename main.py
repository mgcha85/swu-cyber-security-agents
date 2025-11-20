# main.py
import asyncio

from app.settings import init_environment
from app.runner import run_demo


if __name__ == "__main__":
    try:
        # 환경 초기화(.env, config, 로깅 등)
        init_environment()
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("Interrupted by user.")
