# backend/agendaBack/config.py

from datetime import timedelta

class Config:
    # En desarrollo usamos la base local
    if __import__('os').getenv("FLASK_ENV") == "development":
        SQLALCHEMY_DATABASE_URI = "postgresql://postgres:supergary1971@localhost:5432/ventas_db"
    else:
        # Conexión fija a Supabase (solo para pruebas)
        SQLALCHEMY_DATABASE_URI = (
            "postgresql://postgres.bjyswhntsamaolnxlmzq:Supergary2002"
            "@aws-0-us-east-2.pooler.supabase.com:5432/postgres"
            "?sslmode=require"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Clave JWT fija para pruebas
    JWT_SECRET_KEY = "cambiaEstaClave"

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
