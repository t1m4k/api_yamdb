### Как запустить проект:

Клонируйте репозиторий (ssh):
```
git clone git@github.com:t1m4k/api_yamdb.git
```

Измените свою текущую рабочую директорию:
```
cd /api_yamdb/
```

Создайте и активируйте виртуальное окружение

```
python -m venv venv
```

```
source venv/scripts/activate
```

Обновите pip:
```
pip install -U pip
```

Установите зависимости из requirements.txt:

```
pip install -r requirements.txt
```

Создайте миграции:

```
python manage.py makemigrations
```
Примените миграции:

```
python manage.py migrate
```
Запустите сервер:

```
python manage.py runserver
```

### Авторы:
