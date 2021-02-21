-- CREATE TABLE IF NOT EXISTS users(
--     user_id INT  auto_increment PRIMARY KEY,
--     login CHAR(128) NOT NULL,
--     reg_dttm TIMESTAMP NOT NULL
-- );
-- CREATE TABLE IF NOT EXISTS payments(
--     payment_id INT  auto_increment PRIMARY KEY,
--     payment_sum DOUBLE NOT NULL,
--     payment_dttm TIMESTAMP NOT NULL DEFAULT (00.0001),
--     user_id INT NOT NULL,
--     FOREIGN KEY(user_id)
--     REFERENCES users(user_id)
--     ON UPDATE CASCADE ON DELETE CASCADE
-- );
-- CREATE TABLE IF NOT EXISTS sessions(
--     session_id INT  AUTO_INCREMENT PRIMARY KEY,
--     begin_dttm TIMESTAMP NOT NULL,
--     end_dttm TIMESTAMP NOT NULL,
--     user_id INT NOT NULL,
--     FOREIGN KEY(user_id)
--     REFERENCES users(user_id)
--     ON UPDATE CASCADE ON DELETE CASCADE
-- );

-- 'C:\ProgramData\MySQL\MySQL Server 8.0\Uploads\'
-- SHOW VARIABLES LIKE "secure_file_priv";
LOAD DATA INFILE 'users.csv' INTO TABLE users;
-- INSERT INTO users (login) VALUES ('LOLOLO');
-- INSERT INTO payments (payment_sum, user_id) VALUES
--  (30, 1), (40, 2), (33, 1),(333, 1), (444, 3), (100, 3);


