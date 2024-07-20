from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from django.http import StreamingHttpResponse
import json
import time
import random

from app.utils import chat_with_openai


def index_page(request):
    return render(request, "index.html")


@csrf_exempt
def chat_stream(request):
    message = request.GET.get('message', '')

    def event_stream():
        # 응답을 한 글자씩 스트리밍
        for char in chat_with_openai(message):
            yield f"data: {json.dumps({'message': char})}\n\n"
        else:
            yield f"data: {json.dumps({'message': '[END]'})}\n\n"

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


