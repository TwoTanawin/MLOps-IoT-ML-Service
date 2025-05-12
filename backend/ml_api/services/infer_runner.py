import logging
import joblib
import numpy as np
import os

_model_cache = None

class MLrunner:
    
    def __init__(self, model_path: str = None):
        self.logger = self._setup_logger()
        self.model_path = model_path or self._get_default_model_path()
        self.model = self._get_cached_model()

    def _setup_logger(self):
        logger = logging.getLogger(self.__class__.__name__)
        if not logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            )
        return logger

    def _get_default_model_path(self):
        current_file = os.path.abspath(__file__)
        services_dir = os.path.dirname(current_file)
        ml_api_dir = os.path.dirname(services_dir)
        backend_dir = os.path.dirname(ml_api_dir)
        model_path = os.path.join(backend_dir, "ml", "models", "gb_model.joblib")
        self.logger.info(f"Default model path resolved: {model_path}")
        return model_path

    def _get_cached_model(self):
        global _model_cache
        if _model_cache is None:
            self.logger.info(f"Loading model from disk: {self.model_path}")
            try:
                _model_cache = joblib.load(self.model_path)
                self.logger.info("Model loaded and cached successfully.")
            except Exception as e:
                self.logger.error(f"Failed to load model: {e}")
                raise
        else:
            self.logger.info("Using cached model.")
        return _model_cache

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

# Usage
if __name__ == "__main__":
    runner = MLrunner()
    print(runner.predict([8.0, 7.5, 30.0, 400.0]))
