from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Azure OpenAI
    azure_openai_endpoint: str = "https://startuperbyaries.services.ai.azure.com/openai/v1"
    azure_openai_key: str = ""
    azure_openai_model: str = "gpt-5.6-sol"

    # Weather (optional)
    openweather_api_key: str = ""

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # Speech recognition language.
    # en-IN is trained on Hinglish and maps English sounds onto Hindi words
    # ("aur", "Nau"), so we use a pure-English model instead.
    # Try en-GB as an alternative: Indian English is closer to British English.
    speech_language: str = "en-US"

    # Azure gpt-4o-transcribe. Far more accurate than Twilio's recogniser on
    # accented phone audio, at the cost of a recording round trip.
    stt_endpoint: str = ""
    stt_key: str = ""
    # When true, record the caller and transcribe with Azure instead of
    # relying on Twilio's built-in speech recognition.
    use_azure_stt: bool = True

    # Text the answer to the farmer as well as speaking it
    send_sms_answer: bool = True

    @property
    def azure_stt_enabled(self) -> bool:
        return bool(self.use_azure_stt and self.stt_endpoint and self.stt_key)

    @property
    def sms_enabled(self) -> bool:
        return bool(self.send_sms_answer and self.twilio_enabled
                    and self.twilio_phone_number)

    # RAG docs path
    rag_docs_path: str = "./data/docs"

    # Base URL for webhooks (ngrok during dev)
    base_url: str = "http://localhost:8000"

    # Hardcoded location (Alappuzha, Kerala)
    default_lat: float = 9.4981
    default_lng: float = 76.3388
    default_location_name: str = "Alappuzha"

    @property
    def weather_enabled(self) -> bool:
        return bool(self.openweather_api_key)

    @property
    def twilio_enabled(self) -> bool:
        return bool(self.twilio_account_sid and self.twilio_auth_token)


settings = Settings()
