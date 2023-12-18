from django.db import models
from .crawl import get_des
from agent.models import User
# Create your models here.
class Shop(models.Model):
    name = models.CharField(max_length=100)
    apikey = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner", null=True)

    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    shopId = models.ForeignKey(Shop, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    create_at = models.DateTimeField(auto_now_add=True)
    link = models.TextField()

    def __str__(self) -> str:
        return self.name
    
    def getDescrip(self):
        return get_des(self.link)
    
