"""
Django settings for CNStyleShop project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-g==fdl%rcf0s#t-ejx+-v0)iq5=8vf#(lmv*h$&-_ck1_-&1#z"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "products",
    "articles",
    "orders",
    "dashboard",
    "shop",
    "cart",

    "tailwind",
    "theme",
    "django_browser_reload",

    "tinymce"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",

    # เพิ่ม Middleware ป้องกันผู้ใช้ทั่วไปเข้าหน้า admin
    "accounts.middleware.AdminOnlyMiddleware",
]

ROOT_URLCONF = "CNStyleShop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates']
        ,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "CNStyleShop.wsgi.application"

TAILWIND_APP_NAME = 'theme'
NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'sqlite3': {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    'mysql': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cnstyleshop',               # ชื่อ Schema ที่สร้างใน Workbench
        'USER': 'root',                      # ชื่อผู้ใช้ที่สร้างไว้
        'PASSWORD': 'root',                  # รหัสผ่านของผู้ใช้
        'HOST': '127.0.0.1',                 # ใช้ localhost หรือ IP เซิร์ฟเวอร์
        'PORT': '3306',                      # พอร์ตของ MySQL (ค่าเริ่มต้นคือ 3306)
        'OPTIONS': {
            'charset': 'utf8mb4',            # รองรับภาษาไทย
        },
    },
}
DATABASES['default'] = DATABASES['mysql']

AUTH_USER_MODEL = 'accounts.UserProfile'

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'th'

TIME_ZONE = "Asia/Bangkok" # ใช้เวลาประเทศไทยโดยตรง

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static"
]

# Media settings
MEDIA_URL = '/media/'  # URL สำหรับเข้าถึงไฟล์
MEDIA_ROOT = BASE_DIR / 'media'  # โฟลเดอร์เก็บไฟล์อัปโหลด

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TINYMCE_DEFAULT_CONFIG = {
    'height': 400,  # ความสูงของ editor
    'width': 'auto',  # ปรับให้เหมาะกับพื้นที่
    'toolbar': 'undo redo |fontsize forecolor backcolor |bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist',  # เครื่องมือพื้นฐาน
    'menubar': False,  # ปิดเมนูด้านบน
    'plugins': 'lists',  # เพิ่มปลั๊กอิน lists
    'branding': False,  # ซ่อนโลโก้ TinyMCE
    'content_style': 'body {  background-color: #f5f5f5; }',  # กำหนดสีพื้นหลังและกรอบ

}

# ALLOWED_HOSTS = [
#     'eb31-49-231-194-157.ngrok-free.app',
#     'localhost',
#     '127.0.0.1'
# ]
