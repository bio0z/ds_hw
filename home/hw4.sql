SELECT 'ФИО: Безруких Игорь';
-- 1 : top-5 самых больших таблиц базы
select table_name, pg_relation_size(table_name) from information_schema.tables where table_schema <> 'information_schema' order by pg_relation_size(table_name) desc limit 5;
-- функции Postgres 
-- 1 : все фильмы, просмотренные пользователем
SELECT userID, array_agg(movieId) as user_views FROM ratings GROUP BY userid;
-- 2 : создание таблицы user_movies_agg
SELECT userID, user_views INTO public.user_movies_agg FROM (SELECT userID, array_agg(movieId) as user_views FROM ratings GROUP BY userid) as user_movies_agg;
SELECT * FROM user_movies_agg LIMIT 3;
-- 3 : функцию cross_arr, пересечение контента из обоих списков
CREATE OR REPLACE FUNCTION cross_arr(in arr1 int[], in arr2 int[]) RETURNS int[] AS 
$$
	select array_agg(intress) from (select UNNEST($1) as intress intersect select UNNEST($2) as intress) as  intress
$$
LANGUAGE SQL;

-- 4 : всевозможные наборы
DROP TABLE IF EXISTS common_user_views;
with all_user_pairs as 
(select f.userid as u1, f.user_views as arr1, s.userid as u2, s.user_views as arr2 from user_movies_agg f cross join user_movies_agg s where f.userid<>s.userid)
select u1, u2, cross_arr(arr1::int[], arr2::int[]) as crossed_array
into public.common_user_views from all_user_pairs where cross_arr(arr1::int[], arr2::int[]) IS NOT NULL;

--  5 : топ-10 пользователей с самыми большими пересечениями.
select * from common_user_views order by array_length(cross_arr,1) desc limit 10;

-- 6 : функцию diff_arr, вычитает один массив из другого.
CREATE OR REPLACE FUNCTION diff_arr(in arr1 int[], in arr2 int[]) RETURNS int[] AS 
$$
	select array_agg(express) from (select UNNEST($1) as express EXCEPT select UNNEST($2) as express) as express
$$
LANGUAGE SQL;

-- 7 : рекомендации
SELECT cu.u2, diff_arr(um.user_views::int[], cu.cross_arr::int[]) FROM common_user_views cu CROSS JOIN user_movies_agg um where cu.u1=um.userid LIMIT 10;
