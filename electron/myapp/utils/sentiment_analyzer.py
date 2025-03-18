from textblob import TextBlob
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import google.generativeai as genai
from django.conf import settings
import logging

# Set up logger
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        try:
            logger.info("Initializing SentimentAnalyzer components...")
            self.vader = SentimentIntensityAnalyzer()
            logger.info("VADER initialized successfully")
            
            logger.info("Loading BERT model...")
            self.transformer = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment"
            )
            logger.info("BERT model loaded successfully")
            
            # Initialize Gemini
            logger.info("Initializing Gemini...")
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Try to use gemini-1.5-pro first
            try:
                self.gemini_model = genai.GenerativeModel('models/gemini-1.5-pro')
                self.gemini_available = True
                logger.info("Gemini initialized with gemini-1.5-pro model")
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
                        'models/text-bison-001'
                    ]
                    
                    for model_name in preferred_models:
                        if any(m.name == model_name for m in available_models):
                            self.gemini_model = genai.GenerativeModel(model_name)
                            self.gemini_available = True
                            logger.info(f"Using model: {model_name}")
                            break
                    else:
                        # If none of the preferred models are available
                        for model in available_models:
                            if 'generateContent' in model.supported_generation_methods:
                                self.gemini_model = genai.GenerativeModel(model.name)
                                self.gemini_available = True
                                logger.info(f"Using fallback model: {model.name}")
                                break
                        else:
                            raise Exception("No suitable Gemini model available")
                except Exception as e:
                    logger.error(f"Could not find any suitable model: {str(e)}")
                    self.gemini_available = False
                    
        except Exception as e:
            logger.error(f"Error in SentimentAnalyzer initialization: {str(e)}", exc_info=True)
            self.gemini_available = False

    def analyze(self, text):
        try:
            logger.info(f"Analyzing text: {text[:100]}...")  # Log first 100 chars
            
            # VADER Analysis
            logger.debug("Running VADER analysis...")
            vader_scores = self.vader.polarity_scores(text)
            logger.debug(f"VADER scores: {vader_scores}")
            
            # TextBlob Analysis
            logger.debug("Running TextBlob analysis...")
            blob = TextBlob(text)
            textblob_score = blob.sentiment.polarity
            logger.debug(f"TextBlob score: {textblob_score}")
            
            # Transformer Analysis
            logger.debug("Running Transformer analysis...")
            transformer_result = self.transformer(text)[0]
            transformer_score = float(transformer_result['label'].split()[0]) / 5.0
            logger.debug(f"Transformer score: {transformer_score}")

            # Combine scores
            combined_score = (
                vader_scores['compound'] * 0.4 +
                textblob_score * 0.3 +
                transformer_score * 0.3
            )
            logger.info(f"Combined sentiment score: {combined_score}")

            # Determine sentiment label
            if combined_score >= 0.05:
                label = 'positive'
            elif combined_score <= -0.05:
                label = 'negative'
            else:
                label = 'neutral'
            logger.info(f"Determined sentiment label: {label}")

            # Generate response message
            response_message = self.generate_response(text, label, combined_score)
            
            result = {
                'score': combined_score,
                'label': label,
                'response_message': response_message,
                'details': {
                    'vader': vader_scores,
                    'textblob': textblob_score,
                    'transformer': transformer_score
                }
            }
            logger.info("Analysis completed successfully")
            return result

        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}", exc_info=True)
            raise
        
    def generate_response(self, text, sentiment, score):
        """Generate appropriate response based on sentiment"""
        try:
            logger.info(f"Generating response for sentiment: {sentiment}")
            
            # Default responses
            default_responses = {
                'positive': "Thank you for your positive feedback! We're glad you enjoyed our product.",
                'neutral': "Thank you for your feedback. We appreciate your input.",
                'negative': "We apologize for your experience. We take your feedback seriously and will work to improve."
            }
            
            if not self.gemini_available:
                logger.info("Using default response (Gemini not available)")
                return default_responses[sentiment]
                
            # Use Gemini to generate response
            prompt = f"""
            As a customer service AI, generate a brief, personalized response to this customer feedback.
            
            Customer feedback: "{text}"
            Sentiment analysis shows this is a {sentiment.upper()} review with a score of {score:.2f}.
            
            If positive: Express gratitude and enthusiasm.
            If neutral: Thank them for the feedback and encourage future purchases.
            If negative: Apologize sincerely, show empathy, and offer to make it right.
            
            Keep the response under 2 sentences, friendly, and professional.
            """
            
            logger.debug("Sending prompt to Gemini")
            response = self.gemini_model.generate_content(prompt)
            logger.info("Successfully generated Gemini response")
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            return default_responses[sentiment]