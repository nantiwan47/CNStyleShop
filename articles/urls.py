from django.urls import path
from articles.views import *

urlpatterns = [
    path('article/list/', article_list, name='article_list' ),
    path('article/create/', article_create, name='article_create' ),
    path('article/edit/<int:article_id>/', article_edit, name='article_edit'),
    path('article/delete/<int:article_id>/', article_delete, name='article_delete'),

    path('article/detail/<int:article_id>/', article_detail, name='article_detail'),

]