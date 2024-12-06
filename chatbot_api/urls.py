from django.urls import path
from .views import ChatbotView, DocumentUploadView, ChatHistoryView, DebugContextView

urlpatterns = [
    path('chat/', ChatbotView.as_view(), name='chat'),
    path('chat/history/<uuid:session_id>/', ChatHistoryView.as_view(), name='chat-history'),
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('debug-context/', DebugContextView.as_view(), name='debug-context'),
]
