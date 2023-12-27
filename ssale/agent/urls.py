from django.urls import path
from . import views

urlpatterns = [
    path('stream_chat/', views.stream_chat, name='stream_chat'),
    path('new_session/', views.new_session, name='new_session'),
    path('old_session/', views.old_session, name='old_session'),
    path('list_session/', views.list_session, name='list_session'),
    path('save_history/', views.save_history, name='save_history'),
]