import logging
import joblib
import numpy as np
import os

class MLrunner:
    
    def __init__(self, model_path: str = None):
        self.logger = self._setup_logger()
        self.model_path = model_path or self._load_base_model()  # Use default if none provided
        self.model = self._load_model()
        
    def _load_base_model(self):
        
        current_file = os.path.abspath(__file__)
        # Get the directory containing the current file (services)
        services_dir = os.path.dirname(current_file)
        # Go up to ml_api directory
        ml_api_dir = os.path.dirname(services_dir)
        # Go up to backend directory
        backend_dir = os.path.dirname(ml_api_dir)
        # Create path to the correct model location
        model_path = os.path.join(backend_dir, "ml", "models", "gb_model.joblib")
        
        self.logger.info(f"Looking for model at: {model_path}")
        return model_path

    def _setup_logger(self):
        logger = logging.getLogger(self.__class__.__name__)
        if not logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            )
        return logger

    def _load_model(self):
        self.logger.info(f"Loading model from: {self.model_path}")
        try:
            model = joblib.load(self.model_path)
            self.logger.info("Model loaded successfully.")
            return model
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise

    def predict(self, sample: list):
        class_names = ['Clean', 'Low pH', 'High pH', 'Chemical', 'Salt', 'Organic']
        
        self.logger.info(f"Raw sample: {sample}")
        filtered_input = np.array(sample).reshape(1, -1)

        prediction = self.model.predict(filtered_input)
        prediction_proba = self.model.predict_proba(filtered_input)

        predicted_index = prediction[0]
        confidence = prediction_proba[0][predicted_index]

        self.logger.info(f"Predicted class index: {predicted_index}")
        self.logger.info(f"Predicted class name: {class_names[predicted_index]}")
        self.logger.info(f"Confidence (probability): {round(confidence * 100, 2)}%")

        return {
            "class_index": int(predicted_index),
            "class_name": class_names[predicted_index],
            "confidence": round(confidence * 100, 2)
        }

# Usage example:
if __name__ == "__main__":
    runner = MLrunner()
    result = runner.predict([0, 0, 0, 0])
    print(result)