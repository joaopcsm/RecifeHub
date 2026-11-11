import os
from flask import Flask, jsonify
from sqlalchemy import text
from flask import request
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from flask import session
from werkzeug.security import check_password_hash
from database import db, conectar_banco
from models import Usuario


app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

CORS(app, origins=[
    "http://127.0.0.1:5500",
    "http://localhost:5500"
], supports_credentials=True)

conectar_banco(app)


@app.route("/testar-conexao")
def testar_conexao():
    try:
        with db.engine.connect() as conexao:
            conexao.execute(text("SELECT 1"))

        return jsonify({
            "mensagem": "Conexão com PostgreSQL realizada com sucesso!"
        })

    except Exception:
        app.logger.exception("Erro ao conectar ao banco")

        return jsonify({
            "erro": "Não foi possível conectar ao banco."
        }), 500


@app.route("/testar-usuarios")
def testar_usuarios():
    try:
        quantidade = Usuario.query.count()

        return jsonify({
            "mensagem": "Consulta realizada com sucesso!",
            "total_usuarios": quantidade
        })

    except Exception:
        app.logger.exception("Erro ao consultar usuarios")

        return jsonify({
            "erro": "Não foi possível consultar os usuários."
        }), 500

@app.route("/api/cadastro", methods=["POST"])
def cadastrar_usuario():

    dados = request.get_json()

    nome_completo = dados.get("nome_completo", "").strip()
    nome_usuario = dados.get("nome_usuario", "").strip()
    email = dados.get("email", "").strip().lower()
    senha = dados.get("senha", "")
    tipo_usuario = dados.get("tipo_usuario", "")

    # Verifica se todos os campos foram preenchidos
    if not all([nome_completo, nome_usuario, email, senha, tipo_usuario]):
        return jsonify({"erro": "Preencha todos os campos."}), 400

    if len(senha) < 6:
        return jsonify({"erro": "A senha deve ter pelo menos 6 caracteres."}), 400

    tipos_validos = ["pessoa", "estudante", "pesquisador", "instituicao"]

    if tipo_usuario not in tipos_validos:
        return jsonify({"erro": "Tipo de usuário inválido."}), 400

    # Verifica se o usuário ou email já existem
    existente = Usuario.query.filter(
        (Usuario.email == email) |
        (Usuario.nome_usuario == nome_usuario)
    ).first()

    if existente:
        return jsonify({
            "erro": "E-mail ou nome de usuário já cadastrado."
        }), 409

    # Protege a senha utilizando hash
    senha_hash = generate_password_hash(senha)

    novo_usuario = Usuario(
        nome_completo=nome_completo,
        nome_usuario=nome_usuario,
        email=email,
        senha=senha_hash,
        tipo_usuario=tipo_usuario
    )

    try:
        db.session.add(novo_usuario)
        db.session.commit()

        return jsonify({
            "mensagem": "Usuário cadastrado com sucesso!"
        }), 201

    except Exception:
        db.session.rollback()
        app.logger.exception("Erro ao cadastrar usuário")

        return jsonify({
            "erro": "Erro interno ao cadastrar usuário."
        }), 500

@app.route("/api/login", methods=["POST"])
def login():

    dados = request.get_json()

    email = dados.get("email", "").strip().lower()
    senha = dados.get("senha", "")

    if not email or not senha:
        return jsonify({
            "erro": "Informe o e-mail e a senha."
        }), 400

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario is None or not check_password_hash(usuario.senha, senha):
        return jsonify({
            "erro": "E-mail ou senha incorretos."
        }), 401

    session.clear()
    session["usuario_id"] = usuario.id

    return jsonify({
        "mensagem": "Login realizado com sucesso!",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome_completo,
            "tipo": usuario.tipo_usuario
        }
    }), 200

@app.route("/api/sessao", methods=["GET"])
def verificar_sessao():

    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return jsonify({
            "autenticado": False,
            "mensagem": "Usuário não está autenticado."
        }), 401

    usuario = db.session.get(Usuario, usuario_id)

    if usuario is None:
        session.clear()

        return jsonify({
            "autenticado": False,
            "mensagem": "Usuário não encontrado."
        }), 401

    return jsonify({
        "autenticado": True,
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome_completo,
            "email": usuario.email,
            "tipo": usuario.tipo_usuario
        }
    }), 200


if __name__ == "__main__":
    app.run(debug=True)