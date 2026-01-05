import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import Optional, Tuple
import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

class StockPricePredictor:
    """Simple ML model for stock price prediction"""
    
    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, df: pd.DataFrame, lookback: int = 7) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features for prediction
        Features: past prices, moving averages, volume, returns
        """
        if df.empty or len(df) < lookback + 1:
            return pd.DataFrame(), pd.Series()
        
        df = df.copy().sort_values('date')
        
        # Create features
        features = []
        targets = []
        
        for i in range(lookback, len(df)):
            # Past prices
            past_prices = df['close'].iloc[i-lookback:i].values
            
            # Moving averages
            ma_7 = df['close'].iloc[i-lookback:i].mean()
            ma_3 = df['close'].iloc[i-3:i].mean() if i >= 3 else df['close'].iloc[i-lookback:i].mean()
            
            # Volume features
            avg_volume = df['volume'].iloc[i-lookback:i].mean()
            current_volume = df['volume'].iloc[i]
            
            # Return features
            returns = df['close'].iloc[i-lookback:i].pct_change().fillna(0).values
            
            # Combine features
            feature_vector = np.concatenate([
                past_prices,
                [ma_7, ma_3, avg_volume, current_volume],
                returns
            ])
            
            features.append(feature_vector)
            targets.append(df['close'].iloc[i])
        
        X = pd.DataFrame(features)
        y = pd.Series(targets)
        
        return X, y
    
    def train(self, df: pd.DataFrame) -> bool:
        """Train the model on historical data"""
        try:
            if df.empty or len(df) < 20:
                logger.warning("Insufficient data for training")
                return False
            
            X, y = self.prepare_features(df)
            
            if X.empty or len(X) < 5:
                logger.warning("Insufficient features for training")
                return False
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Calculate R² score
            score = self.model.score(X_test_scaled, y_test)
            logger.info(f"Model trained with R² score: {score:.4f}")
            
            self.is_trained = True
            return True
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return False
    
    def predict(self, df: pd.DataFrame, days_ahead: int = 1) -> Optional[float]:
        """
        Predict future price
        For simplicity, predict next day's price
        """
        if not self.is_trained:
            # Train on the fly
            if not self.train(df):
                return None
        
        try:
            if df.empty or len(df) < 7:
                return None
            
            df = df.copy().sort_values('date')
            
            # Get last lookback days
            lookback = 7
            if len(df) < lookback:
                return None
            
            # Prepare features from last data point
            last_prices = df['close'].iloc[-lookback:].values
            ma_7 = df['close'].iloc[-lookback:].mean()
            ma_3 = df['close'].iloc[-3:].mean() if len(df) >= 3 else ma_7
            avg_volume = df['volume'].iloc[-lookback:].mean()
            current_volume = df['volume'].iloc[-1]
            returns = df['close'].iloc[-lookback:].pct_change().fillna(0).values
            
            feature_vector = np.concatenate([
                last_prices,
                [ma_7, ma_3, avg_volume, current_volume],
                returns
            ]).reshape(1, -1)
            
            # Scale and predict
            feature_scaled = self.scaler.transform(feature_vector)
            prediction = self.model.predict(feature_scaled)[0]
            
            return float(prediction)
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return None
    
    def predict_with_confidence(self, df: pd.DataFrame) -> Tuple[Optional[float], float]:
        """
        Predict price with confidence score
        Confidence is based on model's R² score and data quality
        """
        prediction = self.predict(df)
        
        if prediction is None:
            return None, 0.0
        
        # Simple confidence calculation
        # Based on data quality and model performance
        data_quality = min(len(df) / 100, 1.0)  # More data = higher confidence
        confidence = data_quality * 0.85  # Max 85% confidence for simple linear model
        
        return prediction, confidence

# Global predictor instance
_predictor = StockPricePredictor()

def get_predictor() -> StockPricePredictor:
    """Get the global predictor instance"""
    return _predictor

