from django.db import models

# Create your models here.
from django.db import models

class ChatbotResponse(models.Model):
    query = models.CharField(max_length=200)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.query}"

    class Meta:
        ordering = ['query']