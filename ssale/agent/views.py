import requests
import json
from django.shortcuts import render

from django.http import StreamingHttpResponse, JsonResponse
from .models import *
import asyncio
from typing import AsyncIterable
from django.views.decorators.csrf import csrf_exempt
from .tool import *
from .agent import cbfs, AsyncCallbackHandler
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
import time
def event_stream():
    while True:
        # Simulate a process that periodically generates data
        # This could be any kind of live data update
        yield f"data: The server time is {time.ctime()}\n\n"
        time.sleep(2)  # Pause for a second

tools = [get_current_temperature, search_wikipedia, sqlQuery]
@csrf_exempt
def stream_chat(request):
    print(request)
    data = json.loads(request.body)
    message = data['query']
    if message:
        print(message)
        agentchain = cbfs(tools=tools, chat_history='[]')
        stream_it = AsyncIteratorCallbackHandler()
        response_stream = agentchain.send_message(message, stream_it)
        return StreamingHttpResponse(response_stream, content_type="text/event-stream")
    else:
        return JsonResponse({'error': 'No message provided'}, status=400)

# Đặt 1 bàn cho bữa ràm tối nay với 