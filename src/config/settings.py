"""Application configuration models."""

from pathlib import Path

from pydantic import BaseModel, Field, PositiveInt, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent


class RunConfig(BaseModel):
    """Runtime server configuration."""

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "DEBUG"
    file: str | None = None
    retention_days: int = 30
    sa_level: str = "WARNING"


class ApiConfig(BaseModel):
    """API configuration."""

    prefix: str = Field(default="/api/v1", description="Базовый префикс API (c версией)")
    default_limit: int = Field(default=20, ge=1, description="Дефолтный размер страницы для списков")
    max_limit: int = Field(default=200, ge=1, description="Жёсткий верхний предел размера страницы")


class CorsConfig(BaseModel):
    """CORS configuration."""

    enabled: bool = Field(default=False, description="Включить CORS-мидлвару")
    origins: list[str] = Field(default_factory=list, description="Список разрешённых Origin")


class DatabaseConfig(BaseModel):
    """Database configuration."""

    url: PostgresDsn = Field(
        description="Database connection URL",
    )
    echo: bool = Field(default=False)
    echo_pool: bool = Field(default=False)
    pool_size: int = Field(default=50)
    max_overflow: int = Field(default=10)
    use_pgbouncer: bool = Field(default=False)


class LdapGroupsConfig(BaseModel):
    """LDAP group configuration."""

    admin: str | None = Field(default=None, description="DN группы с правами администратора")
    editor: str | None = Field(default=None, description="DN группы с правами редактора")
    viewer: str | None = Field(default=None, description="DN группы с правами просмотра")


class LdapConfig(BaseModel):
    """LDAP connection configuration."""

    server_uri: str = Field(description="URI контроллера домена, например ldap://dc01:389")
    base_dn: str = Field(description="Базовый DN для запросов (DC=example,DC=loc)")
    domain: str = Field(description="Короткое имя домена (EXAMPLE)")
    service_user: str = Field(description="Логин сервисного пользователя (DOMAIN\\\\account)")
    service_pass: SecretStr = Field(description="Пароль сервисного пользователя")
    connect_timeout: float = Field(default=5.0, description="Таймаут установления соединения, сек")
    search_timeout: float = Field(default=5.0, description="Таймаут поиска, сек")
    groups: LdapGroupsConfig = Field(default_factory=LdapGroupsConfig)


class JwtConfig(BaseModel):
    """JWT configuration."""

    secret: SecretStr = Field(description="Секрет для подписи JWT")
    algorithm: str = Field(default="HS256", description="Алгоритм подписи JWT")
    access_token_ttl_hours: PositiveInt = Field(default=1, description="Время жизни access-токена, часы")
    refresh_token_ttl_days: PositiveInt = Field(default=30, description="Время жизни refresh-токена, дни")
    issuer: str | None = Field(default=None, description="Значение iss (опционально)")
    audience: str | None = Field(default=None, description="Значение aud (опционально)")


class DifyConfig(BaseModel):
    """Dify API integration configuration."""

    base_url: str = Field(
        default="https://api.dify.ai/v1",
        description="Base URL for Dify API",
    )
    kb_api_key: str = Field(
        default="",
        min_length=1,
        description="Knowledge base API key",
    )
    customer_segment_api_key: str = Field(
        default="",
        description="API key for the chat that classifies customers by name",
    )
    timeout_sec: int = Field(
        default=30,
        description="HTTP timeout for Dify requests in seconds",
    )


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env.template", PROJECT_ROOT / ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )

    run: RunConfig = RunConfig()
    log: LoggingConfig = LoggingConfig()
    api: ApiConfig = ApiConfig()
    cors: CorsConfig = CorsConfig()
    db: DatabaseConfig
    ldap: LdapConfig
    jwt: JwtConfig
    dify: DifyConfig = DifyConfig()


settings = Settings()  # type: ignore[call-arg]
