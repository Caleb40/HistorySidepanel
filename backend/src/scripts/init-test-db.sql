-- Create test database and user
CREATE DATABASE history_sidepanel_test;
CREATE USER test_user WITH PASSWORD 'test_password';
GRANT ALL PRIVILEGES ON DATABASE history_sidepanel_test TO test_user;