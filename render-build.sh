#!/usr/bin/env bash
# Xatolik bo'lsa darrov to'xtatish
set -o errexit

# Kutubxonalarni o'rnatish
pip install -r requirements.txt

# Statik fayllarni yig'ish (CSS, JS, Rasmlar)
python manage.py collectstatic --no-input

# Ma'lumotlar bazasini yangilash (Migrate)
python manage.py migrate