from django.urls import path
from . import views

urlpatterns = [
    path('getProductByShop/', views.getProductByShop, name='getProductByShop'),
    path('weather/<str:city_name>', views.get_weather, name='get_weather' )
]