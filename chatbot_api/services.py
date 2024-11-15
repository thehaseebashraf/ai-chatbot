from .vector_db import VectorDBService
import os

class ChatbotService:
    def __init__(self):
        self.vector_db = VectorDBService()

    def prepare_prompts(self, question, name="User", conversation=""):
        # Search for relevant context
        search_results = self.vector_db.search(question, top_k=3)
        context = "\n".join([result.payload['content'] for result in search_results])
        
        if not context.strip():
            context = "No context found"

        system_prompt = f"""You are a friendly AI solutioninn customer support agent and will help to answer user queries with greetings and an ending signature. 
        Empathise with the user and maintain a supportive tone throughout the conversation. 
        Look at the question and answer the query according only to the given context.
        Keep your answers concise, short and to the point.
        Context: {context}
        """

        user_prompt = f"""
        Question: {question}
        Conversation history: {conversation}
        """

        return system_prompt, user_prompt

    def make_api_call(self, system_prompt, user_prompt):
        import requests
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')        
        response = requests.post(
            url="https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3
            }
        )
        
        response_json = response.json()
        return response_json['choices'][0]['message']['content']
