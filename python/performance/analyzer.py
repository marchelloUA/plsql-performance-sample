import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class PerformanceAnalyzer:
    """Analyzes database performance data and generates insights"""
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def analyze_query_performance(self, performance_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze query performance patterns"""
        try:
            if performance_data.empty:
                return {}
            
            analysis = {}
            
            # Basic statistics
            analysis['basic_stats'] = {
                'total_queries': len(performance_data),
                'avg_execution_time': performance_data['execution_time_ms'].mean(),
                'median_execution_time': performance_data['execution_time_ms'].median(),
                'p95_execution_time': performance_data['execution_time_ms'].quantile(0.95),
                'p99_execution_time': performance_data['execution_time_ms'].quantile(0.99),
                'max_execution_time': performance_data['execution_time_ms'].max(),
                'min_execution_time': performance_data['execution_time_ms'].min()
            }
            
            # Query type analysis
            if 'query_type' in performance_data.columns:
                query_type_stats = performance_data.groupby('query_type')['execution_time_ms'].agg(['mean', 'count', 'std'])
                analysis['query_type_analysis'] = query_type_stats.to_dict()
            
            # Time-based analysis
            if 'timestamp' in performance_data.columns:
                performance_data['timestamp'] = pd.to_datetime(performance_data['timestamp'])
                performance_data['hour'] = performance_data['timestamp'].dt.hour
                
                hourly_performance = performance_data.groupby('hour')['execution_time_ms'].mean()
                analysis['hourly_performance'] = hourly_performance.to_dict()
                
                # Trend analysis
                performance_data['time_order'] = range(len(performance_data))
                X = performance_data['time_order'].values.reshape(-1, 1)
                y = performance_data['execution_time_ms'].values
                
                model = LinearRegression()
                model.fit(X, y)
                
                analysis['trend_analysis'] = {
                    'trend_slope': model.coef_[0],
                    'trend_intercept': model.intercept_,
                    'r_squared': model.score(X, y)
                }
            
            # Outlier detection
            Q1 = performance_data['execution_time_ms'].quantile(0.25)
            Q3 = performance_data['execution_time_ms'].quantile(0.75)
            IQR = Q3 - Q1
            outliers = performance_data[(performance_data['execution_time_ms'] < Q1 - 1.5 * IQR) | 
                                       (performance_data['execution_time_ms'] > Q3 + 1.5 * IQR)]
            
            analysis['outliers'] = {
                'count': len(outliers),
                'percentage': (len(outliers) / len(performance_data)) * 100,
                'avg_outlier_time': outliers['execution_time_ms'].mean() if not outliers.empty else 0
            }
            
            return analysis
            
        except Exception as e:
            print(f"Query performance analysis failed: {e}")
            return {}
    
    def analyze_resource_usage(self, metrics_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze system resource usage patterns"""
        try:
            if metrics_data.empty:
                return {}
            
            analysis = {}
            
            # CPU analysis
            if 'cpu_percent' in metrics_data.columns:
                analysis['cpu_analysis'] = {
                    'avg_usage': metrics_data['cpu_percent'].mean(),
                    'max_usage': metrics_data['cpu_percent'].max(),
                    'min_usage': metrics_data['cpu_percent'].min(),
                    'high_usage_periods': len(metrics_data[metrics_data['cpu_percent'] > 80]),
                    'consistency': 1 - (metrics_data['cpu_percent'].std() / metrics_data['cpu_percent'].mean())
                }
            
            # Memory analysis
            if 'memory_percent' in metrics_data.columns:
                analysis['memory_analysis'] = {
                    'avg_usage': metrics_data['memory_percent'].mean(),
                    'max_usage': metrics_data['memory_percent'].max(),
                    'min_usage': metrics_data['memory_percent'].min(),
                    'high_usage_periods': len(metrics_data[metrics_data['memory_percent'] > 85]),
                    'trend': self._calculate_trend(metrics_data['memory_percent'])
                }
            
            # Disk analysis
            if 'disk_percent' in metrics_data.columns:
                analysis['disk_analysis'] = {
                    'avg_usage': metrics_data['disk_percent'].mean(),
                    'max_usage': metrics_data['disk_percent'].max(),
                    'min_usage': metrics_data['disk_percent'].min(),
                    'growth_rate': self._calculate_growth_rate(metrics_data['disk_percent'])
                }
            
            # Correlation analysis
            numeric_columns = metrics_data.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 1:
                correlation_matrix = metrics_data[numeric_columns].corr()
                analysis['correlations'] = correlation_matrix.to_dict()
            
            return analysis
            
        except Exception as e:
            print(f"Resource usage analysis failed: {e}")
            return {}
    
    def predict_performance_issues(self, performance_data: pd.DataFrame, 
                                 resource_data: pd.DataFrame) -> Dict[str, Any]:
        """Predict potential performance issues"""
        try:
            predictions = {}
            
            # Query performance prediction
            if not performance_data.empty:
                recent_performance = performance_data.tail(20)  # Last 20 measurements
                if len(recent_performance) >= 10:
                    trend = self._calculate_trend(recent_performance['execution_time_ms'])
                    
                    if trend > 0.1:  # Increasing trend
                        predictions['query_performance_degradation'] = {
                            'severity': 'high' if trend > 0.3 else 'medium',
                            'trend_slope': trend,
                            'prediction': 'Performance is degrading and may require optimization'
                        }
            
            # Resource capacity prediction
            if not resource_data.empty:
                recent_cpu = resource_data.tail(10)['cpu_percent'].values
                recent_memory = resource_data.tail(10)['memory_percent'].values
                
                if len(recent_cpu) > 0:
                    cpu_trend = self._calculate_trend(recent_cpu)
                    if cpu_trend > 0.5 and recent_cpu[-1] > 70:
                        predictions['cpu_capacity_issue'] = {
                            'severity': 'high',
                            'current_usage': recent_cpu[-1],
                            'trend': cpu_trend,
                            'prediction': 'CPU capacity may be insufficient soon'
                        }
                
                if len(recent_memory) > 0:
                    memory_trend = self._calculate_trend(recent_memory)
                    if memory_trend > 0.3 and recent_memory[-1] > 80:
                        predictions['memory_capacity_issue'] = {
                            'severity': 'high',
                            'current_usage': recent_memory[-1],
                            'trend': memory_trend,
                            'prediction': 'Memory usage is approaching capacity'
                        }
            
            return predictions
            
        except Exception as e:
            print(f"Performance prediction failed: {e}")
            return {}
    
    def generate_performance_report(self, performance_data: pd.DataFrame, 
                                  resource_data: pd.DataFrame) -> str:
        """Generate comprehensive performance report"""
        try:
            report = []
            report.append("Database Performance Analysis Report")
            report.append("=" * 50)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # Query performance analysis
            query_analysis = self.analyze_query_performance(performance_data)
            if query_analysis:
                report.append("Query Performance Analysis:")
                report.append("-" * 30)
                
                basic_stats = query_analysis.get('basic_stats', {})
                report.append(f"Total Queries: {basic_stats.get('total_queries', 0)}")
                report.append(f"Average Execution Time: {basic_stats.get('avg_execution_time', 0):.2f} ms")
                report.append(f"P95 Execution Time: {basic_stats.get('p95_execution_time', 0):.2f} ms")
                report.append(f"P99 Execution Time: {basic_stats.get('p99_execution_time', 0):.2f} ms")
                report.append("")
            
            # Resource usage analysis
            resource_analysis = self.analyze_resource_usage(resource_data)
            if resource_analysis:
                report.append("Resource Usage Analysis:")
                report.append("-" * 30)
                
                cpu_analysis = resource_analysis.get('cpu_analysis', {})
                report.append(f"CPU Usage - Avg: {cpu_analysis.get('avg_usage', 0):.1f}%, "
                            f"Max: {cpu_analysis.get('max_usage', 0):.1f}%")
                
                memory_analysis = resource_analysis.get('memory_analysis', {})
                report.append(f"Memory Usage - Avg: {memory_analysis.get('avg_usage', 0):.1f}%, "
                            f"Max: {memory_analysis.get('max_usage', 0):.1f}%")
                report.append("")
            
            # Performance predictions
            predictions = self.predict_performance_issues(performance_data, resource_data)
            if predictions:
                report.append("Performance Predictions:")
                report.append("-" * 30)
                
                for issue, details in predictions.items():
                    severity = details.get('severity', 'unknown')
                    prediction = details.get('prediction', 'No prediction available')
                    report.append(f"[{severity.upper()}] {prediction}")
                report.append("")
            
            # Recommendations
            report.append("Recommendations:")
            report.append("-" * 30)
            report.append("1. Monitor slow queries and consider optimization")
            report.append("2. Review resource usage trends during peak hours")
            report.append("3. Consider scaling resources if usage patterns show growth")
            report.append("4. Implement query caching for frequently executed queries")
            
            return "\n".join(report)
            
        except Exception as e:
            return f"Report generation failed: {e}"
    
    def _calculate_trend(self, data: pd.Series) -> float:
        """Calculate trend slope for time series data"""
        try:
            if len(data) < 2:
                return 0
            
            X = np.arange(len(data)).reshape(-1, 1)
            y = data.values
            
            model = LinearRegression()
            model.fit(X, y)
            
            return model.coef_[0]
            
        except Exception:
            return 0
    
    def _calculate_growth_rate(self, data: pd.Series) -> float:
        """Calculate growth rate for time series data"""
        try:
            if len(data) < 2:
                return 0
            
            first_half = data.iloc[:len(data)//2].mean()
            second_half = data.iloc[len(data)//2:].mean()
            
            if first_half == 0:
                return 0
            
            return (second_half - first_half) / first_half
            
        except Exception:
            return 0