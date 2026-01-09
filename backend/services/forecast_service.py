"""
Forecast Engine - Statistical Model for Multi-Year Predictions
Requires minimum 3 years of real historical data
Provides confidence bands and explanations
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
import math

logger = logging.getLogger(__name__)


class ForecastService:
    """
    Forecast service for KPI predictions
    Uses simple linear regression for explainability
    Requires minimum 3 years of historical data
    """
    
    def __init__(self):
        pass
    
    def forecast_kpi(
        self,
        historical_data: List[Dict[str, Any]],  # [{year, value}, ...]
        forecast_years: int = 3,
        kpi_name: str = "overall_score"
    ) -> Dict[str, Any]:
        """
        Forecast KPI values for future years using linear regression.
        
        Args:
            historical_data: List of {year: int, value: float} dicts
            forecast_years: Number of years to forecast ahead
            kpi_name: Name of KPI being forecasted
            
        Returns:
            {
                "can_forecast": bool,
                "forecast": [{year, predicted_value, lower_bound, upper_bound}],
                "confidence_band": float,  # 0-1
                "explanation": str,
                "insufficient_data_reason": str (if can_forecast=False)
            }
        """
        # Validate minimum 3 years requirement
        if len(historical_data) < 3:
            return {
                "can_forecast": False,
                "forecast": [],
                "confidence_band": 0.0,
                "explanation": None,
                "insufficient_data_reason": f"Insufficient data: {len(historical_data)} year(s) available, need at least 3 years for forecasting"
            }
        
        # Filter out None/null values
        valid_data = [
            point for point in historical_data
            if point.get("value") is not None and isinstance(point.get("value"), (int, float))
        ]
        
        if len(valid_data) < 3:
            return {
                "can_forecast": False,
                "forecast": [],
                "confidence_band": 0.0,
                "explanation": None,
                "insufficient_data_reason": f"Insufficient valid data: {len(valid_data)} valid point(s), need at least 3 for forecasting"
            }
        
        try:
            # Extract years and values
            years = [point["year"] for point in valid_data]
            values = [point["value"] for point in valid_data]
            
            # Calculate linear regression
            slope, intercept, r_squared = self._linear_regression(years, values)
            
            # Calculate confidence band (based on R² and data spread)
            confidence_band = min(0.95, max(0.5, r_squared))
            
            # Get last year
            last_year = max(years)
            
            # Generate forecast for next N years
            forecast_points = []
            for i in range(1, forecast_years + 1):
                forecast_year = last_year + i
                predicted_value = slope * forecast_year + intercept
                
                # Calculate confidence interval (standard error)
                std_error = self._calculate_standard_error(years, values, slope, intercept)
                margin = std_error * 1.96  # 95% confidence interval
                
                forecast_points.append({
                    "year": forecast_year,
                    "predicted_value": round(predicted_value, 2),
                    "lower_bound": round(max(0, predicted_value - margin), 2),
                    "upper_bound": round(min(100, predicted_value + margin), 2),
                    "confidence": round(confidence_band, 2)
                })
            
            # Generate explanation
            trend_direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
            explanation = (
                f"Forecast based on {len(valid_data)} years of historical data. "
                f"Trend shows {trend_direction} pattern (slope: {slope:.2f} per year). "
                f"Confidence: {confidence_band:.0%} (R² = {r_squared:.3f}). "
                f"Forecast range accounts for historical variability."
            )
            
            return {
                "can_forecast": True,
                "forecast": forecast_points,
                "confidence_band": confidence_band,
                "explanation": explanation,
                "insufficient_data_reason": None,
                "model_info": {
                    "method": "linear_regression",
                    "slope": round(slope, 4),
                    "intercept": round(intercept, 4),
                    "r_squared": round(r_squared, 4),
                    "historical_points": len(valid_data)
                }
            }
            
        except Exception as e:
            logger.error(f"Forecast calculation error: {e}")
            return {
                "can_forecast": False,
                "forecast": [],
                "confidence_band": 0.0,
                "explanation": None,
                "insufficient_data_reason": f"Forecast calculation failed: {str(e)}"
            }
    
    def _linear_regression(self, x: List[int], y: List[float]) -> Tuple[float, float, float]:
        """
        Simple linear regression: y = mx + b
        Returns: (slope, intercept, r_squared)
        """
        n = len(x)
        if n < 2:
            return 0.0, 0.0, 0.0
        
        # Calculate means
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        # Calculate slope and intercept
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0, y_mean, 0.0
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Calculate R² (coefficient of determination)
        y_pred = [slope * x[i] + intercept for i in range(n)]
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        
        return slope, intercept, r_squared
    
    def _calculate_standard_error(self, x: List[int], y: List[float], slope: float, intercept: float) -> float:
        """Calculate standard error of regression"""
        n = len(x)
        if n <= 2:
            return 0.0
        
        y_pred = [slope * x[i] + intercept for i in range(n)]
        residuals = [y[i] - y_pred[i] for i in range(n)]
        
        # Sum of squared residuals
        ss_res = sum(r ** 2 for r in residuals)
        
        # Standard error
        std_error = math.sqrt(ss_res / (n - 2)) if n > 2 else 0.0
        
        return std_error
    
    def forecast_department_kpi(
        self,
        institution_name: str,
        department_name: str,
        kpi_name: str,
        historical_batches: List[Dict[str, Any]]  # Batches with same institution+department
    ) -> Dict[str, Any]:
        """
        Forecast KPI for a specific department based on historical batches.
        
        Args:
            institution_name: Institution name
            department_name: Department name
            kpi_name: KPI to forecast (e.g., "overall_score", "fsr_score")
            historical_batches: List of batch dicts with kpi_results and academic_year
            
        Returns:
            Forecast result with can_forecast flag
        """
        # Extract historical data points
        historical_data = []
        
        for batch in historical_batches:
            # Skip invalid batches
            if batch.get("is_invalid", 0) == 1:
                continue
            
            # Extract academic year
            academic_year = batch.get("academic_year")
            if not academic_year:
                continue
            
            # Parse year (e.g., "2024-25" -> 2024)
            try:
                year = int(academic_year.split("-")[0])
            except:
                continue
            
            # Extract KPI value
            kpi_results = batch.get("kpi_results", {})
            if not isinstance(kpi_results, dict):
                continue
            
            kpi_value = None
            if isinstance(kpi_results.get(kpi_name), dict):
                kpi_value = kpi_results[kpi_name].get("value")
            elif kpi_name in kpi_results:
                kpi_value = kpi_results[kpi_name]
            
            if kpi_value is not None and isinstance(kpi_value, (int, float)):
                historical_data.append({
                    "year": year,
                    "value": float(kpi_value)
                })
        
        # Sort by year
        historical_data.sort(key=lambda x: x["year"])
        
        # Forecast
        return self.forecast_kpi(historical_data, forecast_years=3, kpi_name=kpi_name)

