from django.http import JsonResponse
from django.shortcuts import render
import google.generativeai as genai
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from myapp.models import Product, Category
from django.conf import settings
import json
import traceback

# Configure Gemini
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    # List available models first
    available_models = genai.list_models()
    print("Available models:", [model.name for model in available_models])
    
    # Use the correct model name (usually 'gemini-1.0-pro' or similar)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Test the model
    test_response = model.generate_content("Test connection")
    if test_response and test_response.text:
        print("Gemini API configured successfully")
    else:
        raise Exception("Failed to get test response")
except Exception as e:
    print(f"Critical Error - Gemini Configuration Failed: {str(e)}")
    model = None

def get_product_info():
    try:
        categories = Category.objects.all()
        # Get ALL products instead of just the latest 5
        all_products = Product.objects.all()
        
        # Get price ranges for each category
        price_ranges = {}
        products_by_category = {}
        
        for category in categories:
            products_in_category = Product.objects.filter(category=category)
            if products_in_category.exists():
                min_price = products_in_category.order_by('price').first().price
                max_price = products_in_category.order_by('-price').first().price
                price_ranges[category.name] = {
                    'min': float(min_price),
                    'max': float(max_price)
                }
                # Store products by category
                products_by_category[category.name] = [
                    {
                        "name": p.name,
                        "price": float(p.price),
                        "description": p.description,
                        "stock": p.stock
                    } for p in products_in_category
                ]

        return {
            "categories": [cat.name for cat in categories],
            "all_products": [
                {
                    "name": p.name,
                    "price": float(p.price),
                    "category": p.category.name,
                    "description": p.description,
                    "stock": p.stock
                } for p in all_products
            ],
            "products_by_category": products_by_category,
            "price_ranges": price_ranges
        }
    except Exception as e:
        print(f"Error getting product info: {str(e)}")
        return None

def get_products_by_criteria(category=None, max_price=None, min_price=None):
    try:
        products = Product.objects.all()
        
        if category:
            products = products.filter(category__name__iexact=category)
        
        if max_price:
            products = products.filter(price__lte=max_price)
            
        if min_price:
            products = products.filter(price__gte=min_price)
            
        return products[:5]  # Return top 5 matches
    except Exception as e:
        print(f"Error getting products by criteria: {str(e)}")
        return []

def chat_interface(request):
    return render(request, 'chatbot/chat_interface.html')

@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    try:
        if not model:
            raise Exception("Gemini model not initialized")

        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'response': 'Please enter a message.'})

        # Get product information
        product_info = get_product_info()
        
        # Create a more direct, concise prompt
        prompt = f"""
        You are a concise AI shopping assistant for an electronics store. 
        Store Data:
        Categories: {', '.join(product_info['categories']) if product_info else 'Not available'}
        
        Products by Category:
        {json.dumps(product_info['products_by_category'], indent=2) if product_info else 'Not available'}

        Price Ranges: {json.dumps(product_info['price_ranges'], indent=2) if product_info else 'Not available'}

        User Message: {user_message}

        Instructions:
        1. Keep responses short and direct
        2. If user asks about laptops or any category, list actual products from that category with prices
        3. Format product listings as: Product Name - ₹Price
        4. If no products are available in a category, say "No products available in [category] category"
        5. Don't ask follow-up questions
        6. For greetings, keep it brief and friendly
        7. Maximum 3 lines for responses

        Generate a concise response:
        """

        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 256,
                }
            )

            if not response or not response.text:
                raise Exception("Empty response from Gemini API")

            # Save interaction to database
            from .models import ChatbotResponse
            ChatbotResponse.objects.create(
                query=user_message,
                response=response.text.strip()
            )

            return JsonResponse({'response': response.text.strip()})

        except Exception as e:
            print(f"Generation Error: {str(e)}")
            # For product queries, provide direct database access
            if 'laptop' in user_message.lower() or 'lap' in user_message.lower():
                laptops = Product.objects.filter(category__name__icontains='laptop')
                if laptops.exists():
                    laptop_list = [f"{laptop.name} - ₹{laptop.price}" for laptop in laptops]
                    return JsonResponse({'response': "Available laptops:\n" + "\n".join(laptop_list)})
                else:
                    return JsonResponse({'response': "No laptops currently available in store."})
            return JsonResponse({
                'response': "I'm having trouble accessing the product information. Please try again."
            })

    except Exception as e:
        print(f"Chat Error: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'response': "Service unavailable. Please try again."
        })


