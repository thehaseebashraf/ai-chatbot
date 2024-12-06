from rest_framework import serializers
from .models import ChatMessage, ChatSession, DocumentFile

# class ChatMessageSerializer(serializers.ModelSerializer):
#     session_id = serializers.UUIDField(write_only=True, required=False)

#     class Meta:
#         model = ChatMessage
#         fields = ['id', 'user_message', 'bot_response', 'created_at', 'ticket_id', 'session_id']
#         read_only_fields = ['bot_response', 'created_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    session_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = ChatMessage
        fields = ['id', 'user_message', 'bot_response', 'created_at', 'ticket_id', 'session_id']
        read_only_fields = ['bot_response', 'created_at']

    def create(self, validated_data):
        # Remove session_id from validated_data as it's not a model field
        session_id = validated_data.pop('session_id', None)
        
        # If session_id was provided, get the chat session
        if session_id:
            chat_session = ChatSession.objects.get(session_id=session_id)
            validated_data['chat_session'] = chat_session
            
        return super().create(validated_data)

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ['session_id', 'created_at', 'messages']

class DocumentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFile
        fields = ['id', 'file', 'uploaded_at', 'is_processed']
        read_only_fields = ['uploaded_at', 'is_processed']
        
