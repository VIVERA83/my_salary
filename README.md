# My salary

___
<span id="0"></span>
### [Консольные команды](docs/comand.md)

### <span id="1">1. </span><span style="color:purple">Описание</span>

REST-сервис просмотра текущей зарплаты и даты следующего
повышения. 

__Подробная информация по Api:__

- Swagger документация http://127.0.0.1:8000/docs
- Swagger(альтернатива) http://127.0.0.1:8000/redoc

Точная ссылка к документации выводится в логах при запуске сервиса.

___

### <span id="2">2. </span><span style="color:purple">Запуск сервиса</span>

* </span><span style="color:orange">__Клонируем репозиторий:__</span>

```bash
git clone git@github.com:VIVERA83/derbit.git
```

* </span><span style="color:orange">__Переходи в папку с проектом:__</span>

```bash
cd derbit
```

* </span><span style="color:orange">__Создаем файл .env (с переменными окружения) на основе
  примера [.env_example](.env_example)*:__</span>

```bash
echo "COMPOSE_PROJECT_NAME="my_salary"
# Настройка настройка логирования
LOGGING__LEVEL="DEBUG"
LOGGING__GURU="True"
LOGGING__TRACEBACK="True"

# Настройка Postgres
POSTGRES_DB="data_base"
POSTGRES_USER="super_user"
POSTGRES_PASSWORD="super_password"
POSTGRES_HOST="postgres_my_salary"
POSTGRES_PORT="5432"
POSTGRES_DB_SCHEMA="my_salary"

# Настройка Authorization
KEY="144bcc7e564373040999aac89e7622f3ca71fba1d972fd94a31c3bfbf24e3938"
ALGORITHMS=["HS256"]
ACCESS_EXPIRES_DELTA=60
REFRESH_EXPIRES_DELTA=172800

# Настройка приложения
APP_NAME="My_salary"
APP_HOST="0.0.0.0"
APP_PORT="8004"
APP_UVICORN_WORKERS=1
SECRET_KEY="strange code is written"
ALLOWED_ORIGINS=["*"]
ALLOW_METHODS=["*"]
ALLOW_HEADERS=["*"]
ALLOW_CREDENTIALS="True"
" >>.env
```

В ОС windows можно скопировать фаил [.env_example](.env_example) в `.env` командой `copy`, это будет равнозначно команде
выше

```shell
copy /Y ".env_example" ".env"
```

* </span><span style="color:orange">__Запускаем приложение в контейнере:__</span>

```bash
docker-compose up --build
```

* </span><span style="color:orange">__Открываем Swagger:__</span>

Переходим по ссылке указанной в консоли на страницу с документацией
![img.png](docs/images/swagger_link.png)

Если запуск произведен локально то http://127.0.0.1:8000/docs
___

### [Наверх](#0)