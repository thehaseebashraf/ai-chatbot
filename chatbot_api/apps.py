from django.apps import AppConfig


class ChatbotApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chatbot_api"

    def ready(self):
        from .vector_db import VectorDBService
        # Initialize the vector DB only once when Django starts
        VectorDBService.initialize_singleton()
