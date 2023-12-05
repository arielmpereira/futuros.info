from sqlalchemy import Integer, Text, String, BLOB, REAL, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Base(DeclarativeBase):  # Subclase de DeclarativeBase
    pass

db = SQLAlchemy(model_class=Base)

class Paginas(db.Model):
    __tablename__ = 'paginas'
    pagina_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contenido: Mapped[str] = mapped_column(Text)



class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<User {}>'.format(self.email)

    @staticmethod
    def get_by_id(id):
        return Users.query.get(id)

    @staticmethod
    def get_by_email(email):
        return Users.query.filter_by(email=email).first()

