SELECT 'ФИО: Безруких Игорь';
-- 1 часть : запросы
select * from ratings limit 10;
select * from links l where l.imdbid like '%42' and (l.movieid >100 and l.movieid<1000) limit 10;
-- 2 часть : запросы
select l.imdbid from links l join ratings r on l.movieid=r.movieid where r.rating =5 limit 10;
-- 3 часть : запросы
select count(*) from links where movieid not in (select distinct(movieid) from ratings);
select avg(rating) as "average rating" from ratings group by userid having avg(rating) > 3.5 order by avg(rating) desc limit 10;
-- 4 часть: запросы
select imdbid from links where movieid in (select movieid from ratings group by movieid having avg(rating) > 3.5 order by avg(rating) asc limit 10);
	-- простой вариант
select userid, avg(rating) as "avg rating", count(rating) as "count ratings" from ratings group by userid having count(rating)>10 order by count(rating) desc limit 10;
	-- CTE 
with top_users_ratings as (select userid, avg(rating) as "avg_rating", count(rating) as "count_ratings" from ratings group by userid order by count(rating) desc) select avg_rating as avg_rating from top_users_ratings where count_ratings >10 limit 10;
