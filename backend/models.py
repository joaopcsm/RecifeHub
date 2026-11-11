from database import db


# Tabela intermediária: projetos <-> empresas
projetos_empresas = db.Table(
    "projetos_empresas",

    db.Column(
        "projeto_id",
        db.Integer,
        db.ForeignKey("projetos.id"),
        primary_key=True
    ),

    db.Column(
        "empresa_id",
        db.Integer,
        db.ForeignKey("empresas.id"),
        primary_key=True
    )
)


# Tabela usuarios
class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(50), nullable=False)
    nome_completo = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    tipo_usuario = db.Column(db.String(30))

    projetos = db.relationship("Projeto", back_populates="usuario")


# Tabela projetos
class Projeto(db.Model):
    __tablename__ = "projetos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    fase_desenvolvimento = db.Column(db.String(30), nullable=False)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    usuario = db.relationship("Usuario", back_populates="projetos")

    empresas = db.relationship(
        "Empresa",
        secondary=projetos_empresas,
        back_populates="projetos"
    )


# Tabela empresas
class Empresa(db.Model):
    __tablename__ = "empresas"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    cnpj = db.Column(db.String(18), unique=True)
    email = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text)

    projetos = db.relationship(
        "Projeto",
        secondary=projetos_empresas,
        back_populates="empresas"
    )