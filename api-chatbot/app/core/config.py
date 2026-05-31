from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    app_env: str
    database_url: str
    jwt_secret: SecretStr
    jwt_algorithm: str
    access_token_expire_minutes: int
    waha_base_url: str
    waha_api_key: SecretStr
    midtrans_server_key: SecretStr
    midtrans_client_key: SecretStr
    midtrans_is_production: bool
    biteship_api_key: SecretStr
    biteship_couriers: str
    biteship_expanded_couriers: str
    biteship_on_demand_couriers: str
    biteship_base_url: str
    biteship_user_agent: str
    biteship_timeout_seconds: int
    ai_provider_api_key: SecretStr
    ollama_embedding_base_url: str
    ollama_embedding_model: str
    embedding_dimension: int
    ollama_llm_base_url: str
    ollama_llm_model: str
    waha_session: str
    waha_webhook_secret: SecretStr
    midtrans_webhook_server_key: SecretStr
    order_payment_expire_minutes: int
    cart_expire_minutes: int
    store_origin_area_id: str | None = None
    store_origin_postal_code: str
    store_origin_city: str
    store_address: str

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")

@lru_cache
def get_settings() -> Settings:
    return Settings()

