from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

class ProductRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.similarity_matrix = None
        self.products_df = None

    def prepare_data(self, products):
        # Convert QuerySet to DataFrame
        self.products_df = pd.DataFrame(list(products))
        
        # Create a combined features string
        self.products_df['combined_features'] = self.products_df.apply(
            lambda x: f"{x['name']} {x['description']}", 
            axis=1
        )
        
        # Create TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(
            self.products_df['combined_features'].fillna('')
        )
        
        # Calculate similarity matrix
        self.similarity_matrix = cosine_similarity(tfidf_matrix)

    def get_recommendations(self, product_id, num_recommendations=4):
        try:
            # Find the index of the product
            product_idx = self.products_df[
                self.products_df['id'] == product_id
            ].index[0]
            
            # Get similarity scores
            similarity_scores = list(enumerate(
                self.similarity_matrix[product_idx]
            ))
            
            # Sort by similarity
            similarity_scores = sorted(
                similarity_scores, 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Get top similar products (excluding itself)
            similar_products = similarity_scores[1:num_recommendations+1]
            
            # Get the IDs of recommended products
            recommended_ids = [
                self.products_df.iloc[score[0]]['id'] 
                for score in similar_products
            ]
            
            return recommended_ids
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []