SELECT 'ФИО: Безруких Игорь';
-- оконные функции : убрал пользователей у который 1 оценка, при расчёте получается деление на ноль.
SELECT userId, movieId,
  MIN(rating) OVER (PARTITION BY userId) min_rating,
  MAX(rating) OVER (PARTITION BY userId) max_rating,
  (MAX(rating) OVER (PARTITION BY userId) - MIN(rating) OVER (PARTITION BY userId)) diff_rating,
  (rating - MIN(rating) OVER (PARTITION BY userId))/(MAX(rating) OVER (PARTITION BY userId) - MIN(rating) OVER (PARTITION BY userId)) normed_rating,
  AVG(rating) OVER (PARTITION BY userId) avg_rating
FROM (SELECT DISTINCT userId, rating, movieId FROM ratings WHERE userId <>0 and userId in (select userID from ratings group by userid having count(rating)>1)) as sample
ORDER BY userId, rating DESC LIMIT 30;

-- команды создания таблицы
psql --host $APP_POSTGRES_HOST -U postgres -c "CREATE TABLE keywords (id integer, tags text)"
-- команда заполнения таблицы 
psql --host $APP_POSTGRES_HOST -U postgres -c "\\copy keywords FROM '/data/keywords.csv' DELIMITER ',' CSV HEADER"
-- запрос 3.1 ЗАПРОС1
select movieId, avg(rating) from ratings where movieid in (select movieid from ratings group by movieid having count(rating)>50) group by movieid order by avg(rating) desc, movieid asc limit 150;
-- запрос 3.2 ЗАПРОС2
WITH top_rated as 
	(select movieId, avg(rating) as avg_rating from ratings where movieid in (select movieid from ratings group by movieid having count(rating)>50) group by movieid order by avg(rating) desc, movieid asc limit 150 ) 
select tr.movieId, tr.avg_rating, k.tags
from top_rated tr join keywords k on k.id=tr.movieId limit 10;
-- запрос 3.3 ЗАПРОС3
WITH top_rated as 
	(select movieId, avg(rating) as avg_rating from ratings where movieid in (select movieid from ratings group by movieid having count(rating)>50) group by movieid order by avg(rating) desc, movieid asc limit 150 ) 
select tr.movieId, tr.avg_rating, k.tags INTO top_rated_tags
from top_rated tr join keywords k on k.id=tr.movieId limit 10;
-- команда выгрузки таблицы в файл
\copy (select * from top_rated_tags) to '\data\top_rated_tags' with CSV header delimiter as E'\t';
