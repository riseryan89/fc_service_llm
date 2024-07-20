from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from django.http import StreamingHttpResponse
import json
import time
import random


def index_page(request):
    return render(request, "index.html")


@csrf_exempt
def chat_stream(request):
    message = request.GET.get('message', '')

    def event_stream():
        # 미리 정의된 더미 응답들
        dummy_responses = [
            f"안녕하세요! '{message}'에 대한 답변을 생각해보겠습니다.",
            f"흥미로운 질문이네요. '{message}'에 대해 이렇게 생각해볼 수 있겠어요.",
            f"'{message}'라는 메시지를 받았습니다. 제 의견은 다음과 같아요.",
            f"'{message}'에 대해 말씀드리자면, 여러 가지 측면에서 볼 수 있습니다.",
            f"'{message}'라는 주제는 매우 복잡한데, 간단히 설명해보겠습니다."
        ]

        # 랜덤하게 하나의 응답 선택
        response = random.choice(dummy_responses)

        # 응답을 한 글자씩 스트리밍
        for char in response:
            yield f"data: {json.dumps({'message': char})}\n\n"
            time.sleep(0.05)  # 각 글자 사이에 약간의 지연
        else:
            yield f"data: {json.dumps({'message': '[END]'})}\n\n"

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
