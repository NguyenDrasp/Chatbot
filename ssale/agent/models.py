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
    # HUMAN = 'human'
    # AI = 'ai'
    
    # MESSAGE_TYPE_CHOICES = [
    #     (HUMAN, 'human'),
    #     (AI, 'ai'),
    # ]

    # message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default=HUMAN)
    data = models.TextField(default = '')
    '''
    {'type': 'human',
    'data': {'content': 'Chào bạn, mình là Đạt',
            'additional_kwargs': {},
            'type': 'human',
            'example': False}}
    
            
     {'type': 'ai',
    'data': {'content': 'MDC có các sản phẩm sau đây:\n1. iMatch - Match, Chat, Date\n2. iVPN\n3. Vise - Video Search Engine\n4. Can Knockdown AR\n5. Can Knockdown AR Pro\n6. Super Bomber Online\n7. Super Tank Online\n8. Friend Locator\n\nBạn có thể tìm hiểu thêm về từng sản phẩm hoặc có câu hỏi cụ thể về sản phẩm nào đó không?',
        'additional_kwargs': {},
        'type': 'ai',
        'example': False}}
    '''

    session = models.ForeignKey(ChatSession,related_name='chat_sessions', on_delete=models.CASCADE)
    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

