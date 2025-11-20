# SWU Cyber Security Agents

This project implements a multi-agent system for reviewing cyber threat forecasts.

## Configuration

The application is configured via `config.yaml`.

### App Settings
You can configure the application ID, User ID, and Session ID in the `app` section:

```yaml
app:
  name: "cyber_threat_forecast_review_app"
  app_id: "ctf_review_001"
  user_id: "demo_user_1"       # User ID for the session
  session_id: "cyber_forecast_session_001" # Session ID
```

### Models and Agents
Models and agent behaviors are also configured in `config.yaml`.

## Running the Application

1. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

2. Run the main script:
   ```bash
   uv python main.py
   ```

