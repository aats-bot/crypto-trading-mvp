-- Create database if not exists
CREATE DATABASE crypto_trading_mvp;

-- Create user if not exists
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'crypto_user') THEN

      CREATE ROLE crypto_user LOGIN PASSWORD 'crypto_password';
   END IF;
END
$do$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE crypto_trading_mvp TO crypto_user;

-- Connect to the database
\c crypto_trading_mvp;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO crypto_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO crypto_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO crypto_user;

