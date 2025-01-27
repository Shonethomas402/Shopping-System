from django.urls import path, include
from . import views 

urlpatterns = [
    # ... your other URLs ...
    #path('chatbot/', include('chatbot.urls')),
    path('response/', views.chatbot_response, name='chatbot_response'),

]