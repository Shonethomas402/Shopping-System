import google.generativeai as genai
from django.conf import settings

# Configure Gemini API
genai.configure(api_key='AIzaSyBLSAPqtZQ4KhCTNP9zkM2Dke9giqwhENc')

class GeminiRecommender:
    def __init__(self):
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-pro')

    def get_recommendations(self, user_preferences):
        """Generate personalized product recommendations using Gemini AI"""
        try:
            # Construct the prompt
            prompt = self._construct_prompt(user_preferences)
            
            # Generate response from Gemini
            response = self.model.generate_content(prompt)
            
            # Process and return the recommendations
            return self._process_response(response.text, user_preferences.get('brand', ''))
        except Exception as e:
            print(f"Error in Gemini recommendation: {str(e)}")
            return None

    def _construct_prompt(self, preferences):
        """Construct a detailed prompt for Gemini based on user preferences"""
        brand_text = preferences.get('brand', '').strip()
        category = preferences.get('category', 'Any')
        min_price = preferences.get('min_price', '0')
        max_price = preferences.get('max_price', 'Any')
        specs = preferences.get('specifications', 'None specified')

        if brand_text:
            prompt = f"""
            Act as an expert {brand_text.upper()} product specialist. I need specific product recommendations for {brand_text} products only.

            Requirements:
            - Category: {category}
            - Brand: {brand_text.upper()} products ONLY
            - Budget Range: ₹{min_price} - ₹{max_price}
            - Specifications Needed: {specs}

            Please recommend ONLY {brand_text.upper()} products that match these criteria.
            Provide exactly 3 best {brand_text} products in this format:
            1. {brand_text} Product Name | Key Features | Price | Why this {brand_text} model is suitable
            2. {brand_text} Product Name | Key Features | Price | Why this {brand_text} model is suitable
            3. {brand_text} Product Name | Key Features | Price | Why this {brand_text} model is suitable

            Ensure:
            - All products are from {brand_text.upper()} only
            - Latest models from {brand_text}
            - Within specified budget range
            - Match required specifications
            - Include actual model numbers where possible
            """
        else:
            prompt = f"""
            Act as an expert electronics product recommender. Suggest the best products from any brand:

            Requirements:
            - Category: {category}
            - Budget Range: ₹{min_price} - ₹{max_price}
            - Specifications Needed: {specs}

            Please provide 3 recommendations in this format:
            1. Product Name | Key Features | Price | Why it's suitable
            2. Product Name | Key Features | Price | Why it's suitable
            3. Product Name | Key Features | Price | Why it's suitable

            Focus on:
            - Best value for money
            - Latest models
            - Match required specifications
            - Quality and reliability
            """
        return prompt

    def _process_response(self, response_text, brand=''):
        """Process Gemini's response into structured recommendations"""
        try:
            recommendations = []
            lines = [line.strip() for line in response_text.split('\n') if line.strip()]
            
            for line in lines:
                if line[0].isdigit() and '|' in line:
                    parts = [part.strip() for part in line.split('|')]
                    if len(parts) >= 3:
                        product_name = parts[0].split('.')[1].strip() if '.' in parts[0] else parts[0]
                        
                        # If brand is specified, verify the product contains the brand name
                        if not brand or brand.lower() in product_name.lower():
                            rec = {
                                'name': product_name,
                                'features': parts[1].strip(),
                                'price': parts[2].strip(),
                                'reason': parts[3].strip() if len(parts) > 3 else '',
                                'brand': brand if brand else 'Various Brands'
                            }
                            recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            print(f"Error processing Gemini response: {str(e)}")
            return [] 