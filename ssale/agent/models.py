from django.db import models
from shop.models import *
# Create your models here.
from django.contrib.auth.models import User


class User(User):
    # Các trường thông tin bổ sung có thể được thêm vào đây
    isShop = models.BooleanField(default=False)

# Mô hình Phiên Trò Chuyện
class ChatSession(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, related_name='chat_sessions', on_delete=models.CASCADE)

    def __str__(self):
        return f"ChatSession started at {self.start_time} by {self.user}"
    
class Message(models.Model):
    content = models.TextField()
    session = models.ForeignKey(ChatSession,related_name='sessions', on_delete=models.CASCADE)
    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

