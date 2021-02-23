/* создание базы данных bankgo */
CREATE DATABASE IF NOT EXISTS bankgo;
SHOW DATABASES;
USE bankgo;
SELECT DATABASE();

/* создание и заполнение таблицы users*/
CREATE TABLE IF NOT EXISTS users(
 user_id INT PRIMARY KEY AUTO_INCREMENT,
 login CHAR(100),
 reg_dttm TIMESTAMP
);
DESC users;

SHOW TABLES;

LOAD DATA
 INFILE 'C:/mysql/data/bankgo/users.csv'
 INTO TABLE users
 FIELDS TERMINATED BY ';'
;
SELECT * FROM users;

/* создание и заполнение таблицы payments*/
CREATE TABLE IF NOT EXISTS payments(
 payment_id INT PRIMARY KEY,
 user_id INT,
 payment_sum DOUBLE,
 payment_dttm TIMESTAMP,
 FOREIGN KEY (user_id) REFERENCES users (user_id)
);
DESC payments;

LOAD DATA
 INFILE 'C:/mysql/data/bankgo/payments.csv'
 INTO TABLE payments
 FIELDS TERMINATED BY ';'
;
SELECT * FROM payments;

/* создание и заполнение таблицы sessions*/
CREATE TABLE IF NOT EXISTS sessions(
 session_id INT PRIMARY KEY,
 user_id INT,
 begin_dttm TIMESTAMP,
 end_dttm TIMESTAMP,
 FOREIGN KEY (user_id) REFERENCES users (user_id)
);
DESC sessions;

LOAD DATA
 INFILE 'C:/mysql/data/bankgo/sessions.csv'
 INTO TABLE sessions
 FIELDS TERMINATED BY ';'
;
SELECT * FROM sessions;