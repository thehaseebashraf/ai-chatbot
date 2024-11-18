from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_message', 'bot_response', 'created_at', 'ticket_id')
    list_filter = ('created_at', 'ticket_id')
    search_fields = ('user_message', 'bot_response', 'ticket_id')
    readonly_fields = ('created_at',)
    
    
    
    # checking changes to new branch
    # new branch