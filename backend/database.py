import os

from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def conectar_banco(app):

    usuario = os.getenv('DB_USER')
    senha = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    porta = os.getenv('DB_PORT')
    nome_banco = os.getenv('DB_NAME')

    app.config['SQLALCHEMY_DATABASE_URI'] = (f'postgresql://{usuario}:{senha}@{host}:{porta}/{nome_banco}')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)