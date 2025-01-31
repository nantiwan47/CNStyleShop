from django.urls import path
from .views import dashboard, analyze_reviews, test

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('analyze-reviews/', analyze_reviews, name='analyze_reviews'),
    path('test/', test, name='test'),

]