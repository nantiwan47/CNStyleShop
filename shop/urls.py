from django.urls import path
from shop.views import ShopListView, ShopArticleListView, ArticleDetailView

urlpatterns = [
    path('', ShopListView.as_view(), name='home'),
    path('articles/', ShopArticleListView.as_view(), name='articles'),
    path('article/detail/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),

]