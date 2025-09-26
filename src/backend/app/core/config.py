import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables desde el archivo .env

class Settings:
    PROJECT_NAME: str = "Public Transit Agency"
    # Corrige: quita espacios y comillas extras si hay en la variable de entorno
    ALLOWED_ORIGINS: list = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")]

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    HOST: str = os.getenv("HOST")
    PORT: str = os.getenv("PORT")
    DB: str = os.getenv("DB")
    PASSWORD: str = os.getenv("PASSWORD")
    USER: str = os.getenv("USER")

    @property
    def db_config(self) -> dict:
        # Devuelve un diccionario con la configuración de la base de datos
        return {
            "host": self.HOST,
            "port": self.PORT,
            "dbname": self.DB,
            "user": self.USER,
            "password": self.PASSWORD,
        }

settings = Settings()