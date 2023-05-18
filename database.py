from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

with open('settings_database.txt', 'r', encoding='UTF-8') as read_set:

    text = read_set.readlines()

    used = text[0].split(':')[1].strip()
    password = text[1].split(':')[1].strip()
    host = text[2].split(':')[1].strip()
    port = text[3].split(':')[1].strip()
    name_BD = text[4].split(':')[1].strip()


engine = create_engine(f'postgresql://{used}:{password}{host}:{port}/{name_BD}',
                       echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)