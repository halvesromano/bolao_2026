import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.test import Client
from django.contrib.auth.models import User
c = Client()
u = User.objects.first()
c.force_login(u)
res = c.get('/estatisticas/')

with open('stat_output.html', 'w', encoding='utf-8') as f:
    f.write(res.content.decode('utf-8'))
