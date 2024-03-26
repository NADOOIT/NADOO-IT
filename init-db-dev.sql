CREATE USER 'your_mysql_user'@'%' IDENTIFIED BY 'your_database_password';
ALTER USER 'your_mysql_user'@'%' IDENTIFIED WITH mysql_native_password BY 'your_database_password';
GRANT ALL PRIVILEGES ON your_mysql_database.* TO 'your_mysql_user'@'%';
FLUSH PRIVILEGES;
