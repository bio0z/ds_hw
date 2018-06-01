# Работа с Pandas

Pаndas - библиотека для работы с табличными данными. Основной объект в Pandas - DataFrame, представляет собой абстракцию таблицы.

Библиотека позволяет гибко загружать данные из текстовых файлов, а так же из реляционных баз данных

Пример - подгружаем в DataFrame файл с рейтингами (все команды выполняются в python консоли)

Импортируем нужные библиотеки
<pre>
import pandas as pd
import numpy as np
</pre>

<pre>
>>> df = pd.read_csv('/data/links.csv', sep=',', header='infer')
>>> df.head()
   movieId  imdbId   tmdbId
0        1  114709    862.0
1        2  113497   8844.0
2        3  113228  15602.0
3        4  114885  31357.0
4        5  113041  11862.0
>>> df.dtypes
movieId      int64
imdbId       int64
tmdbId     float64
dtype: object
</pre>

Автоматически чтаем заголовок в первой строке и неявно приводим колонку к правильному типу данных

Тип данных можно поменять на лету:
<pre>
links[['tmdbId']] = df.tmdbId.astype(np.int64)
</pre>

Фозникнет ошибка про незаполненные поля
<pre>
ValueError: Cannot convert non-finite values (NA or inf) to integer
</pre>

Аналог конструкции UPDATE + WHERE
<pre>
links.loc[df.tmdbId.isnull()] = 0
</pre

После этого ещё раз запустим процессинг - ошибка больше не возникнет.

# Загрузка из Postgres

<pre>
>>> ratings = pd.read_sql('SELECT * FROM ratings', engine)
>>> ratings.head()
   userid  movieid  rating   timestamp
0       1       31     2.5  1260759144
1       1     1029     3.0  1260759179
2       1     1061     3.0  1260759182
3       1     1129     2.0  1260759185
4       1     1172     4.0  1260759205
>>> ratings.dtypes
userid         int64
movieid        int64
rating       float64
timestamp      int64
dtype: object
</pre>

Можно заметить, что Pandas воспользовался информацией о типаъ данных из метаиныормации о таблице в БД.

# Pandas - конструкции из SQL.

Pandas позволяет строить конструкции, аналогичные операторам SQL - where, join и т.д.

DataFrame.merge - аналог JOIN
<pre>
>>> links.merge(ratings, how='inner', left_on='movieId', right_on='movieid').head()
   movieId  imdbId  tmdbId  userid  movieid  rating   timestamp
0        1  114709   862.0       7        1     3.0   851866703
1        1  114709   862.0       9        1     4.0   938629179
2        1  114709   862.0      13        1     5.0  1331380058
3        1  114709   862.0      15        1     2.0   997938310
4        1  114709   862.0      19        1     3.0   855190091
</pre>

how - тип джойна, кроме INNER бывает ещё LEFT.

Агрегация данных происходит в операторе GroupBy:

<pre>
>>> ratings[ratings.timestamp > datetime.datetime.strptime('2015-01-01', '%Y-%m-%d').timestamp()].groupby(by=['userid'])['movieid'].count().sort_values(ascending=False).head()
userid
213    910
457    713
262    676
475    655
56     522
</pre>

COUNT - встроенная функция, кастомные функции можно передавать в .agg и считать несколько различных метрик

<pre>
>>> ratings[ratings.timestamp > datetime.datetime.strptime('2015-01-01', '%Y-%m-%d').timestamp()].groupby(by=['userid'])['rating'].agg([np.ma.count, np.mean, np.std]).head()
        count      mean       std
userid
15      266.0  2.274436  1.232372
38        4.0  4.125000  0.478714
40       43.0  4.511628  0.369819
42       70.0  4.014286  0.756477
48       17.0  3.000000  0.612372
</pre>