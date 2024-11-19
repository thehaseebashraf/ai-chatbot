from rest_framework import serializers
from .models import ChatMessage, DocumentFile

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'user_message', 'bot_response', 'created_at', 'ticket_id']
        read_only_fields = ['bot_response', 'created_at']

class DocumentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFile
        fields = ['id', 'file', 'uploaded_at', 'is_processed']
        read_only_fields = ['uploaded_at', 'is_processed']