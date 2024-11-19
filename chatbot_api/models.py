from django.db import models

class ChatMessage(models.Model):
    user_message = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ticket_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Chat {self.id} - {self.created_at}"

class DocumentFile(models.Model):
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Document {self.id} - {self.uploaded_at}"
