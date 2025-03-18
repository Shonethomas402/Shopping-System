import google.generativeai as genai
from django.conf import settings
import logging
import json

logger = logging.getLogger(__name__)

class ProductSummarizer:
    def __init__(self):
        try:
            logger.info("Initializing ProductSummarizer with Gemini")
            # Use the API key from settings
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Try to use gemini-1.5-pro first
            try:
                self.model = genai.GenerativeModel('models/gemini-1.5-pro')
                self.available = True
                logger.info("ProductSummarizer initialized with gemini-1.5-pro model")
            except Exception as model_error:
                logger.warning(f"Could not initialize gemini-1.5-pro model: {str(model_error)}")
                
                # Try to find any available text generation model
                try:
                    available_models = genai.list_models()
                    logger.info(f"Available models: {[m.name for m in available_models]}")
                    
                    # Look for specific models in order of preference
                    preferred_models = [
                        'models/gemini-1.5-pro',
                        'models/gemini-2.0-pro-exp',
                        'models/text-bison-001'  # Fallback to text-bison if available
                    ]
                    
                    for model_name in preferred_models:
                        if any(m.name == model_name for m in available_models):
                            self.model = genai.GenerativeModel(model_name)
                            self.available = True
                            logger.info(f"Using model: {model_name}")
                            break
                    else:
                        # If none of the preferred models are available
                        for model in available_models:
                            if 'generateContent' in model.supported_generation_methods:
                                self.model = genai.GenerativeModel(model.name)
                                self.available = True
                                logger.info(f"Using fallback model: {model.name}")
                                break
                        else:
                            raise Exception("No suitable Gemini model available")
                except Exception as e:
                    logger.error(f"Could not find any suitable model: {str(e)}")
                    raise
        except Exception as e:
            logger.error(f"Error initializing ProductSummarizer: {str(e)}", exc_info=True)
            self.available = False

    def generate_summary(self, products, min_price=None, max_price=None, category_name=None):
        """
        Generate a summary of the products based on price range and category
        
        Args:
            products: List of product objects
            min_price: Minimum price filter (optional)
            max_price: Maximum price filter (optional)
            category_name: Category name
            
        Returns:
            dict: Summary information including best value, premium pick, etc.
        """
        try:
            # Add this at the start of the method
            logger.debug(f"Received {len(products)} products for summary")
            for product in products:
                logger.debug(f"Product: {product.name} - Price: {product.price}")
            
            # Check if we have enough products to make a meaningful comparison
            if not self.available or not products or len(products) < 2:
                logger.warning(f"ProductSummarizer not available or not enough products ({len(products) if products else 0})")
                return self._get_default_summary()
                
            # Format products for the prompt
            product_list = []
            for product in products:
                product_list.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'description': product.description[:200] if product.description else "No description available",
                    'stock': product.stock
                })
                
            # Create price range text
            price_range_text = ""
            if min_price and max_price:
                price_range_text = f"between ₹{min_price} and ₹{max_price}"
            elif min_price:
                price_range_text = f"above ₹{min_price}"
            elif max_price:
                price_range_text = f"below ₹{max_price}"
                
            # Construct the prompt
            prompt = self._construct_prompt(product_list, price_range_text, category_name)
            
            # Generate content
            logger.info(f"Sending request to Gemini for product summary with {len(product_list)} products")
            response = self.model.generate_content(prompt)
            
            # Process the response
            summary = self._process_response(response.text, product_list)
            logger.info("Successfully generated product summary")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating product summary: {str(e)}", exc_info=True)
            return self._get_default_summary()
            
    def _construct_prompt(self, products, price_range_text, category_name):
        """Construct the prompt for Gemini"""
        products_text = "\n".join([
            f"Product {i+1}: {p['name']} - ₹{p['price']} - {p['description'][:100]}..." 
            for i, p in enumerate(products)
        ])
        
        prompt = f"""
        As a shopping assistant, analyze these {category_name} products {price_range_text if price_range_text else ''}:
        
        {products_text}
        
        Provide a concise summary with these sections:
        1. Best Value Pick: The product with the best price-to-features ratio
        2. Premium Pick: The highest quality product (usually higher priced)
        3. Budget Pick: The most affordable decent option
        4. Quick Comparison: Brief 1-2 sentence comparison of the options
        
        Format your response as JSON with these exact keys:
        {{
            "best_value": {{
                "name": "Product name",
                "reason": "Brief reason why it's the best value"
            }},
            "premium_pick": {{
                "name": "Product name",
                "reason": "Brief reason why it's premium"
            }},
            "budget_pick": {{
                "name": "Product name",
                "reason": "Brief reason why it's good for budget"
            }},
            "comparison": "Your 1-2 sentence comparison"
        }}
        
        Only include the JSON in your response, nothing else.
        """
        return prompt
        
    def _process_response(self, response_text, products):
        """Process the response from Gemini"""
        try:
            # Clean the response text to extract just the JSON
            cleaned_text = response_text.strip()
            
            # If the response is wrapped in ```json and ```, remove them
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
                
            cleaned_text = cleaned_text.strip()
            logger.debug(f"Cleaned response text: {cleaned_text[:100]}...")
            
            # Parse the JSON
            try:
                summary = json.loads(cleaned_text)
            except json.JSONDecodeError:
                # Try to extract JSON if it's embedded in other text
                import re
                json_match = re.search(r'({.*})', cleaned_text, re.DOTALL)
                if json_match:
                    try:
                        summary = json.loads(json_match.group(1))
                    except:
                        raise ValueError("Could not extract valid JSON from response")
                else:
                    raise ValueError("Response does not contain valid JSON")
            
            # Ensure all required keys are present
            required_keys = ['best_value', 'premium_pick', 'budget_pick', 'comparison']
            for key in required_keys:
                if key not in summary:
                    summary[key] = self._get_default_summary()[key]
                elif isinstance(summary[key], dict):
                    for subkey in ['name', 'reason']:
                        if subkey not in summary[key]:
                            summary[key][subkey] = "Not specified"
                            
            return summary
            
        except Exception as e:
            logger.error(f"Error processing Gemini response: {str(e)}", exc_info=True)
            logger.debug(f"Problematic response: {response_text}")
            return self._get_default_summary()
            
    def _get_default_summary(self):
        """Return a default summary when Gemini is unavailable or errors occur"""
        return {
            "best_value": {
                "name": "Not available",
                "reason": "Unable to determine best value product"
            },
            "premium_pick": {
                "name": "Not available",
                "reason": "Unable to determine premium product"
            },
            "budget_pick": {
                "name": "Not available",
                "reason": "Unable to determine budget product"
            },
            "comparison": "Product comparison is currently unavailable. Please compare the products manually based on their specifications and prices."
        }

    def generate_test_summary(self, products):
        """Generate a test summary without using the API (for debugging)"""
        if not products or len(list(products)) < 2:
            print("Not enough products for test summary")
            return self._get_default_summary()
        
        # Convert QuerySet to list if needed
        products_list = list(products)
        print(f"Generating test summary for {len(products_list)} products")
        
        # Sort products by price
        sorted_products = sorted(products_list, key=lambda p: float(p.price))
        
        # Get budget, mid-range and premium products
        budget_product = sorted_products[0]
        premium_product = sorted_products[-1]
        
        # Find a mid-range product for best value
        if len(sorted_products) >= 3:
            best_value_product = sorted_products[len(sorted_products) // 2]
        else:
            best_value_product = sorted_products[0]
        
        summary = {
            "best_value": {
                "name": best_value_product.name,
                "reason": "This product offers a good balance of features and price."
            },
            "premium_pick": {
                "name": premium_product.name,
                "reason": "This is the highest-priced option with premium features."
            },
            "budget_pick": {
                "name": budget_product.name,
                "reason": "This is the most affordable option in this category."
            },
            "comparison": f"Prices range from ₹{budget_product.price} to ₹{premium_product.price}. Choose based on your budget and feature requirements."
        }
        
        print(f"Test summary generated successfully: {summary}")
        return summary 