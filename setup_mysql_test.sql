-- Prepares a MySQL server for the AirBnB clone project (test)
-- Create the database hbnb_test_db if it does not exist
CREATE DATABASE IF NOT EXISTS hbnb_test_db;
-- Create the user hbnb_test (localhost) if it does not exist
CREATE USER IF NOT EXISTS 'hbnb_test'@'localhost' IDENTIFIED BY 'hbnb_test_pwd';
-- Give hbnb_test all privileges on hbnb_test_db only
GRANT ALL PRIVILEGES ON `hbnb_test_db`.* TO 'hbnb_test'@'localhost';
-- Give hbnb_test the SELECT privilege on performance_schema only
GRANT SELECT ON `performance_schema`.* TO 'hbnb_test'@'localhost';
-- Apply the privilege changes
FLUSH PRIVILEGES;
