import requests
import json
from django.shortcuts import render

from django.http import StreamingHttpResponse, JsonResponse
from .models import *
import asyncio
from typing import AsyncIterable
from django.views.decorators.csrf import csrf_exempt
from .tool import *
from .agent import cbfs, CustomAsyncCallbackHandler
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
import time
# from langchain.agents.agent_toolkits import create_retriever_tool


# retriever = RetrieKlook()

# retrietool = create_retriever_tool(
#     retriever,
#     "retriver_klook",
#     "Searches and returns documents regarding the travel information in Vietnam by Klook",
# )

def getHistory(session_id):
    session = ChatSession.objects.get(id=session_id)
    messages = Message.objects.filter(session=session)
    result = [message.data for message in messages ]
    print(str(result))
    return result


def event_stream():
    while True:
        # Simulate a process that periodically generates data
        # This could be any kind of live data update
        yield f"data: The server time is {time.ctime()}\n\n"
        time.sleep(2)  # Pause for a second

tools = [get_current_temperature, search_wikipedia, sqlQuery, retrietool]

@csrf_exempt
def stream_chat(request):
    print(request)
    '''
    {
        'query':'Hello',
        'history':'[{'type': 'human',
                    'data': {'content': 'Chào bạn, mình là Đạt',
                    'additional_kwargs': {},
                    'type': 'human',
                    'example': False}},
                    {'type': 'ai',
                    'data': {'content': 'Chào Đạt! Tôi là trợ lý của bạn. Cần tôi giúp gì hôm nay?',
                    'additional_kwargs': {},
                    'type': 'ai',
                    'example': False}},
                    {'type': 'human',
                    'data': {'content': 'MDC có những sản phẩm nào thế?',
                    'additional_kwargs': {},
                    'type': 'human',
                    'example': False}},
                    {'type': 'ai',
                    'data': {'content': 'MDC có các sản phẩm sau đây:\n1. iMatch - Match, Chat, Date\n2. iVPN\n3. Vise - Video Search Engine\n4. Can Knockdown AR\n5. Can Knockdown AR Pro\n6. Super Bomber Online\n7. Super Tank Online\n8. Friend Locator\n\nBạn có thể tìm hiểu thêm về từng sản phẩm hoặc có câu hỏi cụ thể về sản phẩm nào đó không?',
                    'additional_kwargs': {},
                    'type': 'ai',
                    'example': False}},
    }
    '''
    data = json.loads(request.body)

    message = data['query']
    #history = data['history']
    
    history = '[]'
    if message:
        agentchain = cbfs(tools=tools, chat_history=history)
        print(message)
        stream_it = CustomAsyncCallbackHandler()
        response_stream = agentchain.send_message(message, stream_it)

        return StreamingHttpResponse(response_stream, content_type="text/event-stream")
    else:
        return JsonResponse({'error': 'No message provided'}, status=400)

# Đặt 1 bàn cho bữa ràm tối nay với 

def new_session(request):
    '''
    input: user_id
    '''
    data = json.loads(request.body)
    user = User.objects.get(id=data['user_id'])
    new_chat = ChatSession.objects.create(user=user)
    new_chat.save(force_insert=True)
    session_id = new_chat.id
    return JsonResponse({'session_id':session_id}, status=200)

def old_session(request):
    '''
    input: 
        session_id
    '''
    data = json.loads(request.body)
    session = ChatSession.objects.get(id=data['session_id'])
    messages = Message.objects.filter(session=session)
    result = [message.data for message in messages ]
    return JsonResponse({'data':result}, status=200)
