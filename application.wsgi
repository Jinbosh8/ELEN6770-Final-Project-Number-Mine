#application.wsgi
import sys
sys.path.insert(0, '/var/www/html/NumberMine')

from application import application as application

