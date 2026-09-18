# Application configuration and environment variable management using Pydantic Settings.
#this application configures the application
import json
import os
from pathlib import Path
from typing import Any, List, Union
from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT_ENV = Path(__file__).resolve().parent.parent / ".env"
_BACKEND_ENV = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ROOT_ENV)
load_dotenv(dotenv_path=_BACKEND_ENV)


class Settings(BaseSettings):
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0" if os.getenv("PORT") else "127.0.0.1")
    backend_port: int = int(os.getenv("PORT", os.getenv("BACKEND_PORT", "8000")))
    github_token: str = ""
    github_api_url: str = "https://api.github.com"
    git_committer_name: str = "flux-bot"
    git_committer_email: str = "bot@flux.dev"
    git_clone_timeout: int = 120
    gemini_api_key: str = ""
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    max_diff_lines_for_pr: int = 150
    max_files_touched_for_pr: int = 4
    opencode_cli_cmd: str = "opencode"
    opencode_model: str = ""
    opencode_timeout: int = 120
    demo_mode: bool = False
    workspaces_dir: Path = Path(os.getenv("WORKSPACES_DIR", str(Path(__file__).resolve().parent.parent / "workspaces")))
    database_path: Path = Path(os.getenv("DATABASE_PATH", str(Path(__file__).resolve().parent / "flux.db")))
    cors_origins: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    http_timeout: float = 10.0
    user_agent: str = "flux-app/1.0"
    max_preview_lines: int = 600
    max_preview_bytes: int = 64 * 1024
    max_read_chars: int = 100_000

    # Normalizes CORS origins from comma-separated string, wildcard, or JSON array.
    @field_validator("cors_origins", mode="after")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if v == "*":
                return ["*"]
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Resolves the Gemini API key from settings or environment.
    @property
    def effective_api_key(self) -> str:
        key = self.gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        return key.strip().strip("\"'")

    # Resolves the effective Gemini model name with fallback.
    @property
    def effective_model(self) -> str:
        model = self.gemini_model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        return model.strip().strip("\"'")

    model_config = SettingsConfigDict(
        env_file=(str(_ROOT_ENV), str(_BACKEND_ENV), ".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
settings.workspaces_dir.mkdir(parents=True, exist_ok=True)
if settings.effective_model:
    os.environ["GEMINI_MODEL"] = settings.effective_model
if settings.effective_api_key:
    os.environ["GEMINI_API_KEY"] = settings.effective_api_key
