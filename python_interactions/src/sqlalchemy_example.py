import logging
import os

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Float, MetaData
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Формируем подключение к Postgres через SQLAlchemy")
# создаём движок для работы с данными
engine = create_engine('postgresql://postgres:@{}:{}'.format(
    os.environ['APP_POSTGRES_HOST'], os.environ['APP_POSTGRES_PORT']))

# создаём пустую таблицу
metadata = MetaData()
ui_table = Table(
    'ui_interactions', metadata,
    Column('user', Integer, primary_key=True),
    Column('item', Integer, primary_key=True),
    Column('rating', Float)
)

# проверка на существование таблицы - уже внутри
metadata.create_all(engine)


class UITriplet(object):
    """
        Интеракция контента с пользователем

        Содержит триплеты пользователь-контент-рейтинг
    """
    def __init__(self, user, item, rating):
        self.user = user
        self.item = item
        self.rating = rating

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.user, self.item, self.rating)


# ассоциируем объект Python с таблицей Postgres
mapper(UITriplet, ui_table)

# создаём вспомогательный объект для работы с таблицей
Session = sessionmaker(bind=engine)
session = Session()

# читаем построчно файл и формируем из каждой строчки триплет
agg_filename = '/home/user_agg.tsv'
ui_data = []
with open(agg_filename, 'r') as f:
    for line in f.readlines():
        line = line.strip().split('\t')
        ui_data.append(
            UITriplet(line[0], line[1], line[2])
        )

session.add_all(ui_data)
session.commit()

logger.info("{} записей загружены в Postgres".format(len(ui_data)))
