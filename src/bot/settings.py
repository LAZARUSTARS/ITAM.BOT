from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Класс настроек приложения.
    
    Загружает настройки из переменных окружения и .env файла.
    
    Attributes:
        bot_token: Токен Telegram бота
        bot_name: Имя бота
        use_webhook: Использовать ли webhook вместо long polling
        postgres_host: Хост базы данных PostgreSQL
        postgres_db: Имя базы данных
        postgres_password: Пароль базы данных
        postgres_port: Порт базы данных (по умолчанию 5432)
        postgres_user: Пользователь базы данных
        redis_host: Хост Redis
        redis_port: Порт Redis (по умолчанию 6379)
        secret: Секретный ключ для шифрования
    """
    
    model_config = SettingsConfigDict(env_file_encoding="utf-8", env_file=".env")

    bot_token: SecretStr
    bot_name: str
    use_webhook: bool = False

    postgres_host: str
    postgres_db: str
    postgres_password: str
    postgres_port: int = 5432
    postgres_user: str
    redis_host: str
    redis_port: int = 6379

    secret: str
    # redis_host: str
    # redis_port: int
    # redis_database: int

    def build_postgres_dsn(self) -> str:
        """
        Создает строку подключения к PostgreSQL.
        
        Returns:
            str: Строка подключения в формате postgresql://user:password@host:port/dbname
        """
        return (
            "postgresql://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
        
    def redis_dsn(self) -> str:
        """
        Создает строку подключения к Redis.
        
        Returns:
            str: Строка подключения в формате redis://host:port/0
        """
        return f"redis://{self.redis_host}:{self.redis_port}/0"
