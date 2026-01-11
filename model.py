"""
Blood Sense AI - ML Model Module (Inference Only)
This module loads the trained model and performs predictions.
Training is separated into train.py.
"""
import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from typing import Dict, Optional, List


# Module-level globals
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TRAIN_DATA_DIR = r'C:\Users\ADMIN\OneDrive\Desktop\train'  # External training dataset
MODEL_PATH = os.path.join(BASE_DIR, 'blood_cell_model.keras')
CLASS_NAMES_PATH = os.path.join(BASE_DIR, 'class_names.json')
METRICS_PATH = os.path.join(BASE_DIR, 'model_metrics.json')
IMG_SIZE = (224, 224)

# Singleton model instance
_model_instance = None
_class_names = None
_model_metrics = None


class ModelManager:
    """Manages ML model loading and predictions (Singleton pattern)"""
    
    def __init__(self):
        self.model = None
        self.class_names = None
        self.metrics = None
        self.model_loaded = False
        
    def load_model(self, model_path: str = MODEL_PATH, 
                   class_names_path: str = CLASS_NAMES_PATH,
                   metrics_path: str = METRICS_PATH) -> bool:
        """Load the trained model and metadata"""
        try:
            # Load the Keras model
            if os.path.exists(model_path):
                print(f"Loading model from {model_path}...")
                self.model = load_model(model_path)
                print("✅ Model loaded successfully")
            else:
                print(f"❌ Model file not found: {model_path}")
                return False
            
            # Load class names
            if os.path.exists(class_names_path):
                with open(class_names_path, 'r') as f:
                    self.class_names = json.load(f)
                print(f"✅ Class names loaded: {self.class_names}")
            else:
                print(f"⚠️  Class names file not found: {class_names_path}")
                # Try to infer from training data
                self.class_names = self._infer_class_names()
            
            # Load metrics
            if os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    self.metrics = json.load(f)
                print(f"✅ Model metrics loaded")
            else:
                print(f"⚠️  Metrics file not found: {metrics_path}")
                self.metrics = self._default_metrics()
            
            self.model_loaded = True
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model_loaded = False
            return False
    
    def _infer_class_names(self) -> Optional[List[str]]:
        """Try to infer class names from training data directory"""
        if os.path.isdir(TRAIN_DATA_DIR):
            class_names = sorted([d for d in os.listdir(TRAIN_DATA_DIR) 
                                if os.path.isdir(os.path.join(TRAIN_DATA_DIR, d))])
            if class_names:
                # Save for future use
                self.save_class_names(class_names)
                return class_names
        return None
    
    def _default_metrics(self) -> Dict:
        """Return default metrics structure"""
        return {
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "per_class_metrics": {},
            "last_trained": "unknown"
        }
    
    def save_class_names(self, class_names: List[str]):
        """Save class names to JSON file"""
        try:
            with open(CLASS_NAMES_PATH, 'w') as f:
                json.dump(class_names, f, indent=2)
            print(f"✅ Class names saved to {CLASS_NAMES_PATH}")
        except Exception as e:
            print(f"Error saving class names: {e}")
    
    def predict_single_image(self, image_path: str) -> Dict:
        """
        Predict class for a single image.
        Returns detailed prediction information.
        """
        if not self.model_loaded or self.model is None:
            return {
                "error": "Model not loaded",
                "class": "UNKNOWN",
                "confidence": 0.0,
                "all_probabilities": {},
                "model_loaded": False,
                "recall_note": "Model unavailable"
            }
        
        if self.class_names is None:
            return {
                "error": "Class names not available",
                "class": "UNKNOWN",
                "confidence": 0.0,
                "all_probabilities": {},
                "model_loaded": True,
                "recall_note": "Class names unavailable"
            }
        
        try:
            # Load and preprocess image
            img = tf.keras.utils.load_img(image_path, target_size=IMG_SIZE)
            img_array = tf.keras.utils.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)
            
            # Get predictions
            predictions = self.model.predict(img_array, verbose=0)
            score = tf.nn.softmax(predictions[0])
            
            # Get predicted class and confidence
            predicted_class_index = int(np.argmax(score))
            predicted_class = self.class_names[predicted_class_index]
            confidence = float(np.max(score))
            
            # Get all class probabilities
            all_probabilities = {
                self.class_names[i]: float(score[i])
                for i in range(len(self.class_names))
            }
            
            # Get recall note for this class
            recall_note = self._get_recall_note(predicted_class)
            
            return {
                "class": predicted_class,
                "confidence": confidence,
                "all_probabilities": all_probabilities,
                "model_loaded": True,
                "recall_note": recall_note,
                "predicted_class_index": predicted_class_index,
                "num_classes": len(self.class_names)
            }
            
        except Exception as e:
            print(f"Error in predict_single_image: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "class": "UNKNOWN",
                "confidence": 0.0,
                "all_probabilities": {},
                "model_loaded": True,
                "recall_note": "Error during prediction"
            }
    
    def predict_batch_images(self, image_paths: List[str]) -> List[Dict]:
        """Predict classes for multiple images"""
        results = []
        for image_path in image_paths:
            result = self.predict_single_image(image_path)
            result['image_path'] = image_path
            results.append(result)
        return results
    
    def _get_recall_note(self, predicted_class: str) -> str:
        """Get recall note for a predicted class"""
        if not self.metrics or 'per_class_metrics' not in self.metrics:
            return "Model optimized for high sensitivity (recall) to minimize false negatives."
        
        class_metrics = self.metrics.get('per_class_metrics', {}).get(predicted_class, {})
        recall = class_metrics.get('recall', 0.0)
        
        if recall > 0:
            recall_pct = int(recall * 100)
            return f"Model recall for {predicted_class}: {recall_pct}% (sensitivity in detecting this cell type)"
        else:
            return "Model optimized for high sensitivity (recall) to minimize false negatives."
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            "model_loaded": self.model_loaded,
            "model_path": MODEL_PATH,
            "classes": self.class_names or [],
            "num_classes": len(self.class_names) if self.class_names else 0,
            "image_size": IMG_SIZE
        }
    
    def get_model_metrics(self) -> Dict:
        """Get model performance metrics"""
        if not self.metrics:
            return self._default_metrics()
        return self.metrics


# Singleton instance getter
def get_model_manager() -> ModelManager:
    """Get or create model manager instance (singleton)"""
    global _model_instance
    
    if _model_instance is None:
        _model_instance = ModelManager()
        _model_instance.load_model()
    
    return _model_instance


# Convenience functions for backward compatibility
def predict_image(image_path: str) -> Dict:
    """Predict class for a single image (backward compatible)"""
    manager = get_model_manager()
    return manager.predict_single_image(image_path)


def predict_batch(image_paths: List[str]) -> List[Dict]:
    """Predict classes for multiple images"""
    manager = get_model_manager()
    return manager.predict_batch_images(image_paths)


def get_model_performance_metrics() -> Dict:
    """Get model performance metrics"""
    manager = get_model_manager()
    return manager.get_model_metrics()


def calculate_recall_per_class() -> Dict:
    """Get per-class recall metrics"""
    manager = get_model_manager()
    metrics = manager.get_model_metrics()
    
    if 'per_class_metrics' not in metrics:
        return {}
    
    recall_dict = {}
    for class_name, class_metrics in metrics['per_class_metrics'].items():
        recall_dict[class_name] = class_metrics.get('recall', 0.0)
    
    return recall_dict


if __name__ == '__main__':
    # Test model loading
    print("\n🔬 Testing Model Manager...")
    manager = get_model_manager()
    
    if manager.model_loaded:
        print("\n✅ Model is ready for predictions")
        print(f"   Classes: {manager.class_names}")
        print(f"   Number of classes: {len(manager.class_names) if manager.class_names else 0}")
        
        # Test prediction if test images exist in training directory
        if os.path.isdir(TRAIN_DATA_DIR):
            print(f"\n🔍 Looking for test images in {TRAIN_DATA_DIR}...")
            for root, dirs, files in os.walk(TRAIN_DATA_DIR):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        test_image = os.path.join(root, file)
                        print(f"\n📷 Testing prediction on: {file}")
                        result = manager.predict_single_image(test_image)
                        print(f"   Predicted: {result['class']} ({result['confidence']*100:.2f}% confidence)")
                        break
                break
    else:
        print("\n❌ Model failed to load")
        print("   Make sure the model file exists and training has been completed")
