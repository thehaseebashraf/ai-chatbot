from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatMessageSerializer
from .services import ChatbotService

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

