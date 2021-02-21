SELECT user_id, COUNT(payment_sum) AS user_sum
FROM payments
GROUP BY user_id
ORDER BY user_sum
LIMIT 3
