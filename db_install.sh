# Установка Postgresql
apt-get update
apt-get -y install postgresql

# Настройка базы данных
postgres psql -c "CREATE DATABASE telebot;"
postgres psql -c "CREATE USER myuser WITH PASSWORD 'mypass';"
postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE telebot TO myuser;"
