from django.urls import path
from . import views
from .views import create_superuser_view

urlpatterns = [
    path('', views.product_list_view, name='home'),
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),

    path('create-superuser/', create_superuser_view, name='create_superuser'),
    path('chatbot/get_response/', views.get_chatbot_response, name='get_chatbot_response'),
]
