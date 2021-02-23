/* Запрос 1. Вывести логины трёх пользователей
	с наибольшим количеством сессий */

/* возвращает id трех пользователей с наиб кол-вом сессий
 и само кол-во */
SELECT user_id, count(session_id) AS count_s FROM sessions
GROUP BY user_id ORDER BY count_s DESC LIMIT 3;

/* возвращает логины строго по запросу */
SELECT login FROM users
INNER JOIN (
 SELECT user_id, count(session_id) FROM sessions
 GROUP BY user_id
 ORDER BY count(session_id)
 DESC LIMIT 3
) AS count_of_sessions
ON users.user_id = count_of_sessions.user_id;

/* возвращает логины и количество сессий */
SELECT users.login,count_of_sessions.count_s FROM users
INNER JOIN (
 SELECT user_id, count(session_id) AS count_s
 FROM sessions
 GROUP BY user_id
 ORDER BY count_s
 DESC LIMIT 3
) AS count_of_sessions
ON users.user_id = count_of_sessions.user_id;

/* Запрос 2. Посчитать средний платеж платящего пользователя */

/*средний платеж каждого отдельно */
SELECT user_id, AVG(payment_sum) AS mid_arifm FROM payments
GROUP BY user_id;

/*средний платеж среди всех пользователей */
SELECT AVG(payment_sum) as mid_arifm FROM payments;

/*средний платеж конкретного по его id */
SELECT AVG(payment_sum) FROM payments WHERE user_id = 3;










