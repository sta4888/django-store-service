# django-store-service





## команды

```shell

```

создание миграций для конкретного приложения
```shell
python manage.py makemigrations users
```

Проверяем созданные миграции
```shell
python manage.py sqlmigrate catalog 0001
```

применение миграций

```shell
python manage.py migrate
```

создание суперпользователя
```shell
python manage.py createsuperuser --username admin --email admin@example.com
```
или
```shell
python manage.py createsuperuser 
```


запуск сервера

```shell
python manage.py runserver
```


запуск тестов 
```shell
python -m pytest src/users/tests/ -v
```

запуск shell
```shell
python manage.py shell
```