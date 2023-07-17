# Консольные команды

___

### [Вернуться назад](../README.md)

* </span><span style="color:orange">__Запустить локально__</span>

```bash
cd ..
poetry run python app/main.py
```

* </span><span style="color:orange">__Создать миграцию__</span>

```bash
cd ../app
alembic revision --autogenerate -m "First migration"
```
* </span><span style="color:orange">__Накатить миграцию__</span>

```bash
cd ../app
alembic upgrade head
```