from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings are loaded from the following sources, in order of precedence:
    1. Environment variables.
    2. .env file.
    3. Secrets directory, if set (e.g., /mnt/secret-store).
    4. Default values defined in this class.
    """

    PROJECT_NAME: str = "app"
    VERSION: str = "0.0.1"
    DESCRIPTION: str = ""

    # OpenTelemetry settings
    # Handles "enabled"/"disabled" via alias if needed, or True/False
    OTEL_ENABLED: bool = Field(False, alias="OTEL_ENABLED")
    OTEL_PROVIDER: str = "azure"
    APPLICATIONINSIGHTS_CONNECTION_STRING: str | None = None

    POSTGRES_HOST: str = Field("localhost", alias="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(5432, alias="POSTGRES_PORT")
    POSTGRES_DB: str = Field("postgres", alias="POSTGRES_DB")
    POSTGRES_USER: str = Field("postgres", alias="POSTGRES_DB_USERNAME")
    POSTGRES_PASSWORD: str = Field("", alias="POSTGRES_DB_PASSWORD")
    ENVIRONMENT: str = "development"

    @model_validator(mode="after")
    def check_azure_conn_str(self) -> "Settings":
        """
        Validate if OTEL_ENABLED is True and provider is azure -
        the Azure conn string must be set
        """
        if self.OTEL_ENABLED and self.OTEL_PROVIDER == "azure":
            if not self.APPLICATIONINSIGHTS_CONNECTION_STRING:
                raise ValueError(
                    "APPLICATIONINSIGHTS_CONNECTION_STRING must be set when OTEL_ENABLED is true and OTEL_PROVIDER is 'azure'"
                )
        return self

    model_config = SettingsConfigDict(
        env_file=[".env", ".env.local"],
        env_file_encoding="utf-8",
        # Directory for secrets
        # Pydantic will look for a file with the same name as the setting key
        secrets_dir="/mnt/secret-store",
        extra="ignore",  # Ignore extra fields from sources
    )
