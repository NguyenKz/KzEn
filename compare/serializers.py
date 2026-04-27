"""DRF serializers — mirror cấu trúc kzen.schemas (không duplicate logic)."""
from __future__ import annotations

from rest_framework import serializers


class DiffResultSerializer(serializers.Serializer):
    ref_text = serializers.CharField()
    stt_text = serializers.CharField()
    type = serializers.CharField()


class CompareResultSerializer(serializers.Serializer):
    diff_results = DiffResultSerializer(many=True)
    iou_level = serializers.CharField()
    iou = serializers.IntegerField(min_value=0, max_value=100)


def compare_result_to_api_dict(result) -> dict:
    """Chuyển kzen CompareResult (Pydantic) → dict cho serializer."""
    return result.model_dump(mode="json")
