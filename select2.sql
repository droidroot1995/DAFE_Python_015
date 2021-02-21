SELECT user_id, AVG(payment_sum) AS av_payment  FROM 
(SELECT * FROM payments WHERE payment_sum > 0) AS t
GROUP BY user_id 