from django.urls import path
from articles.views import ArticleListView,ArticleCreateView, ArticleUpdateView, ArticleDeleteView

urlpatterns = [
    path('article/list/', ArticleListView.as_view(), name='article_list' ),
    path('article/create/', ArticleCreateView.as_view(), name='article_create' ),
    path('article/edit/<int:pk>/', ArticleUpdateView.as_view(), name='article_edit'),
    path('article/delete/<int:pk>/', ArticleDeleteView.as_view(), name='article_delete'),
]