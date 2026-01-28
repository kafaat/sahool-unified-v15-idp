"""
Tests for Advanced ML Features - Yield Engine
==============================================
اختبارات المزايا المتقدمة للتعلم الآلي

Tests for:
- Boruta feature selection
- SBO hyperparameter optimization
- SHAP explainability

Author: SAHOOL Platform Team
Updated: January 2026
"""

import pytest
import numpy as np


class TestBorutaFeatureSelector:
    """Tests for Boruta feature selection algorithm."""

    def test_boruta_initialization(self):
        """Test Boruta selector initialization."""
        from ml.feature_selection import BorutaFeatureSelector
        
        selector = BorutaFeatureSelector(max_iterations=50, alpha=0.05)
        assert selector.max_iterations == 50
        assert selector.alpha == 0.05
        assert selector.verbose is True

    def test_boruta_fit(self):
        """Test Boruta feature selection on synthetic data."""
        from ml.feature_selection import BorutaFeatureSelector
        
        # Create synthetic data with known important features
        np.random.seed(42)
        n_samples = 100
        n_features = 10
        
        X = np.random.rand(n_samples, n_features)
        # Features 0, 2, 5 are important
        y = 2 * X[:, 0] + 3 * X[:, 2] + 1.5 * X[:, 5] + np.random.randn(n_samples) * 0.1
        
        feature_names = [f"feature_{i}" for i in range(n_features)]
        feature_names_ar = [f"متغير_{i}" for i in range(n_features)]
        
        selector = BorutaFeatureSelector(max_iterations=20, verbose=False)
        result = selector.fit(X, y, feature_names, feature_names_ar)
        
        # Assertions
        assert len(result.feature_importances) == n_features
        assert result.n_confirmed > 0
        assert result.n_confirmed + result.n_tentative + result.n_rejected == n_features
        assert len(result.selected_features) > 0
        assert result.execution_time_seconds > 0

    def test_boruta_transform(self):
        """Test transforming data to selected features."""
        from ml.feature_selection import BorutaFeatureSelector
        
        np.random.seed(42)
        X = np.random.rand(50, 8)
        y = np.random.rand(50)
        
        feature_names = [f"f{i}" for i in range(8)]
        
        selector = BorutaFeatureSelector(max_iterations=10, verbose=False)
        selector.fit(X, y, feature_names)
        
        X_transformed = selector.transform(X)
        assert X_transformed.shape[0] == X.shape[0]
        assert X_transformed.shape[1] <= X.shape[1]

    def test_feature_importance_report(self):
        """Test feature importance report generation."""
        from ml.feature_selection import BorutaFeatureSelector, create_feature_importance_report
        
        np.random.seed(42)
        X = np.random.rand(50, 5)
        y = np.random.rand(50)
        
        feature_names = ["rainfall", "temperature", "soil_moisture", "nitrogen", "ndvi"]
        feature_names_ar = ["الأمطار", "الحرارة", "رطوبة التربة", "النيتروجين", "NDVI"]
        
        selector = BorutaFeatureSelector(verbose=False)
        result = selector.fit(X, y, feature_names, feature_names_ar)
        
        report = create_feature_importance_report(result)
        
        assert "summary" in report
        assert "summary_ar" in report
        assert "selected_features" in report
        assert "feature_importances" in report
        assert report["summary"]["total_features"] == 5


class TestSatinBowerbirdOptimizer:
    """Tests for SBO hyperparameter optimization."""

    def test_sbo_initialization(self):
        """Test SBO optimizer initialization."""
        from ml.optimization import SatinBowerbirdOptimizer
        
        bounds = {
            "learning_rate": (0.0001, 0.01),
            "n_layers": (2, 10),
        }
        
        optimizer = SatinBowerbirdOptimizer(
            bounds=bounds,
            population_size=20,
            max_iterations=30,
        )
        
        assert optimizer.population_size == 20
        assert optimizer.max_iterations == 30
        assert len(optimizer.param_names) == 2

    def test_sbo_optimization(self):
        """Test SBO optimization on simple objective function."""
        from ml.optimization import SatinBowerbirdOptimizer
        
        # Simple quadratic objective: maximize -(x-5)^2 - (y-3)^2
        # Optimal: x=5, y=3, max_value=0
        def objective(params):
            x = params["x"]
            y = params["y"]
            return -(x - 5)**2 - (y - 3)**2
        
        bounds = {
            "x": (0, 10),
            "y": (0, 10),
        }
        
        optimizer = SatinBowerbirdOptimizer(
            bounds=bounds,
            population_size=10,
            max_iterations=20,
            verbose=False,
        )
        
        result = optimizer.optimize(objective)
        
        # Assertions
        assert "x" in result.best_params
        assert "y" in result.best_params
        assert len(result.convergence_history) == result.n_iterations + 1
        assert result.execution_time_seconds > 0
        
        # Check convergence (should be close to optimal)
        assert abs(result.best_params["x"] - 5) < 2  # Within 2 units
        assert abs(result.best_params["y"] - 3) < 2

    def test_sbo_integer_parameters(self):
        """Test SBO with integer parameters."""
        from ml.optimization import SatinBowerbirdOptimizer
        
        def objective(params):
            # Simple: prefer n_layers=5
            return 1.0 - abs(params["n_layers"] - 5) / 10
        
        bounds = {"n_layers": (2, 10)}
        
        optimizer = SatinBowerbirdOptimizer(bounds=bounds, max_iterations=15, verbose=False)
        result = optimizer.optimize(objective)
        
        # Check that n_layers is integer
        assert isinstance(result.best_params["n_layers"], int)

    def test_sbo_vs_grid_search_comparison(self):
        """Test SBO comparison with grid search."""
        from ml.optimization import compare_with_grid_search
        
        def objective(params):
            return -(params["x"] - 3)**2
        
        bounds = {"x": (0, 10)}
        
        comparison = compare_with_grid_search(objective, bounds, n_grid_points=5)
        
        assert "sbo" in comparison
        assert "grid_search" in comparison
        assert "improvement" in comparison
        assert "best_score" in comparison["sbo"]
        assert "time_seconds" in comparison["sbo"]


class TestSHAPExplainer:
    """Tests for SHAP model explainability."""

    def test_shap_initialization(self):
        """Test SHAP explainer initialization."""
        from ml.explainability import SHAPExplainer
        from sklearn.linear_model import LinearRegression
        
        model = LinearRegression()
        X_train = np.random.rand(50, 4)
        y_train = np.random.rand(50)
        model.fit(X_train, y_train)
        
        explainer = SHAPExplainer(model, model_type="linear")
        
        assert explainer.model == model
        assert explainer.model_type == "linear"

    def test_shap_fit_and_explain(self):
        """Test SHAP fitting and explanation."""
        from ml.explainability import SHAPExplainer
        from sklearn.linear_model import LinearRegression
        
        # Create simple linear model
        np.random.seed(42)
        X_train = np.random.rand(100, 5) * 10
        # y = 2*x0 + 3*x1 + noise
        y_train = 2 * X_train[:, 0] + 3 * X_train[:, 1] + np.random.randn(100) * 0.1
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        explainer = SHAPExplainer(model, model_type="linear")
        explainer.fit(X_train, max_samples=50)
        
        # Explain single prediction
        X_test = np.array([5.0, 4.0, 1.0, 2.0, 3.0])
        feature_names = ["rainfall", "temperature", "soil", "nitrogen", "ndvi"]
        feature_names_ar = ["الأمطار", "الحرارة", "التربة", "النيتروجين", "NDVI"]
        
        explanation = explainer.explain(X_test, feature_names, feature_names_ar)
        
        # Assertions
        assert explanation.prediction_value > 0
        assert len(explanation.feature_contributions) == 5
        assert len(explanation.top_positive_features) <= 3
        assert explanation.explanation_text != ""
        assert explanation.explanation_text_ar != ""

    def test_shap_explanation_report(self):
        """Test SHAP explanation report generation."""
        from ml.explainability import SHAPExplainer, create_explanation_report
        from sklearn.linear_model import LinearRegression
        
        np.random.seed(42)
        X_train = np.random.rand(50, 3)
        y_train = np.random.rand(50)
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        explainer = SHAPExplainer(model, model_type="linear")
        explainer.fit(X_train)
        
        X_test = np.array([0.5, 0.3, 0.8])
        feature_names = ["f1", "f2", "f3"]
        
        explanation = explainer.explain(X_test, feature_names)
        report = create_explanation_report(explanation)
        
        assert "prediction" in report
        assert "top_features" in report
        assert "contributions" in report
        assert "explanation" in report
        assert len(report["contributions"]) == 3

    def test_shap_fallback_when_unavailable(self):
        """Test fallback explanation when SHAP library unavailable."""
        from ml.explainability import SHAPExplainer
        from sklearn.linear_model import LinearRegression
        
        np.random.seed(42)
        X_train = np.random.rand(30, 4)
        y_train = np.random.rand(30)
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        explainer = SHAPExplainer(model, model_type="linear")
        # Force fallback by not fitting properly
        explainer.explainer = None
        explainer.expected_value = 0.5
        
        X_test = np.array([0.5, 0.3, 0.8, 0.2])
        feature_names = ["a", "b", "c", "d"]
        
        # Should still work with fallback
        explanation = explainer.explain(X_test, feature_names)
        
        assert explanation.prediction_value is not None
        assert len(explanation.feature_contributions) == 4


class TestMLIntegration:
    """Integration tests for ML modules."""

    def test_full_pipeline_feature_selection_to_optimization(self):
        """Test complete pipeline: feature selection -> optimization."""
        from ml.feature_selection import BorutaFeatureSelector
        from ml.optimization import SatinBowerbirdOptimizer
        
        # 1. Feature selection
        np.random.seed(42)
        X = np.random.rand(100, 8)
        y = 2 * X[:, 0] + 3 * X[:, 3] + np.random.randn(100) * 0.1
        
        feature_names = [f"feature_{i}" for i in range(8)]
        
        selector = BorutaFeatureSelector(max_iterations=10, verbose=False)
        boruta_result = selector.fit(X, y, feature_names)
        
        # 2. Use selected features for optimization
        n_selected = len(boruta_result.selected_features)
        
        def objective(params):
            # Dummy objective using n_features
            return 0.9 + 0.1 * (1 - abs(params["n_features"] - n_selected) / 8)
        
        bounds = {"n_features": (1, 8)}
        optimizer = SatinBowerbirdOptimizer(bounds=bounds, max_iterations=10, verbose=False)
        opt_result = optimizer.optimize(objective)
        
        # Both should complete successfully
        assert boruta_result.n_confirmed > 0
        assert opt_result.best_score > 0.8

    def test_yield_prediction_with_explainability(self):
        """Test yield prediction with SHAP explanation."""
        from ml.explainability import SHAPExplainer
        from sklearn.ensemble import RandomForestRegressor
        
        # Simulate yield prediction model
        np.random.seed(42)
        X_train = np.random.rand(200, 6) * 100  # 6 features
        # Yield = f(rainfall, temp, soil, nitrogen, irrigation, ndvi)
        y_train = (
            0.5 * X_train[:, 0] +  # rainfall
            0.3 * X_train[:, 1] +  # temperature
            0.2 * X_train[:, 5] +  # ndvi
            np.random.randn(200) * 5
        )
        
        model = RandomForestRegressor(n_estimators=10, max_depth=5, random_state=42)
        model.fit(X_train, y_train)
        
        # Explain prediction for a specific field
        explainer = SHAPExplainer(model, model_type="tree")
        explainer.fit(X_train, max_samples=50)
        
        X_field = np.array([250, 22, 7.2, 120, 80, 0.72])  # Sample field data
        feature_names = ["rainfall_mm", "temperature_c", "soil_ph", "nitrogen_ppm", "irrigation_mm", "ndvi"]
        
        explanation = explainer.explain(X_field, feature_names)
        
        # Verify we get meaningful explanation
        assert explanation.prediction_value > 0
        assert len(explanation.top_positive_features) > 0
        assert "rainfall" in explanation.explanation_text.lower() or "temperature" in explanation.explanation_text.lower()


@pytest.mark.unit
class TestMLModuleImports:
    """Test that all ML modules can be imported."""

    def test_import_feature_selection(self):
        """Test importing feature selection module."""
        from ml.feature_selection import BorutaFeatureSelector, FeatureImportance, BorutaResult
        assert BorutaFeatureSelector is not None
        assert FeatureImportance is not None
        assert BorutaResult is not None

    def test_import_optimization(self):
        """Test importing optimization module."""
        from ml.optimization import SatinBowerbirdOptimizer, OptimizationResult
        assert SatinBowerbirdOptimizer is not None
        assert OptimizationResult is not None

    def test_import_explainability(self):
        """Test importing explainability module."""
        from ml.explainability import SHAPExplainer, ExplanationResult
        assert SHAPExplainer is not None
        assert ExplanationResult is not None

    def test_import_ml_package(self):
        """Test importing ML package."""
        import ml
        assert hasattr(ml, "BorutaFeatureSelector")
        assert hasattr(ml, "SatinBowerbirdOptimizer")
        assert hasattr(ml, "SHAPExplainer")
