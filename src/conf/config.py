from pydantic_settings import BaseSettings
from pydantic import ConfigDict, EmailStr


class Settings(BaseSettings):

    DB_URL: str     
    # jwt
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    REFRESH_TOKEN_EXPIRE_DAYS: int 
    ALGORITHM: str 
    SECRET_KEY: str 
    # redis
    REDIS_URL: str 
    # mail
    MAIL_USERNAME: EmailStr 
    MAIL_PASSWORD: str 
    MAIL_FROM: EmailStr
    MAIL_PORT: int 
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool 
    VALIDATE_CERTS: bool 
    # cloudinary
    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: int 
    CLOUDINARY_API_SECRET: str 

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
        )
   
settings = Settings()
