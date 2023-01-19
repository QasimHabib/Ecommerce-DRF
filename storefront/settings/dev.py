from .common import *

DEBUG = True

SECRET_KEY = 'django-insecure-lb$nj+xyw&*&iqzxsm^ak+#t@p*)($eyp#=-&5ddm%@*#%tf_x'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'storefront',
        'HOST': 'localhost',
        'USER' : 'root',
        'PASSWORD': 'Qasimhabib123'

    }
}