from django.urls import path
from .views import  *

urlpatterns = [
 path('dashboard/', dashboard, name='dashboard'),
 path('product/list', product_list, name="product_list"),
 path('product/create/', product_create, name="product_create"),
 path('product/edit/<int:product_id>/', product_edit, name='product_edit'),
 path('product/delete_image/<int:image_id>/', delete_image, name='delete_image'),
 path('product/delete/<int:product_id>/', product_delete, name='product_delete'),

]