from __future__ import annotations

import json
import random

from django.http import FileResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .passages import PASSAGES
from .serializers import CompareResultSerializer, compare_result_to_api_dict
from .services import transcribe_upload_and_compare
from .tts_service import get_or_create_tts_mp3, preprocess_text_for_tts


@ensure_csrf_cookie
def home(request):
    passage = random.choice(PASSAGES)
    return render(
        request,
        "compare/home.html",
        {"passage": passage},
    )


class CompareApiView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        ref = (request.data.get("reference_text") or "").strip()
        audio = request.FILES.get("audio")
        if not ref:
            return Response({"detail": "Thiếu reference_text."}, status=400)
        if not audio:
            return Response({"detail": "Thiếu file audio."}, status=400)
        try:
            stt_text, result = transcribe_upload_and_compare(audio, ref)
        except Exception as e:
            return Response({"detail": str(e)}, status=500)
        payload = compare_result_to_api_dict(result)
        ser = CompareResultSerializer(data=payload)
        ser.is_valid(raise_exception=True)
        return Response(
            {
                "stt_text": stt_text,
                "compare": ser.data,
            }
        )


@require_POST
def tts_api(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("JSON không hợp lệ.")
    text = data.get("text") or ""
    pre = preprocess_text_for_tts(text)
    if not pre:
        return HttpResponseBadRequest("Text rỗng.")
    if len(pre) > 4000:
        return HttpResponseBadRequest("Text quá dài.")
    try:
        path = get_or_create_tts_mp3(pre)
    except Exception as e:
        return HttpResponseBadRequest(str(e))
    return FileResponse(open(path, "rb"), content_type="audio/mpeg")
