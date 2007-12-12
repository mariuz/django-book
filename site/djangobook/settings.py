ADMINS = [("Jacob", "jacob@jacobian.org")]

ADMIN_MEDIA_PREFIX = 'http://media.djangoproject.com/admin/'

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = 'djangobook'
DATABASE_USER = "apache"

DEBUG = True
TEMPLATE_DEBUG = DEBUG
PREPEND_WWW = not DEBUG

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.flatpages",
    "django.contrib.humanize",
    "django.contrib.markup",
    "django.contrib.redirects",
    "django.contrib.sessions", 
    "django.contrib.sites", 
    "django_evolution",
    "djangobook",
)

MANAGERS = ADMINS

MEDIA_ROOT = '/home/media/media.djangobook.com/'
MEDIA_URL = 'http://media.djangobook.com/'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = "djangobook.urls"

SECRET_KEY = '8-b(7zd6y!w-+ds9+bqw$)$_dfz!haol&&ru8qlh3bzza3w)ap'

SITE_ID = 1

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)
TEMPLATE_DIRS = ('/home/djangobook.com/templates/',)

TIME_ZONE = 'America/Chicago'
