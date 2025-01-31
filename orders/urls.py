from django.urls import path
from .views import order_list, order_detail

urlpatterns = [
    path('order/list', order_list, name='order_list'),
    path('order/detail/<int:order_id>/', order_detail, name='order_detail'),
]