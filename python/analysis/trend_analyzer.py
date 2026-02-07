import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from unittest.mock import Mock

# Mock optional modules if not available
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = Mock()

try:
    from sklearn.linear_model import LinearRegression
except ImportError:
    LinearRegression = Mock()

try:
    from sklearn.preprocessing import StandardScaler
except ImportError:
    StandardScaler = Mock()

class TrendAnalyzer:
    """Analyzes performance trends and makes predictions"""
    
    def __init__(self):
        try:
            self.scaler = StandardScaler()
        except:
            self.scaler = None
    
    def analyze_cpu_trends(self, performance_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze CPU usage trends"""
        try:
            if 'cpu_percent' not in performance_data.columns or performance_data.empty:
                return {}
            
            data = performance_data.copy()
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data = data.sort_values('timestamp')
            
            # Calculate moving averages
            data['cpu_ma_5'] = data['cpu_percent'].rolling(window=5).mean()
            data['cpu_ma_10'] = data['cpu_percent'].rolling(window=10).mean()
            
            # Linear regression for trend
            X = np.arange(len(data)).reshape(-1, 1)
            y = data['cpu_percent'].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict future values
            future_points = np.arange(len(data), len(data) + 10).reshape(-1, 1)
            future_predictions = model.predict(future_points)
            
            # Calculate trend statistics
            trend_slope = model.coef_[0]
            r_squared = model.score(X, y)
            
            # Identify anomalies
            Q1 = data['cpu_percent'].quantile(0.25)
            Q3 = data['cpu_percent'].quantile(0.75)
            IQR = Q3 - Q1
            anomalies = data[(data['cpu_percent'] < Q1 - 1.5 * IQR) | 
                           (data['cpu_percent'] > Q3 + 1.5 * IQR)]
            
            return {
                'trend_slope': trend_slope,
                'r_squared': r_squared,
                'current_avg': data['cpu_percent'].mean(),
                'predicted_values': future_predictions.tolist(),
                'anomalies': len(anomalies),
                'anomaly_percentage': (len(anomalies) / len(data)) * 100,
                'moving_averages': {
                    'ma_5': data['cpu_ma_5'].iloc[-1] if not data['cpu_ma_5'].isna().all() else 0,
                    'ma_10': data['cpu_ma_10'].iloc[-1] if not data['cpu_ma_10'].isna().all() else 0
                }
            }
            
        except Exception as e:
            print(f"CPU trend analysis failed: {e}")
            return {}
    
    def analyze_memory_trends(self, performance_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze memory usage trends"""
        try:
            if 'memory_percent' not in performance_data.columns or performance_data.empty:
                return {}
            
            data = performance_data.copy()
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data = data.sort_values('timestamp')
            
            # Calculate growth rate
            first_half = data['memory_percent'].iloc[:len(data)//2].mean()
            second_half = data['memory_percent'].iloc[len(data)//2:].mean()
            growth_rate = (second_half - first_half) / first_half if first_half > 0 else 0
            
            # Predict memory exhaustion
            current_memory = data['memory_percent'].iloc[-1]
            time_to_exhaustion = None
            
            if growth_rate > 0:
                remaining_memory = 100 - current_memory
                time_to_exhaustion = remaining_memory / growth_rate if growth_rate > 0 else None
            
            # Memory usage patterns
            peak_hours = data[data['memory_percent'] > 80]['timestamp'].dt.hour.value_counts()
            
            return {
                'growth_rate': growth_rate,
                'current_usage': current_memory,
                'time_to_exhaustion': time_to_exhaustion,
                'peak_hours': peak_hours.head(5).to_dict(),
                'avg_usage': data['memory_percent'].mean(),
                'max_usage': data['memory_percent'].max(),
                'volatility': data['memory_percent'].std()
            }
            
        except Exception as e:
            print(f"Memory trend analysis failed: {e}")
            return {}
    
    def analyze_disk_trends(self, performance_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze disk usage trends"""
        try:
            if 'disk_percent' not in performance_data.columns or performance_data.empty:
                return {}
            
            data = performance_data.copy()
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data = data.sort_values('timestamp')
            
            # Calculate disk growth rate
            first_half = data['disk_percent'].iloc[:len(data)//2].mean()
            second_half = data['disk_percent'].iloc[len(data)//2:].mean()
            growth_rate = (second_half - first_half) / first_half if first_half > 0 else 0
            
            # Predict disk capacity
            current_disk = data['disk_percent'].iloc[-1]
            time_to_full = None
            
            if growth_rate > 0:
                remaining_disk = 100 - current_disk
                time_to_full = remaining_disk / growth_rate if growth_rate > 0 else None
            
            return {
                'growth_rate': growth_rate,
                'current_usage': current_disk,
                'time_to_full': time_to_full,
                'avg_usage': data['disk_percent'].mean(),
                'max_usage': data['disk_percent'].max(),
                'trend_direction': 'increasing' if growth_rate > 0 else 'decreasing' if growth_rate < 0 else 'stable'
            }
            
        except Exception as e:
            print(f"Disk trend analysis failed: {e}")
            return {}
    
    def predict_future_performance(self, performance_data: pd.DataFrame, 
                                 days_ahead: int = 7) -> Dict[str, Any]:
        """Predict future performance metrics"""
        try:
            if performance_data.empty:
                return {}
            
            predictions = {}
            
            # CPU prediction
            cpu_trend = self.analyze_cpu_trends(performance_data)
            if cpu_trend:
                predictions['cpu'] = {
                    'current_avg': cpu_trend.get('current_avg', 0),
                    'predicted_avg': cpu_trend.get('predicted_values', [0] * days_ahead)[-1] if cpu_trend.get('predicted_values') else 0,
                    'trend_slope': cpu_trend.get('trend_slope', 0),
                    'risk_level': self._assess_cpu_risk(cpu_trend)
                }
            
            # Memory prediction
            memory_trend = self.analyze_memory_trends(performance_data)
            if memory_trend:
                predictions['memory'] = {
                    'current_usage': memory_trend.get('current_usage', 0),
                    'predicted_usage': min(100, memory_trend.get('current_usage', 0) + 
                                         (memory_trend.get('growth_rate', 0) * days_ahead)),
                    'time_to_exhaustion': memory_trend.get('time_to_exhaustion'),
                    'risk_level': self._assess_memory_risk(memory_trend)
                }
            
            # Disk prediction
            disk_trend = self.analyze_disk_trends(performance_data)
            if disk_trend:
                predictions['disk'] = {
                    'current_usage': disk_trend.get('current_usage', 0),
                    'predicted_usage': min(100, disk_trend.get('current_usage', 0) + 
                                         (disk_trend.get('growth_rate', 0) * days_ahead)),
                    'time_to_full': disk_trend.get('time_to_full'),
                    'risk_level': self._assess_disk_risk(disk_trend)
                }
            
            return predictions
            
        except Exception as e:
            print(f"Future performance prediction failed: {e}")
            return {}
    
    def _assess_cpu_risk(self, cpu_trend: Dict[str, Any]) -> str:
        """Assess CPU risk level"""
        try:
            current_avg = cpu_trend.get('current_avg', 0)
            trend_slope = cpu_trend.get('trend_slope', 0)
            
            if current_avg > 80 or trend_slope > 2:
                return 'high'
            elif current_avg > 60 or trend_slope > 1:
                return 'medium'
            else:
                return 'low'
        except:
            return 'unknown'
    
    def _assess_memory_risk(self, memory_trend: Dict[str, Any]) -> str:
        """Assess memory risk level"""
        try:
            current_usage = memory_trend.get('current_usage', 0)
            time_to_exhaustion = memory_trend.get('time_to_exhaustion')
            
            if current_usage > 85 or (time_to_exhaustion and time_to_exhaustion < 24):
                return 'high'
            elif current_usage > 70 or (time_to_exhaustion and time_to_exhaustion < 72):
                return 'medium'
            else:
                return 'low'
        except:
            return 'unknown'
    
    def _assess_disk_risk(self, disk_trend: Dict[str, Any]) -> str:
        """Assess disk risk level"""
        try:
            current_usage = disk_trend.get('current_usage', 0)
            time_to_full = disk_trend.get('time_to_full')
            
            if current_usage > 90 or (time_to_full and time_to_full < 24):
                return 'high'
            elif current_usage > 75 or (time_to_full and time_to_full < 72):
                return 'medium'
            else:
                return 'low'
        except:
            return 'unknown'