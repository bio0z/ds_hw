import os
import logging

import psycopg2
import psycopg2.extensions
from pymongo import MongoClient
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Float, MetaData, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
	
# 1 часть Psycopg2 создание таблицы
logger.info('1 часть Psycopg2 создание таблицы')
	
# Задание по Psycopg2
# --------------------------------------------------------------

logger.info("Создаём подключёние к Postgres")
params = {
	"host": os.environ['APP_POSTGRES_HOST'],
	"port": os.environ['APP_POSTGRES_PORT'],
	"user": 'postgres'
}
conn = psycopg2.connect(**params)

# дополнительные настройки
psycopg2.extensions.register_type(
	psycopg2.extensions.UNICODE,
	conn
)
conn.set_isolation_level(
	psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
)
cursor = conn.cursor()

sql_str = "DROP TABLE IF EXISTS movies_top; SELECT *  INTO movies_top FROM (SELECT movieid, count(rating) as ratings_num, avg(rating) as ratings_avg FROM ratings GROUP BY movieid HAVING avg(rating)>3) as result;"

# -------------

cursor.execute(sql_str)
conn.commit()

# Проверка - выгружаем данные
cursor.execute("SELECT * FROM movies_top LIMIT 10")
logger.info(
	"Выгружаем данные из таблицы movies_top: (movieId, ratings_num, ratings_avg)\n{}".format(
		[i for i in cursor.fetchall()])
)

# 2 часть SQLAlchemy
logger.info('2 часть SQLAlchemy')
	
Base = declarative_base()
	
class MoviesTop(Base):
    __tablename__ = 'movies_top'

    movieid = Column(Integer, primary_key=True)
    ratings_num = Column(Float)
    ratings_avg = Column(Float)

    def __repr__(self):
        return "<User(movieid='%s', ratings_num='%s', ratings_avg='%s')>" % (self.movieid, self.ratings_num, self.ratings_avg)

#engine = create_engine('postgresql://postgres:@{}:{}'.format('0.0.0.0', 5433))
engine = create_engine('postgresql://postgres:@{}'.format(os.environ['APP_POSTGRES_HOST']))
Session = sessionmaker(bind=engine)
session = Session()
	
top_rated_query = session.query(MoviesTop).filter(MoviesTop.ratings_num > 15).filter(MoviesTop.ratings_avg > 3.5).order_by(MoviesTop.ratings_avg)
logger.info('Результат выбрки SQLAlchemy top_rated_query\n{}' . format([i for i in top_rated_query.limit(4)]))

top_rated_content_ids = [
    i[0] for i in top_rated_query.values(MoviesTop.movieid)
][:5]

# 3 часть PyMongo
logger.info('3 часть - PyMongo')

mongo = MongoClient(**{
    'host': os.environ['APP_MONGO_HOST'],
    'port': int(os.environ['APP_MONGO_PORT'])
})
db = mongo.get_database(name="movie")
tags_collection = db['tags']

logger.info("Общее количество документов к коллекции: {}".format(db.tags.count()))

logger.info("Теги фильмов из массива top_rated_content_ids и модификатор $in.")
logger.info("Проверка даннных в таблице тегов : {}".format(db.tags.find_one()))
#for res in db.tags.find({"name":"war"}).limit(5): print(res)
#print(list(db.tags.find({"name":"war"}).limit(5)))

#mongo_query = tags_collection.find({'id': {"$in": [3175,931]}})
mongo_query = tags_collection.find({'id': {"$in": top_rated_content_ids}})
mongo_docs = [
    i for i in mongo_query
]

print("Достали документы из Mongo: {}".format(mongo_docs[:5]))
id_tags = [(i['id'], i['name']) for i in mongo_docs]

# 4 часть Pandas
logger.info('4 часть - Pandas')

tags_df = pd.DataFrame(id_tags, columns=['movieid', 'tags'])
my_tags_df = tags_df.groupby(['tags'])['movieid'].count().sort_values(ascending=False)

#top_5_tags = tags_df.head(5)
my_top_5_tags = my_tags_df.head(5)

#print(top_5_tags)
print(my_top_5_tags)

logger.info("На этом всё! Домашка выполнена.")
