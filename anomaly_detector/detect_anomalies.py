import pandas as pd
import joblib

class AnomalyDetector:
    def __init__(self, model_path: str = 'isolation_forest.joblib', vectorizer_path: str = 'tfidf_vectorizer.joblib'):
        """Loads the pre-trained model and vectorizer."""
        print("Loading anomaly detection model and vectorizer...")
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vectorizer_path)
        print("Ready to detect anomalies.")

    def predict(self, log_messages: list[str]) -> list[int]:
        """
        Predicts if a list of new log messages are anomalies.
        Returns a list where -1 is an anomaly and 1 is normal.
        """
        X_new = self.vectorizer.transform(log_messages)
        predictions = self.model.predict(X_new)
        return predictions

if __name__ == '__main__':
    detector = AnomalyDetector()
    
    # Example of processing a new batch of logs
    new_logs = [
        "INFO: User 'testuser' logged in successfully.",
        "ERROR: Database connection failed: timeout expired.", # This should be an anomaly
        "INFO: Processing request /api/v1/users",
        "WARN: High memory usage detected: 95%",
        "FATAL: NullPointerException at com.example.UserService:123" # This should be an anomaly
    ]
    
    results = detector.predict(new_logs)
    
    print("\n--- Anomaly Detection Results ---")
    for log, result in zip(new_logs, results):
        status = "Anomaly" if result == -1 else "Normal"
        print(f"[{status}] {log}")
