from django.urls import path
from .views import ChatbotView, DocumentUploadView, DebugContextView

urlpatterns = [
    path('chat/', ChatbotView.as_view(), name='chat'),
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('debug-context/', DebugContextView.as_view(), name='debug-context'),
]
