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
if alembic revision --autogenerate -m "First migration"; then
  sleep 3
  exit 0
fi
```
* </span><span style="color:orange">__Накатить миграцию__</span>

```bash
cd ../app
if alembic upgrade head; then
  sleep 3
  exit 0
fi 
```