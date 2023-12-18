from django.shortcuts import render

from django.http import JsonResponse, HttpResponse
from .models import *
import requests

api_key = "b99b731b4d834246a0a84755230512"

def getProductByShop(request):
    products = list(Product.objects.all())
    listproduct = []
    for product in products:
        x = {}
        x['id'] = str(product.pk)
        x['name'] = product.name
        x['price'] = product.price
        x['descript'] = product.getDescrip()
        x['link'] = product.link
        x['shop'] = str(product.shopId)

        listproduct.append(x)
    context = {'listproduct': listproduct}
    return JsonResponse(context)

def get_weather(request, city_name):
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "q": city_name,
        "key": api_key,
        "aqi": "yes"  
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        weather_data = response.json()
        return JsonResponse(weather_data)
    else:
        return None
