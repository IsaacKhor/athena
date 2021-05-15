from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'yge7&9=pn(g*(c-5o3di42+hz&d_c16+g)oea7gdshhu_n!3+3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '140.232.229.10', 
    'athena.clarku.edu', 
    'localhost'
]

# Application definition
INSTALLED_APPS = (
    # third party packages
    'django_bootstrap5',
    'django_python3_ldap',
    'django_q',
    'django_extensions',

    #django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # custom apps
    'grader',
    'autogapp'
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ClarkCSHWGrader.wsgi.application'

#LDAP authentication options
AUTHENTICATION_BACKENDS = [ 'django_python3_ldap.auth.LDAPBackend' ]
LDAP_AUTH_URL = "ldap://140.232.229.7:389"
LDAP_AUTH_USE_TLS = False
LDAP_AUTH_SEARCH_BASE = "dc=cslab"
LDAP_AUTH_OBJECT_CLASS = "inetOrgPerson"

# The LDAP Username and password of a user so ldap_sync_users can be run
# Set to None if you allow anonymous queries
LDAP_AUTH_CONNECTION_USERNAME = None
LDAP_AUTH_CONNECTION_PASSWORD = None

# User model fields mapped to the LDAP
# attributes that represent them.
LDAP_AUTH_USER_FIELDS = {
    "username": "uid",
    "first_name": "cn",
}

# A tuple of fields used to uniquely identify a user.
LDAP_AUTH_USER_LOOKUP_FIELDS = ("username",)

# Callable that transforms the user data loaded from
# LDAP into a form suitable for creating a user.
# Override this to set custom field formatting for your
# user model.
import django_python3_ldap.utils
LDAP_AUTH_CLEAN_USER_DATA = django_python3_ldap.utils.clean_user_data

ROOT_URLCONF = 'ClarkCSHWGrader.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'ClarkCSHWGrader.wsgi.application'

DATABASES = {
    'default' : {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME' : 'grader',
        'USER': 'django',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '', #empty is default
    }
}


## sqlite database ##
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}
#Import databse configuration
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'US/Eastern'
USE_I18N = False
USE_L10N = False
USE_TZ = True

STATIC_ROOT = BASE_DIR / 'static'
STATIC_URL = '/static/'

# Runtime data directories
MEDIA_ROOT = BASE_DIR / 'runtimedata'
SUBMISSION_DIR = MEDIA_ROOT / 'submissions'
COURSE_DIR = MEDIA_ROOT / 'course_files'
TEMP_DIR = MEDIA_ROOT / 'tmp'

# Autograder settings
AUTOGRADER_DIR = BASE_DIR / 'autograder' # Location of autograder .zip files
AUTOGRADE_SCRIPT = BASE_DIR / 'autograder' / 'autograde.sh'

#Email host to use for usernames
DEFAULT_EMAIL_HOST = "clarku.edu"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Database, test only
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'athena',
        'USER': 'athena',
        'PASSWORD': 'athena',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

# Django-q cluster config
Q_CLUSTER = {
    'name': 'autograder-cluster',
    'workers': 6,
    'recycle': 500,
    'timeout': 900, # in seconds, can be overriden per-task
    'retry': 1000,
    'compress': False,
    'save_limit': 100,
    'queue_limit': 36,
    'label': 'Autograder Queue',
}