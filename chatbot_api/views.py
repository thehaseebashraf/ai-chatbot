from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatMessageSerializer, DocumentFileSerializer
from .services import ChatbotService
from .models import DocumentFile
from .vector_db import VectorDBService

class ChatbotView(APIView):
    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            chatbot_service = ChatbotService()
            
            user_message = serializer.validated_data['user_message']
            
            # Prepare prompts and get response
            system_prompt, user_prompt = chatbot_service.prepare_prompts(user_message)
            bot_response = chatbot_service.make_api_call(system_prompt, user_prompt)
            
            # Save the chat message and response
            chat_message = serializer.save(bot_response=bot_response)
            
            return Response(ChatMessageSerializer(chat_message).data, status=status.HTTP_201_CREATED)
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

