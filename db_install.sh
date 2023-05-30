# Установка Postgresql
apt-get update
apt-get -y install postgresql

# Настройка базы данных
sudo -u postgres psql -c "CREATE DATABASE telebot;"
sudo -u postgres psql -c "CREATE USER myuser WITH PASSWORD 'mypass';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE telebot TO myuser;"
