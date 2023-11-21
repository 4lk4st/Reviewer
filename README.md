# Проект "Yamdb"
 Веб-ресурс для сбора отзывов пользователей на произведения. Можно обсудить фильм, музыку или литературу, оставить ревью или комментарий на него.

 ## Технологии:
- Python 3.9
- Django 3.2
- Django rest framework
- Pillow 9.3.0
- PyJWT 2.1.0
- Pytest
- SQLite3
### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:


Cоздать и активировать виртуальное окружение:

```bash
python3 -m venv env
```

```bash
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```bash
python3 -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

Выполнить миграции:

```bash
python3 manage.py migrate
```

Запустить проект:

```bash
python3 manage.py runserver
```
## Примеры некоторых запросов

**POST** `.../api/v1/auth/signup/`
```js
{
    "email": "string",
    "username": "string"
}
```
Пример ответа:
```
{
    "email": "string",
    "username": "string"
}
```

**GET** `.../api/v1/categories/`
```js
{
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
        {
            "name": "string",
            "slug": "string"
        }
    ]
}
```

**GET** `.../api/v1/genres/`
```js
{
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
        {
            "name": "string",
            "slug": "string"
        }
    ]
}
```

**GET** `.../api/v1/titles/`
```js
{
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
        {
            "id": 0,
            "name": "string",
            "year": 0,
            "rating": 0,
            "description": "string",
            "genre": [
                {
                    "name": "string",
                    "slug": "string"
                }
            ],
            "category": {
                "name": "string",
                "slug": "string"
            }
        }
    ]
}
```


### Документация к проекту

Документация и полный список запросов к API можно посмотреть после запуска сервера:
```
/redoc/
```

### Авторы
Рахим Исхаков

Всеволод Зайковский

Темникова Дарья
