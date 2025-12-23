# CRM для малого бизнеса

Простая система учёта клиентов и заявок.

## Развёртывание на PythonAnywhere

### Шаг 1: Регистрация
1. Зайдите на https://www.pythonanywhere.com
2. Нажмите "Start running Python online" → "Create a Beginner account"
3. Зарегистрируйтесь (бесплатно)

### Шаг 2: Загрузка файлов
1. После входа нажмите **"Files"** в меню
2. Нажмите **"Upload a file"** и загрузите ZIP-архив проекта
3. Или используйте консоль Bash для git clone

### Шаг 3: Создание виртуального окружения
1. Откройте **"Consoles"** → **"Bash"**
2. Выполните команды:

```bash
cd ~
unzip crm.zip  # если загрузили архив
cd crm
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

### Шаг 4: Настройка веб-приложения
1. Перейдите в **"Web"** → **"Add a new web app"**
2. Выберите **"Manual configuration"** → **Python 3.10**
3. В настройках укажите:

**Source code:** `/home/ВАШЕ_ИМЯ/crm`

**Virtualenv:** `/home/ВАШЕ_ИМЯ/crm/venv`

4. Откройте **WSGI configuration file** и замените содержимое:

```python
import os
import sys

path = '/home/ВАШЕ_ИМЯ/crm'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'crm_project.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. В разделе **Static files** добавьте:
   - URL: `/static/`
   - Directory: `/home/ВАШЕ_ИМЯ/crm/staticfiles`

### Шаг 5: Настройка settings.py
Добавьте ваш домен в ALLOWED_HOSTS:
```python
ALLOWED_HOSTS = ['ВАШЕ_ИМЯ.pythonanywhere.com']
```

### Шаг 6: Запуск
1. Нажмите **"Reload"** на странице Web
2. Откройте https://ВАШЕ_ИМЯ.pythonanywhere.com

## Готово!
Ваша CRM доступна в интернете.






