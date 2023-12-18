from django.urls import path
from . import views

urlpatterns = [
    path('stream_chat/', views.stream_chat, name='stream_chat'),
]