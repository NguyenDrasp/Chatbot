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
from langchain.agents.agent_toolkits import create_retriever_tool
import time


retriever = createRetrieval()

retrietool = create_retriever_tool(
    retriever,
    "retriver_klook",
    "This tool retrieves travel-related documents based on queries.",
)
tools = [get_current_temperature, search_wikipedia, sqlQuery, retrietool]

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

agentchain = cbfs(tools=tools, chat_history='[]')


"""
Luồng: Khi có một yêu cầu chat, sẽ thay đổi lịch sử của agentchain, sau đó chạy và gửi lại.
khi chọn 1 session cũ thì sẽ gửi về lịch sử của section đó
khi chọn 1 session mới: sẽ tạo 1 session_chat mới và gửi về id của session đó.
Sau khi hết phiên: người dùng rời page, lòa lại page, tạo 1 session mới, sẽ lưu lại history của session đó.
"""
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
                    'example': False}}
                    ]',
    }
    '''
    data = json.loads(request.body)

    
    message = data['query']
    chat_history = data['history']
    print(chat_history)
    agentchain.set_history(chat_history)
    if message:
        print(message)
        stream_it = CustomAsyncCallbackHandler()
        response_stream = agentchain.send_message(message, stream_it)

        return StreamingHttpResponse(response_stream, content_type="text/event-stream")
    else:
        return JsonResponse({'error': 'No message provided'}, status=400)

# Đặt 1 bàn cho bữa ràm tối nay với 

@csrf_exempt
def new_session(request):
    '''
    input: user_id
    '''
    data = json.loads(request.body)
    try:
        user_id = int(data['user_id'])
        user = User.objects.get(id=user_id)
        new_chat = ChatSession.objects.create(user=user)
        new_chat.save()
        session_id = new_chat.id
        return JsonResponse({'session_id':session_id, 'history':'[]'}, status=200)
    except:
        return JsonResponse({'error': 'No or wrong userid'}, status=400)

@csrf_exempt
def old_session(request):
    '''
    {
        'session_id': '123'
    }    
    '''
    data = json.loads(request.body)
    session = ChatSession.objects.get(id=data['session_id'])
    #messages = Message.objects.filter(session=session)
    #result = [message.data for message in messages ]
    history = session.data
    return JsonResponse({'data':history}, status=200)

@csrf_exempt
def list_session(request):
    '''
    {
        'user_id': '123'
    }    
    '''
    data = json.loads(request.body)
    try:
        user_id = int(data['user_id'])
        
        user = User.objects.get(id = user_id)
        sessions = ChatSession.objects.filter(user=user)
        list_id = [i.id for i in sessions]

        return JsonResponse({'session_ids':list_id}, status=200)
    except:
        return JsonResponse({'error': 'No or wrong userid'}, status=400)
@csrf_exempt
def save_history(request):
    '''
    {
        'session_id':'123',
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
                    'example': False}}
                    ]',
    }
    '''

    data = json.loads(request.body)
    print(data)
    session_id  = data['session_id']
    if session_id:
        session = ChatSession.objects.get(id=session_id)
        if data['history']:
            session.data = data['history']
            session.save()
            return JsonResponse({'success': "Oke nhe em iu"}, status=200)
        else: 
            return JsonResponse({'error': 'No history provided'}, status=400)

    else:
        return JsonResponse({'error': 'No session_id provided'}, status=400)
    