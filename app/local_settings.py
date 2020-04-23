from .settings import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -----------------------------------------------------------
# DEVELOPMENT SETTING
# ------------------------------------------------------------

SECRET_KEY = 'qn9ha89dlx0ra5=(t)i(9npey-63e3%1vm6nx5+8(h(05xh7-+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database on DEVELOPMENT
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}