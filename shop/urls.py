from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list_view, name='home'),
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('chatbot/get_response/', views.get_chatbot_response, name='get_chatbot_response'),
]
