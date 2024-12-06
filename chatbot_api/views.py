from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatMessageSerializer, DocumentFileSerializer, ChatSessionSerializer
from .services import ChatbotService
from .models import DocumentFile, ChatSession
from .vector_db import VectorDBService
from .constants.chat_constants import ChatLimits, ErrorMessages, ResponseMessages


class ChatbotView(APIView):
    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            # Get or create chat session
            session_id = serializer.validated_data.get('session_id')
            if session_id:
                chat_session = ChatSession.objects.filter(session_id=session_id).first()
                if not chat_session:
                    return Response(
                        {'error': ErrorMessages.INVALID_SESSION}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Check message count for this session
                message_count = chat_session.messages.count()
                if message_count >= ChatLimits.FREE_TIER_MESSAGE_LIMIT:
                    return Response({
                        'error': 'Message limit exceeded',
                        'message': ErrorMessages.LIMIT_EXCEEDED.format(
                            limit=ChatLimits.FREE_TIER_MESSAGE_LIMIT
                        ),
                        'message_count': message_count,
                        'limit': ChatLimits.FREE_TIER_MESSAGE_LIMIT
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                chat_session = ChatSession.objects.create()

            chatbot_service = ChatbotService()
            
            # Get conversation history and format messages
            previous_messages = chat_session.messages.all().order_by('created_at')
            formatted_messages = chatbot_service.format_conversation_history(previous_messages)
            
            # Add the new user message
            formatted_messages.append({
                "role": "user", 
                "content": serializer.validated_data['user_message']
            })
            
            # Get bot response
            bot_response = chatbot_service.make_api_call(formatted_messages)
            
            # Save the chat message
            chat_message = serializer.save(
                bot_response=bot_response,
                chat_session=chat_session
            )
            
            # Get updated message count
            current_message_count = chat_session.messages.count()
            remaining_messages = ChatLimits.FREE_TIER_MESSAGE_LIMIT - current_message_count
            
            response_data = ChatMessageSerializer(chat_message).data
            response_data['session_id'] = chat_session.session_id
            response_data['remaining_messages'] = remaining_messages
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DocumentUploadView(APIView):
    def post(self, request):
        serializer = DocumentFileSerializer(data=request.data)
        if serializer.is_valid():
            # Delete all previous documents
            DocumentFile.objects.all().delete()
            
            # Save new document
            document = serializer.save()
            
            # Initialize vector DB with the new file
            vector_db = VectorDBService()
            try:
                # This will now clear previous embeddings and add new ones
                vector_db.initialize_vector_db(document.file.path)
                document.is_processed = True
                document.save()
                return Response(DocumentFileSerializer(document).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DebugContextView(APIView):
    def post(self, request):
        question = request.data.get('question', '')
        if not question:
            return Response({'error': 'Question is required'}, status=status.HTTP_400_BAD_REQUEST)

        vector_db = VectorDBService()
        search_results = vector_db.search(question, top_k=3)
        
        # Format the results for debugging
        context_results = [{
            'content': result.payload['content'],
            'score': result.score,
            'id': result.id
        } for result in search_results]

        return Response({
            'question': question,
            'context_results': context_results,
            'current_document': DocumentFile.objects.last().file.name if DocumentFile.objects.exists() else None
        })

class ChatHistoryView(APIView):
    def get(self, request, session_id):
        try:
            chat_session = ChatSession.objects.get(session_id=session_id)
            serializer = ChatSessionSerializer(chat_session)
            return Response(serializer.data)
        except ChatSession.DoesNotExist:
            return Response(
                {'error': 'Chat session not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )