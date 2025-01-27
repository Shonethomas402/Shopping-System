# # from django.shortcuts import render
# # from django.http import JsonResponse
# # from django.views.decorators.csrf import csrf_exempt

# # @csrf_exempt
# # def chatbot_response(request):
# #     if request.method == "POST":
# #         user_message = request.POST.get("message", "").lower()
# #         print(f"Received message: {user_message}")

# #         responses = {
# #             "hello": "Hi! How can I help you today?",
# #             "hi": "Hello! How can I assist you?",
# #             "help": "I can help you with: \n- Product information\n- Order status\n- Returns\n- Technical support",
# #             "bye": "Goodbye! Have a great day!",
# #             "thanks": "You're welcome!",
# #             "thank you": "You're welcome!",
# #         }

# #         response = responses.get(user_message, "I'm not sure how to respond to that. Can you try rephrasing or ask for 'help' to see what I can do?")
        
# #         return JsonResponse({"reply": response})
    
# #     return JsonResponse({"error": "Invalid request method"}, status=400)
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import ChatbotResponse
# from django.db.models import Q

# @csrf_exempt  # Only for testing, remove in production
# def chatbot_response(request):
#     if request.method == "POST":
#         user_message = request.POST.get("message", "").lower().strip()
        
#         try:
#             # Try to find an exact match first
#             response = ChatbotResponse.objects.filter(
#                 query__iexact=user_message
#             ).first()
            
#             if not response:
#                 # If no exact match, try to find keywords
#                 keywords = user_message.split()
#                 response = ChatbotResponse.objects.filter(
#                     Q(query__icontains=user_message) |
#                     any(Q(query__icontains=keyword) for keyword in keywords)
#                 ).first()
            
#             if response:
#                 return JsonResponse({"reply": response.response})
            
#             # Default response if no match found
#             return JsonResponse({
#                 "reply": "I'm not sure how to respond to that. Please try asking something else or contact our support team."
#             })
            
#         except Exception as e:
#             print(f"Error in chatbot response: {str(e)}")
#             return JsonResponse({
#                 "reply": "Sorry, I encountered an error. Please try again."
#             })
    
#     return JsonResponse({"error": "Invalid request method"}, status=400)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatbotResponse
from django.db.models import Q

@csrf_exempt  # Remove this in production and implement proper CSRF handling
def chatbot_response(request):
    if request.method == "POST":
        user_message = request.POST.get("message", "").lower().strip()
        
        try:
            # Get all responses from the database
            all_responses = ChatbotResponse.objects.all()
            
            # First try exact match
            exact_match = all_responses.filter(query__iexact=user_message).first()
            if exact_match:
                return JsonResponse({"reply": exact_match.response})
            
            # If no exact match, try partial matches
            partial_matches = all_responses.filter(
                Q(query__icontains=user_message) |
                Q(response__icontains=user_message)
            )
            
            if partial_matches.exists():
                # Return the first partial match
                return JsonResponse({"reply": partial_matches.first().response})
            
            # If still no match, try keyword matching
            keywords = user_message.split()
            keyword_matches = all_responses.filter(
                Q(query__iregex=r'(' + '|'.join(keywords) + ')') |
                Q(response__iregex=r'(' + '|'.join(keywords) + ')')
            )
            
            if keyword_matches.exists():
                return JsonResponse({"reply": keyword_matches.first().response})
            
            # If no matches found, return default response
            return JsonResponse({
                "reply": "I'm not sure how to help with that. Try asking about our products, shipping, or contact information."
            })
            
        except Exception as e:
            print(f"Error in chatbot response: {str(e)}")
            return JsonResponse({
                "reply": "Sorry, I encountered an error. Please try again."
            })
    
    return JsonResponse({"error": "Invalid request method"}, status=400)
