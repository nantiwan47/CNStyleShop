from django.urls import path
from shop.views import ShopListView, ProductDetailView, ProductOptionView

urlpatterns = [
    path('', ShopListView.as_view(), name='home'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name="product_detail"),
    path("product/<int:pk>/options/", ProductOptionView.as_view(), name="product-option"),  # ✅ ตรวจสอบเส้นทางนี้


]