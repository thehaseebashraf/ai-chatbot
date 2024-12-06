from django.db import models
import uuid

class ChatSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat Session {self.session_id}"

class ChatMessage(models.Model):
    chat_session = models.ForeignKey(
        ChatSession, 
        related_name='messages', 
        on_delete=models.CASCADE,
    )
    user_message = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ticket_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Chat {self.id} - {self.created_at}"

class DocumentFile(models.Model):
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Document {self.id} - {self.uploaded_at}"
