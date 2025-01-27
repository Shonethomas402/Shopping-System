from django.contrib import admin
from .models import ChatbotResponse

@admin.register(ChatbotResponse)
class ChatbotResponseAdmin(admin.ModelAdmin):
    list_display = ['query', 'response', 'updated_at']
    search_fields = ['query', 'response']
    list_filter = ['created_at', 'updated_at']
