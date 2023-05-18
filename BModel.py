from pydantic import BaseModel

class Settings(BaseModel):
    authjwt_secret_key:str = 'bfb9f79f923c4488d4c05302163a88b0d4229ea71f822b0436ce412d35e178b0'


class UseRegiste(BaseModel):
    login: str
    password: str
    email: str

    class Config:
        orm_mode = True

class UseLogin(BaseModel):
    login: str
    password: str

    class Config:
        orm_mode = True

class UseWork(BaseModel):
    login: str
    has_login: str

    class Config:
        orm_mode = True

class UserCreateTask(BaseModel):
    login: str
    text: str
    has_login: str

    class Config:
        orm_mode = True

class TextRecorde(BaseModel):
    text: str

class RacordsText(BaseModel):
    id: int
    autor_rec: int
    text: str

    class Config:
        orm_mode = True

class Users(BaseModel):
    id: int
    login: str
    password: str
    email: str
    is_active: bool
    has_login: str = ''

    class Config:
        orm_mode=True
