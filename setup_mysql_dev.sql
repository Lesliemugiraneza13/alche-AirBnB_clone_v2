-- Prepares a MySQL server for the AirBnB clone project (development)
-- Create the database hbnb_dev_db if it does not exist
CREATE DATABASE IF NOT EXISTS hbnb_dev_db;
-- Create the user hbnb_dev (localhost) if it does not exist
CREATE USER IF NOT EXISTS 'hbnb_dev'@'localhost' IDENTIFIED BY 'hbnb_dev_pwd';
-- Give hbnb_dev all privileges on hbnb_dev_db only
GRANT ALL PRIVILEGES ON `hbnb_dev_db`.* TO 'hbnb_dev'@'localhost';
-- Give hbnb_dev the SELECT privilege on performance_schema only
GRANT SELECT ON `performance_schema`.* TO 'hbnb_dev'@'localhost';
-- Apply the privilege changes
FLUSH PRIVILEGES;
