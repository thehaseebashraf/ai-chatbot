from .vector_db import VectorDBService
import os
import requests

class ChatbotService:
    def __init__(self):
        self.vector_db = VectorDBService()

    def format_conversation_history(self, messages):
        """Format conversation history into OpenAI message format"""
        formatted_messages = [
            {
                "role": "system",
                "content": """You are a friendly AI solutioninn customer support agent and will help to answer user queries with greetings and an ending signature. 
                            Empathise with the user and maintain a supportive tone throughout the conversation. 
                            Look at the question and answer the query according only to the given context.
                            You will also be given the complete conversation history for the given complaint, look at that and respond to the latest customer query. 
                            Also look at our latest response as well, that will give you the current progress of the ticket, don't generate responses that contradict our previous responses.
                            Don't ask the user to perform too many tasks or check different things, just focus on what you can provide them with.
                            Ask the user for more information only in case the provided information is not sufficient.
                            If a query relates to account issues, refunds, or technical problems, provide clear steps or explanations when possible or say if the issue persists, the request will be forwarded to the technical team and they will get back to you.
                            If anyone is promoting their services, answer them politely and say that we are not in need right now and don't require the services.
                            If you cannot find the relevant information, try to answer to the best of your knowledge but be specific in your answers and don't provide generic responses.
                            Avoid phrases like "I don't know" or "I'm unable to provide information." Instead, focus on what you can do or explain.
                            Keep your answers concise, short and to the point.
                            Don't ask the user to contact the bank in case of refunds or other charges, you are responsible for performing the refunds for the user.
                            Don't ask the user to reach out to support@solutioninn.com or refer to external support or any other form of support, you're the solutioninn support."""
            }
        ]

        # Add context from vector DB if it's the first message
        if messages.exists():
            latest_message = messages.latest('created_at')
            search_results = self.vector_db.search(latest_message.user_message, top_k=3)
            context = "\n".join([result.payload['content'] for result in search_results])
            
            if context.strip():
                formatted_messages[0]["content"] += f"\n\nContext: {context}"

        # Add conversation history
        for message in messages:
            formatted_messages.extend([
                {"role": "user", "content": message.user_message},
                {"role": "assistant", "content": message.bot_response}
            ])

        return formatted_messages

    def make_api_call(self, messages):
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found")
        
        try:
            response = requests.post(
                url="https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "temperature": 0.3
                }
            )
            
            response.raise_for_status()
            response_json = response.json()
            
            if 'error' in response_json:
                raise Exception(f"OpenAI API Error: {response_json['error']}")
            
            return response_json['choices'][0]['message']['content']
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"API call failed: {str(e)}")
