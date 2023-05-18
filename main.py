from fastapi import FastAPI, status, HTTPException, Depends
from BModel import UseRegiste, Settings, UseLogin, UserCreateTask, UseWork, RacordsText, Users as BU, TextRecorde
from database import SessionLocal
from models import Users, Records
from fastapi_jwt_auth import AuthJWT
from typing import List

app = FastAPI()

db = SessionLocal()


@AuthJWT.load_config
def get_config():
    return Settings()


@app.get('/')
def index():
    return {'hello': 'Hello'}

@app.get('/all_users', response_model=List[BU])
def all_users():
    all_users = db.query(Users).all()
    return all_users

@app.get('/all_recors', response_model=List[RacordsText])
def all_users():
    all_users = db.query(Records).all()#
    return all_users


@app.post('/register', response_model=UseRegiste, status_code= status.HTTP_200_OK)
def register_new_user(user:UseRegiste):
    '''
    Функция обрабатывает запрос на url /register регистрирует пользователя в базе данных
    :param user: Объект pydantic представляющий JSON формат
    :return: Возвращает сохраненные данные пользователя new_user в виде объекта UseRegiste, лобо ошибку HTTPException
    '''
    new_user = db.query(Users).filter(Users.login == user.login).first()
    if new_user:
        raise HTTPException(status_code=400, detail="Такой логин сушествует")

    try:
        new_user = Users(login=user.login, password=user.password,
                         email=user.email)
    except:
        raise HTTPException(status_code=400, detail="Ошибка при сохранении данных")
    else:
        db.add(new_user)
        db.commit()
    return new_user


@app.post('/login', status_code=status.HTTP_200_OK)
def login_user(user: UseLogin, Authorize: AuthJWT=Depends()):
    '''
    Функция обрабаотывает запрос на url /login проводит Аутентификацию пользователя
    :param user: Объект pydantic представляющий JSON формат
    :param Authorize: Объект fastapi-jwt-auth представляющий хэшированный токен доступа
    :return: Возвращает токен доступа access_token либо ошибку HTTPException
    '''

    log_user = db.query(Users).filter(Users.login == user.login).first()

    if (not log_user) or (log_user.password != user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не правильный логин или пароль')

    elif log_user.password == user.password:
        if log_user.is_active == True:
            raise HTTPException(status_code=400, detail="Вы уже залогинены")
        else:
            try:
                access_token = Authorize.create_access_token(subject=log_user.login)
                log_user.has_login = access_token
                log_user.is_active = True
            except:
                raise HTTPException(status_code=400, detail="Ошибка при сохранении данных")
            else:
                db.commit()
            return {'access_token': access_token, }


@app.post('/logout', status_code=status.HTTP_200_OK)
def log_out(user: UseWork):
    '''
    Функция обрабаотывает запрос на url /logout проводит выход пользователя из системы
    :param user: Объект pydantic представляющий JSON формат
    :return: Возвращает успешный результат выхода из системы, либо ошибку HTTPException
    '''
    log_user = db.query(Users).filter(Users.login == user.login).first()
    if not log_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Вы ввели неверные данные для выхода.')

    # elif log_user.is_active == False:
    #     return {'exit': 'Вы не авторизированный пользователь'}

    elif (user.has_login == log_user.has_login) and log_user.is_active == True:
        log_user.has_login = ''
        log_user.is_active = False
        db.commit()
        return {'exit': 'Вы успешно вышли'}

    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Вы не залогинены.')


@app.post('/tasks', status_code=status.HTTP_200_OK)
def create_task(user: UserCreateTask):
    '''
    Функция обрабаотывает запрос на url /tasks авторизированный пользователь создает новую запись
    :param user: Объект pydantic представляющий JSON формат
    :return: Возвращает успешный результат создания новой записи, либо ошибку HTTPException
    '''
    log_user = db.query(Users).filter(Users.login == user.login).first()
    if not log_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Вы ввели неверные данные для запроса.')

    elif user.has_login == log_user.has_login and log_user.is_active == True:
        try:
            new_task = Records(autor_rec=log_user.id, text=user.text)
        except:
            raise HTTPException(status_code=400, detail="Ошибка при сохранении данных")
        else:
            db.add(new_task)
            db.commit()
            return {'create text': 'Вы успешно добавили запись.'}

    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Вы не залогинены.')

@app.get('/tasks', response_model=List[RacordsText], status_code=status.HTTP_200_OK) #
def all_task(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Вы не авторизированы, зайдите в систему'
                                   'для того чтобы воспользоваться данным запросом')
    try:
        user = Authorize.get_jwt_subject()
        autor = db.query(Users).filter(Users.login == user).first()
        records = db.query(Records).filter(Records.autor_rec == autor.id).all()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Ошибка при выводе данных')
    else:
        return records

@app.get('/tasks/{task}', response_model=RacordsText, status_code=status.HTTP_200_OK)
def get_task(task: int, Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Вы не авторизированы, зайдите в систему'
                                   'для того чтобы воспользоваться данным запросом')
    try:
        user = Authorize.get_jwt_subject()
        autor = db.query(Users).filter(Users.login == user).first()
        records = db.query(Records).filter(Records.autor_rec == autor.id, Records.id == task).one()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Ошибка при выводе данных')
    else:
        return records

@app.put('/tasks/{task}', response_model=RacordsText, status_code=status.HTTP_200_OK)
def update_task(task: int, text: TextRecorde, Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Вы не авторизированы, зайдите в систему'
                                   'для того чтобы воспользоваться данным запросом')
    try:
        user = Authorize.get_jwt_subject()
        autor = db.query(Users).filter(Users.login == user).first()
        update_record = db.query(Records).filter(Records.autor_rec == autor.id, Records.id == task).one()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Ошибка при поиске данных')
    try:
        print(text.text)
        update_record.text = text.text
        print(update_record.text)
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Ошибка при записи данных')
    else:
        db.commit()

    record = db.query(Records).filter(Records.autor_rec == autor.id, Records.id == task).one()

    return record

@app.delete('/tasks/{task}', response_model=RacordsText, status_code=status.HTTP_200_OK)
def del_task(task:int, Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Вы не авторизированы, зайдите в систему'
                                   'для того чтобы воспользоваться данным запросом')
    try:
        user = Authorize.get_jwt_subject()
        autor = db.query(Users).filter(Users.login == user).first()
        del_record = db.query(Records).filter(Records.autor_rec == autor.id, Records.id == task).one()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Ошибка при поиске данных')
    try:
        db.delete(del_record)
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Ошибка при удалении данных')
    else:
        db.commit()

    return del_record