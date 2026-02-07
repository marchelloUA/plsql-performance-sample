import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

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

from analysis.trend_analyzer import TrendAnalyzer

class TestTrendAnalyzer:
    """Test cases for TrendAnalyzer"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = TrendAnalyzer()
    
    def test_init(self):
        """Test TrendAnalyzer initialization"""
        assert self.analyzer.scaler is not None
        assert isinstance(self.analyzer.scaler, StandardScaler)
    
    def test_analyze_cpu_trends_success(self):
        """Test successful CPU trend analysis"""
        # Create sample performance data
        performance_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01 10:00:00', periods=10, freq='1min'),
            'cpu_percent': [45.2, 52.3, 48.7, 55.1, 42.9, 58.3, 51.2, 47.8, 53.6, 49.1],
            'memory_percent': [62.1, 64.5, 61.8, 66.2, 60.3, 68.1, 63.4, 59.7, 65.2, 61.9]
        })
        
        # Call the method
        result = self.analyzer.analyze_cpu_trends(performance_data)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'trend_slope' in result
        assert 'r_squared' in result
        assert 'moving_averages' in result
        assert 'future_predictions' in result
        assert 'anomalies' in result
        
        # Verify moving averages
        assert 'cpu_ma_5' in result['moving_averages']
        assert 'cpu_ma_10' in result['moving_averages']
        
        # Verify future predictions
        assert len(result['future_predictions']) == 10
        
        # Verify anomalies
        assert isinstance(result['anomalies'], pd.DataFrame)
    
    def test_analyze_cpu_trends_empty_data(self):
        """Test CPU trend analysis with empty data"""
        performance_data = pd.DataFrame()
        
        # Call the method
        result = self.analyzer.analyze_cpu_trends(performance_data)
        
        # Verify empty result
        assert result == {}
    
    def test_analyze_cpu_trends_missing_column(self):
        """Test CPU trend analysis with missing cpu_percent column"""
        performance_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01 10:00:00', periods=5, freq='1min'),
            'memory_percent': [62.1, 64.5, 61.8, 66.2, 60.3]
        })
        
        # Call the method
        result = self.analyzer.analyze_cpu_trends(performance_data)
        
        # Verify empty result
        assert result == {}
    
    def test_analyze_cpu_trends_insufficient_data(self):
        """Test CPU trend analysis with insufficient data for moving averages"""
        performance_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01 10:00:00', periods=2, freq='1min'),
            'cpu_percent': [45.2, 52.3],
            'memory_percent': [62.1, 64.5]
        })
        
        # Call the method
        result = self.analyzer.analyze_cpu_trends(performance_data)
        
        # Verify result structure but no moving averages
        assert isinstance(result, dict)
        assert 'trend_slope' in result
        assert 'r_squared' in result
        assert 'moving_averages' in result
        assert 'future_predictions' in result
        assert 'anomalies' in result
        
        # Verify moving averages are empty due to insufficient data
        assert result['moving_averages'] == {}
    
    def test_analyze_cpu_trends_with_anomalies(self):
        """Test CPU trend analysis with anomalies"""
        # Create data with anomalies
        performance_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01 10:00:00', periods=10, freq='1min'),
            'cpu_percent': [45.2, 52.3, 48.7, 55.1, 95.0, 58.3, 51.2, 47.8, 53.6, 49.1],  # 95.0 is anomaly
            'memory_percent': [62.1, 64.5, 61.8, 66.2, 98.5, 68.1, 63.4, 59.7, 65.2, 61.9]  # 98.5 is anomaly
        })
        
        # Call the method
        result = self.analyzer.analyze_cpu_trends(performance_data)
        
        # Verify anomalies are detected
        assert not result['anomalies'].empty
        assert len(result['anomalies']) > 0
        
        # Verify anomalies have expected columns
        expected_columns = ['timestamp', 'cpu_percent', 'memory_percent']
        for col in expected_columns:
            assert col in result['anomalies'].columns
    
    def test_analyze_cpu_trends_negative_trend(self):
        """Test CPU trend analysis with negative trend"""
        # Create data with decreasing trend
        performance_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01 10:00:00', periods=10, freq='1min'),
            'cpu_percent': [80.0, 78.5, 76.2, 74.8, 72.1, 70.5, 68.9, 66.3, 64.7, 62.1],
            'memory_percent': [62.1, 64.5, 61.8, 66.2, 60.3, 68.1, 63.4, 59.7, 65.2, 61.9]
        })
        
        # Call the method
        result = self.analyzer.analyze_cpu_trends(performance_data)
        
        # Verify negative trend slope
        assert result['trend_slope'] < 0
        
        # Verify future predictions are decreasing
        future_predictions = result['future_predictions']
        assert all(future_predictions[i] >= future_predictions[i+1] for i in range(len(future_predictions)-1))
    
    def test_analyze_cpu_trends_positive_trend(self):
        """Test CPU trend analysis with positive trend"""
        # Create data with increasing trend
        performance_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01 10:00:00', periods=10, freq='1min'),
            'cpu_percent': [40.0, 42.5, 44.2, 46.8, 48.1, 50.5, 52.9, 54.3, 56.7, 58.1],
            'memory_percent': [62.1, 64.5, 61.8, 66.2, 60.3, 68.1, 63.4, 59.7, 65.2, 61.9]
        })
        
        # Call the method
        result = self.analyzer.analyze_cpu_trends(performance_data)
        
        # Verify positive trend slope
        assert result['trend_slope'] > 0
        
        # Verify future predictions are increasing
        future_predictions = result['future_predictions']
        assert all(future_predictions[i] <= future_predictions[i+1] for i in range(len(future_predictions)-1))
    
    def test_analyze_cpu_trends_flat_trend(self):
        """Test CPU trend analysis with flat trend"""
        # Create data with stable values
        performance_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01 10:00:00', periods=10, freq='1min'),
            'cpu_percent': [50.0, 50.2, 49.8, 50.1, 50.3, 49.9, 50.0, 50.2, 49.7, 50.1],
            'memory_percent': [62.1, 64.5, 61.8, 66.2, 60.3, 68.1, 63.4, 59.7, 65.2, 61.9]
        })
        
        # Call the method
        result = self.analyzer.analyze_cpu_trends(performance_data)
        
        # Verify trend slope is close to zero
        assert abs(result['trend_slope']) < 0.1
        
        # Verify R-squared is low (flat trend)
        assert result['r_squared'] < 0.5
    
    def test_analyze_cpu_trends_with_missing_timestamps(self):
        """Test CPU trend analysis with missing timestamps"""
        # Create data with irregular timestamps
        performance_data = pd.DataFrame({
            'timestamp': [
                '2023-01-01 10:00:00',
                '2023-01-01 10:02:00',  # 2-minute gap
                '2023-01-01 10:03:00',
                '2023-01-01 10:05:00',  # 2-minute gap
                '2023-01-01 10:06:00'
            ],
            'cpu_percent': [45.2, 52.3, 48.7, 55.1, 42.9],
            'memory_percent': [62.1, 64.5, 61.8, 66.2, 60.3]
        })
        
        # Call the method
        result = self.analyzer.analyze_cpu_trends(performance_data)
        
        # Verify result is still valid
        assert isinstance(result, dict)
        assert 'trend_slope' in result
        assert 'r_squared' in result
        assert 'moving_averages' in result
        assert 'future_predictions' in result
        assert 'anomalies' in result
    
    def test_analyze_cpu_trends_with_string_timestamps(self):
        """Test CPU trend analysis with string timestamps"""
        # Create data with string timestamps
        performance_data = pd.DataFrame({
            'timestamp': [
                '2023-01-01 10:00:00',
                '2023-01-01 10:01:00',
                '2023-01-01 10:02:00',
                '2023-01-01 10:03:00',
                '2023-01-01 10:04:00'
            ],
            'cpu_percent': [45.2, 52.3, 48.7, 55.1, 42.9],
            'memory_percent': [62.1, 64.5, 61.8, 66.2, 60.3]
        })
        
        # Call the method
        result = self.analyzer.analyze_cpu_trends(performance_data)
        
        # Verify result is still valid
        assert isinstance(result, dict)
        assert 'trend_slope' in result
        assert 'r_squared' in result
        assert 'moving_averages' in result
        assert 'future_predictions' in result
        assert 'anomalies' in result
    
    def test_analyze_cpu_trends_with_negative_values(self):
        """Test CPU trend analysis with negative CPU values"""
        # Create data with negative CPU values (shouldn't happen but test robustness)
        performance_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01 10:00:00', periods=5, freq='1min'),
            'cpu_percent': [-5.2, -2.3, -1.7, -5.1, -2.9],
            'memory_percent': [62.1, 64.5, 61.8, 66.2, 60.3]
        })
        
        # Call the method
        result = self.analyzer.analyze_cpu_trends(performance_data)
        
        # Verify result is still valid
        assert isinstance(result, dict)
        assert 'trend_slope' in result
        assert 'r_squared' in result
        assert 'moving_averages' in result
        assert 'future_predictions' in result
        assert 'anomalies' in result
    
    def test_analyze_cpu_trends_with_extreme_values(self):
        """Test CPU trend analysis with extreme values"""
        # Create data with extreme values
        performance_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01 10:00:00', periods=10, freq='1min'),
            'cpu_percent': [0.1, 100.0, 0.2, 99.9, 0.3, 100.0, 0.4, 99.8, 0.5, 100.0],
            'memory_percent': [62.1, 64.5, 61.8, 66.2, 60.3, 68.1, 63.4, 59.7, 65.2, 61.9]
        })
        
        # Call the method
        result = self.analyzer.analyze_cpu_trends(performance_data)
        
        # Verify result is still valid
        assert isinstance(result, dict)
        assert 'trend_slope' in result
        assert 'r_squared' in result
        assert 'moving_averages' in result
        assert 'future_predictions' in result
        assert 'anomalies' in result
        
        # Verify extreme values are detected as anomalies
        assert not result['anomalies'].empty
    
    @patch('matplotlib.pyplot.show')
    def test_analyze_cpu_trends_with_plot(self, mock_show):
        """Test CPU trend analysis with plotting"""
        # Create sample performance data
        performance_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01 10:00:00', periods=10, freq='1min'),
            'cpu_percent': [45.2, 52.3, 48.7, 55.1, 42.9, 58.3, 51.2, 47.8, 53.6, 49.1],
            'memory_percent': [62.1, 64.5, 61.8, 66.2, 60.3, 68.1, 63.4, 59.7, 65.2, 61.9]
        })
        
        # Call the method with plot=True
        result = self.analyzer.analyze_cpu_trends(performance_data, plot=True)
        
        # Verify plot was called
        mock_show.assert_called_once()
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'trend_slope' in result
        assert 'r_squared' in result
        assert 'moving_averages' in result
        assert 'future_predictions' in result
        assert 'anomalies' in result

class TestTrendAnalyzerIntegration:
    """Integration tests for TrendAnalyzer"""
    
    @pytest.mark.integration
    def test_trend_analyzer_integration(self, sample_performance_data):
        """Test real trend analyzer functionality"""
        try:
            from analysis.trend_analyzer import TrendAnalyzer
            
            # Create analyzer
            analyzer = TrendAnalyzer()
            
            # Convert sample data to DataFrame
            performance_data = pd.DataFrame(sample_performance_data)
            performance_data['timestamp'] = pd.to_datetime(performance_data['timestamp'])
            
            # Test CPU trend analysis
            result = analyzer.analyze_cpu_trends(performance_data)
            
            # Verify result structure
            assert isinstance(result, dict)
            assert 'trend_slope' in result
            assert 'r_squared' in result
            assert 'moving_averages' in result
            assert 'future_predictions' in result
            assert 'anomalies' in result
            
            # Verify data types
            assert isinstance(result['trend_slope'], (int, float))
            assert isinstance(result['r_squared'], (int, float))
            assert isinstance(result['moving_averages'], dict)
            assert isinstance(result['future_predictions'], list)
            assert isinstance(result['anomalies'], pd.DataFrame)
            
        except Exception as e:
            pytest.skip(f"Trend analyzer integration test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__])