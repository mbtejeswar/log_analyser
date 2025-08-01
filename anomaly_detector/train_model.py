import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest
import joblib

def train_and_save_model(normal_logs_path: str, model_path: str = 'isolation_forest.joblib', vectorizer_path: str = 'tfidf_vectorizer.joblib'):
    """Trains an Isolation Forest model on normal log data and saves it."""
    
    print("Loading normal logs for training...")
    # Assume normal_logs.csv has a single column 'log_message'
    df = pd.read_csv(normal_logs_path)
    
    # Vectorize the log messages using TF-IDF
    print("Vectorizing log messages...")
    vectorizer = TfidfVectorizer(max_features=5000)
    X_train = vectorizer.fit_transform(df['log_message'])
    
    # Train the Isolation Forest model
    print("Training Isolation Forest model...")
    model = IsolationForest(contamination='auto', random_state=42)
    model.fit(X_train)
    
    # Save the trained model and vectorizer
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    print(f"Model saved to {model_path} and vectorizer to {vectorizer_path}")

if __name__ == '__main__':
    # You would replace 'data/normal_logs.csv' with a path to a CSV file
    # containing thousands of log lines from your application during
    # a period of normal, stable operation.
    train_and_save_model('data/normal_logs.csv')
