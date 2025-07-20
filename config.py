import os
from datetime import timedelta  # ✂ añade esto

class Config:
    # Si estamos en desarrollo, conectamos como superuser
    if os.getenv("FLASK_ENV") == "development":
        SQLALCHEMY_DATABASE_URI = "postgresql://postgres:supergary1971@localhost:5432/ventas_db"
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv(
            "DATABASE_URL",
            "postgresql://ventas_app:ventas123@localhost:5432/ventas_db"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "cambiaEstaClave")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
