from sqlalchemy import Column, Integer, ForeignKey, Text, String, Boolean
from database import Base

class Records(Base):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True)
    autor_rec = Column(Integer, ForeignKey('users.id'))
    text = Column(Text)

    def __int__(self, autor_rec, text):
        self.autor_rec = autor_rec
        self.text = text

    def __repr__(self):
        return f'Запись {self.text} сделана вытором {self.autor_rec.login}'

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True,)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), default='')
    is_active = Column(Boolean, default=False)
    has_login = Column(Text, default='')

    def __int__(self, login, password, email):
        self.login = login
        self.password = password
        self.email = email

    def __repr__(self):
        return f'Пользователь {self.login}, сейчас в сети {self.is_active}?'
