@echo off
erase db.sqlite3
erase products\migrations\0*.py
erase users\migrations\0*.py
erase cart\migrations\0*.py
echo "DATABASE Removed..."
@echo off
python manage.py makemigrations 
python manage.py migrate 
python manage.py createsuperuser