# cloveri_vacancies
Vacancies API

Микросервис для работы с вакансиями.
При разработке использовался шаблон: 
[https://github.com/tiangolo/full-stack-fastapi-postgresql](https://github.com/tiangolo/full-stack-fastapi-postgresql)

## Деплой для разработчиков и тестировщиков

1. Утсанавливаем и активируем окружение
```commandline
python3 -m venv venv
source venv/bin/activate
```
2. Нужен python версии 3.9+
```commandline
cd cloveri_vacancies
```

3. Устанавливаем зависимости через poetry
```
poetry install
```
или pip
```commandline
pip install -r requirements.txt
```
4. Конфигурируем env. (создать .env и положить в корень проекта)
```
vim .env
```
```
ENVIRONMENT="DEV"
BACKEND_CORS_ORIGINS=localhost
DEFAULT_DATABASE_HOSTNAME=localhost
DEFAULT_DATABASE_DB=vacancies
DEFAULT_DATABASE_USER=
DEFAULT_DATABASE_PASSWORD=
DEFAULT_DATABASE_PORT=5434
```
3. Поднимаем постгрес. Можно через прилагающийся докер компоуз. <br> 
При первоначальном запуске команда ниже создаст и запустит контейнер с Postgres с параметрами default_database из файла .env<br>
Ключ -d запустит контейнер без вывода отладочной информации в консоль.
```commandline
docker-compose up -d default_database
```
Далее, чтобы остановить но не удалять контейнер нужно набрать:
```commandline
docker-compose stop default_database
```
Если нужно повторно запустить ранее созданный контейнер:
```commandline
docker-compose start -d default_database  
```
Если нужно удалить контейнер (ОСТОРОЖНО могут удалиться БД):
```commandline
docker-compose down  
```
Если нужно посмотреть логи контейнера:
```commandline
docker logs ID_CONTEINER
```
--follow - ключ для вывода в консоль логов контейнера


5. Накатываем алембик миграции
```commandline
alembic upgrade head
```
6. Запускаем серверное приложение

```commandline
python -m uvicorn app.main:app --port 8010 > app.log 2>&1 & 
```

## Запуск тестов ##
###################

Тесты разрабатывали на основе: [https://fastapi.tiangolo.com/tutorial/testing/](https://fastapi.tiangolo.com/tutorial/testing/) . <br>
В .env файле порт в docker-compose.yml для TEST_DATABASE_PORT должен отличаться от порта для DEFAULT_DATABASE_PORT

1. docker compose up -d test_database (при повторном запуске: docker compose start test_database)
2. pytest
3. docker compose stop test_database 

Для проверки открытых портов можно использовать команду:
```commandline
sudo lsof -i -P | grep LISTEN | grep :$PORT 
```

## PGadmin
Если для администрирования БД вы используете pgadmin, то в при разработке и использовании docker в качестве сетевого <br> 
адреса в настройках подключения pgadmin нужно указывать host.docker.internal (если не работает localhost)


## Деплой на STAGE

Подготовка:
1. Создать в домашнем каталоге папку www <br>
   Здесь будет храниться backend 
```commandline
mkdir www
```

2. Создать файл .env
```env
ENVIRONMENT="STAGE"
BACKEND_CORS_ORIGINS="allow_ip_addresses"
DEFAULT_DATABASE_HOSTNAME=ip_address_db
DEFAULT_DATABASE_DB=name_db
DEFAULT_DATABASE_USER=user_db
DEFAULT_DATABASE_PASSWORD=user_pwd
DEFAULT_DATABASE_PORT=port

PGADMIN_MAIL=email
PGADMIN_PW=pwd

STAGE_DATABASE_HOSTNAME=ip_address_db
STAGE_DATABASE_DB=name_db
STAGE_DATABASE_USER=user_db
STAGE_DATABASE_PASSWORD=pwd
STAGE_DATABASE_PORT=port

TEST_DATABASE_HOSTNAME=ip_address_db
TEST_DATABASE_DB=
TEST_DATABASE_USER=
TEST_DATABASE_PASSWORD=
TEST_DATABASE_PORT=
```

3. Создать в каталоге www папку frontend
```commandline
mkdir www/frontend
```

4. Сделать
```commandline
git clone -b deploy https://git.infra.cloveri.com/cloveri.start/job/vacancies.git
```
Скопировать в папку www
```commandline
cp vacancies www
```

5. Сделать 
```commandline
git clone -b dev https://git.infra.cloveri.com/cloveri.start/job/vacancies-front.git
```
Скопировать в папку www/frontend
```commandline
cp vacancies-front www/frontend
```

6. Перейти в папку www
```commandline
cd www
```

7. Заменить файл docker-compose.yml (здесь придется раскомментировать некоторые строки, так как база уже создана)
8. Собрать docker контейнер
```commandline
docker-compose build
```

9. Запустить docker контейнер
```commandline
docker-compose up -d
```
