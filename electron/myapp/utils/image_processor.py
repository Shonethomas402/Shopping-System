import torch
from torchvision import transforms, models
import numpy as np
from PIL import Image
from scipy.spatial.distance import cosine
import logging
import torchvision.models as models

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        # Load pretrained ResNet model for feature extraction
        self.feature_model = models.resnet50(pretrained=True)
        self.feature_model.eval()
        self.feature_extractor = torch.nn.Sequential(*(list(self.feature_model.children())[:-1]))
        
        # Load pretrained model for classification
        self.classifier = models.resnet50(pretrained=True)
        self.classifier.eval()
        
        # Define image transformations
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # Define electronic device categories
        self.electronic_categories = {
            'laptop', 'computer', 'monitor', 'keyboard', 'mouse', 'printer',
            'smartphone', 'mobile phone', 'tablet', 'camera', 'television',
            'headphones', 'speaker', 'microphone', 'router', 'electronic',
            'device', 'appliance', 'gadget'
        }

    def is_electronic_device(self, image_file):
        """Check if the image contains an electronic device"""
        try:
            # Open and preprocess image
            if isinstance(image_file, str):
                image = Image.open(image_file)
            else:
                image = Image.open(image_file).convert('RGB')
            
            # Transform image
            img_tensor = self.transform(image)
            img_tensor = img_tensor.unsqueeze(0)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.classifier(img_tensor)
                _, predicted = torch.max(outputs, 1)
            
            # Get class labels
            with open('imagenet_classes.txt') as f:
                classes = [line.strip() for line in f.readlines()]
            
            predicted_class = classes[predicted.item()].lower()
            
            # Check if any electronic-related words are in the prediction
            is_electronic = any(category in predicted_class for category in self.electronic_categories)
            
            confidence = torch.nn.functional.softmax(outputs[0], dim=0)[predicted].item()
            
            return is_electronic, confidence, predicted_class
            
        except Exception as e:
            logger.error(f"Error checking if image is electronic device: {str(e)}")
            raise

    def extract_features(self, image_file):
        try:
            # Open and convert image to RGB if needed
            if isinstance(image_file, str):
                image = Image.open(image_file)
            else:
                image = Image.open(image_file).convert('RGB')
            
            # Transform image
            img_tensor = self.transform(image)
            img_tensor = img_tensor.unsqueeze(0)
            
            # Extract features
            with torch.no_grad():
                features = self.feature_extractor(img_tensor)
            
            return features.numpy().flatten()
            
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            raise

    def compute_similarity(self, features1, features2):
        """Compute cosine similarity between two feature vectors"""
        return 1 - cosine(features1, features2)

    def find_similar_products(self, query_features, product_features, threshold=0.5):
        """Find similar products based on feature similarity"""
        similar_products = []
        
        for idx, features in enumerate(product_features):
            similarity = self.compute_similarity(query_features, features)
            if similarity > threshold:
                similar_products.append((idx, similarity))
        
        # Sort by similarity score
        similar_products.sort(key=lambda x: x[1], reverse=True)
        return similar_products[:6]  # Return top 6 similar products 