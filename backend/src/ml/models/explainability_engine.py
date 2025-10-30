"""
Explainability Engine for EFFICODE-ACRR using SHAP and LIME
Provides interpretable explanations for ML optimization decisions
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Callable
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logging.warning("SHAP not available. Install with: pip install shap")

try:
    from lime.lime_text import LimeTextExplainer
    from lime.lime_tabular import LimeTabularExplainer
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False
    logging.warning("LIME not available. Install with: pip install lime")

from ...data_models import ExplainabilityResult, BaseExplainabilityEngine
from ...config import Config
from .complexity_predictor import ComplexityPredictor

logger = logging.getLogger('efficode.explainability')

class SHAPAnalyzer:
    """SHAP-based explainability analyzer"""
    
    def __init__(self):
        self.explainer = None
        self.background_data = None
    
    def initialize_explainer(self, model: Any, background_data: np.ndarray, 
                           model_type: str = 'tree'):
        """Initialize SHAP explainer for the given model"""
        if not SHAP_AVAILABLE:
            raise ImportError("SHAP is not available")
        
        try:
            if model_type == 'tree':
                # For tree-based models (Random Forest, LightGBM)
                self.explainer = shap.TreeExplainer(model)
            elif model_type == 'linear':
                # For linear models
                self.explainer = shap.LinearExplainer(model, background_data)
            elif model_type == 'kernel':
                # For any model (slower but more general)
                self.explainer = shap.KernelExplainer(model.predict, background_data)
            else:
                # Default to kernel explainer
                self.explainer = shap.KernelExplainer(model.predict, background_data)
            
            self.background_data = background_data
            logger.info(f"SHAP explainer initialized with type: {model_type}")
            
        except Exception as e:
            logger.error(f"Error initializing SHAP explainer: {e}")
            raise
    
    def explain_prediction(self, features: np.ndarray, 
                         feature_names: List[str]) -> Dict[str, float]:
        """Generate SHAP explanation for a single prediction"""
        if not self.explainer:
            raise RuntimeError("SHAP explainer not initialized")
        
        try:
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(features)
            
            # Handle different output formats
            if isinstance(shap_values, list):
                # Multi-class case - use the first class or average
                shap_values = shap_values[0] if len(shap_values) > 0 else shap_values
            
            # Ensure we have the right shape
            if len(shap_values.shape) > 1:
                shap_values = shap_values[0]  # Take first sample if batch
            
            # Create feature importance dictionary
            feature_importance = {}
            for i, name in enumerate(feature_names):
                if i < len(shap_values):
                    feature_importance[name] = float(shap_values[i])
            
            return feature_importance
            
        except Exception as e:
            logger.error(f"Error generating SHAP explanation: {e}")
            return {}
    
    def generate_waterfall_plot(self, features: np.ndarray, feature_names: List[str], 
                              save_path: Optional[str] = None) -> Optional[str]:
        """Generate SHAP waterfall plot"""
        if not self.explainer:
            return None
        
        try:
            shap_values = self.explainer.shap_values(features)
            
            # Handle different output formats
            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            if len(shap_values.shape) > 1:
                shap_values = shap_values[0]
            
            # Create waterfall plot
            plt.figure(figsize=(10, 6))
            shap.waterfall_plot(
                shap.Explanation(
                    values=shap_values,
                    base_values=self.explainer.expected_value if hasattr(self.explainer, 'expected_value') else 0,
                    data=features[0] if len(features.shape) > 1 else features,
                    feature_names=feature_names
                ),
                show=False
            )
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close()
                return save_path
            else:
                plt.show()
                return None
                
        except Exception as e:
            logger.error(f"Error generating waterfall plot: {e}")
            return None
    
    def get_top_features(self, features: np.ndarray, feature_names: List[str], 
                        top_k: int = 5) -> List[Tuple[str, float]]:
        """Get top K most important features"""
        feature_importance = self.explain_prediction(features, feature_names)
        
        # Sort by absolute importance
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        return sorted_features[:top_k]

class LIMEAnalyzer:
    """LIME-based explainability analyzer"""
    
    def __init__(self):
        self.text_explainer = None
        self.tabular_explainer = None
    
    def initialize_text_explainer(self, class_names: List[str]):
        """Initialize LIME text explainer"""
        if not LIME_AVAILABLE:
            raise ImportError("LIME is not available")
        
        try:
            self.text_explainer = LimeTextExplainer(
                class_names=class_names,
                mode='classification'
            )
            logger.info("LIME text explainer initialized")
        except Exception as e:
            logger.error(f"Error initializing LIME text explainer: {e}")
            raise
    
    def initialize_tabular_explainer(self, training_data: np.ndarray, 
                                   feature_names: List[str], 
                                   class_names: List[str]):
        """Initialize LIME tabular explainer"""
        if not LIME_AVAILABLE:
            raise ImportError("LIME is not available")
        
        try:
            self.tabular_explainer = LimeTabularExplainer(
                training_data,
                feature_names=feature_names,
                class_names=class_names,
                mode='classification'
            )
            logger.info("LIME tabular explainer initialized")
        except Exception as e:
            logger.error(f"Error initializing LIME tabular explainer: {e}")
            raise
    
    def explain_code_prediction(self, code: str, predict_fn: Callable, 
                              num_features: int = 10) -> Dict[str, Any]:
        """Explain prediction for code text"""
        if not self.text_explainer:
            raise RuntimeError("LIME text explainer not initialized")
        
        try:
            explanation = self.text_explainer.explain_instance(
                code,
                predict_fn,
                num_features=num_features
            )
            
            # Extract explanation data
            explanation_data = {
                'text_explanation': explanation.as_list(),
                'prediction_probabilities': explanation.predict_proba.tolist(),
                'score': explanation.score
            }
            
            return explanation_data
            
        except Exception as e:
            logger.error(f"Error generating LIME code explanation: {e}")
            return {}
    
    def explain_feature_prediction(self, features: np.ndarray, predict_fn: Callable,
                                 num_features: int = 10) -> Dict[str, Any]:
        """Explain prediction for feature vector"""
        if not self.tabular_explainer:
            raise RuntimeError("LIME tabular explainer not initialized")
        
        try:
            explanation = self.tabular_explainer.explain_instance(
                features,
                predict_fn,
                num_features=num_features
            )
            
            # Extract explanation data
            explanation_data = {
                'feature_explanation': explanation.as_list(),
                'prediction_probabilities': explanation.predict_proba.tolist(),
                'score': explanation.score,
                'intercept': explanation.intercept[0] if explanation.intercept else 0
            }
            
            return explanation_data
            
        except Exception as e:
            logger.error(f"Error generating LIME feature explanation: {e}")
            return {}

class ExplainabilityEngine(BaseExplainabilityEngine):
    """Main explainability engine combining SHAP and LIME"""
    
    def __init__(self):
        self.shap_analyzer = SHAPAnalyzer() if SHAP_AVAILABLE else None
        self.lime_analyzer = LIMEAnalyzer() if LIME_AVAILABLE else None
        self.complexity_predictor = None
        self.feature_names = []
    
    def initialize(self, complexity_predictor: ComplexityPredictor, 
                  background_data: Optional[np.ndarray] = None):
        """Initialize the explainability engine with models"""
        self.complexity_predictor = complexity_predictor
        
        if hasattr(complexity_predictor, 'feature_names'):
            self.feature_names = complexity_predictor.feature_names
        
        # Initialize SHAP if available
        if self.shap_analyzer and complexity_predictor.model:
            try:
                if background_data is None:
                    # Create dummy background data
                    background_data = np.zeros((10, len(self.feature_names)))
                
                model_type = 'tree' if hasattr(complexity_predictor.model, 'feature_importances_') else 'kernel'
                self.shap_analyzer.initialize_explainer(
                    complexity_predictor.model,
                    background_data,
                    model_type
                )
            except Exception as e:
                logger.warning(f"Could not initialize SHAP: {e}")
                self.shap_analyzer = None
        
        # Initialize LIME if available
        if self.lime_analyzer and complexity_predictor.label_encoder:
            try:
                class_names = list(complexity_predictor.label_encoder.classes_)
                self.lime_analyzer.initialize_text_explainer(class_names)
                
                if background_data is not None:
                    self.lime_analyzer.initialize_tabular_explainer(
                        background_data,
                        self.feature_names,
                        class_names
                    )
            except Exception as e:
                logger.warning(f"Could not initialize LIME: {e}")
                self.lime_analyzer = None
    
    def explain_optimization(self, original_code: str, optimized_code: str, 
                           model_output: Any) -> ExplainabilityResult:
        """Generate comprehensive explainability analysis"""
        
        if not self.complexity_predictor:
            return ExplainabilityResult(
                decision_rationale="Explainability engine not properly initialized"
            )
        
        try:
            # Extract features from the original code
            features = self.complexity_predictor.extract_features(original_code)
            feature_vector = np.array([features.get(name, 0) for name in self.feature_names]).reshape(1, -1)
            
            result = ExplainabilityResult()
            
            # Generate SHAP analysis
            if self.shap_analyzer:
                try:
                    shap_values = self.shap_analyzer.explain_prediction(feature_vector, self.feature_names)
                    result.shap_values = shap_values
                    
                    # Get top features
                    top_features = self.shap_analyzer.get_top_features(feature_vector, self.feature_names)
                    result.key_features.extend([f[0] for f in top_features[:5]])
                    
                except Exception as e:
                    logger.error(f"SHAP analysis failed: {e}")
            
            # Generate LIME analysis
            if self.lime_analyzer and self.lime_analyzer.tabular_explainer:
                try:
                    def predict_fn(x):
                        return self.complexity_predictor.model.predict_proba(x)
                    
                    lime_explanation = self.lime_analyzer.explain_feature_prediction(
                        feature_vector[0], predict_fn
                    )
                    result.lime_explanation = lime_explanation
                    
                except Exception as e:
                    logger.error(f"LIME analysis failed: {e}")
            
            # Generate decision rationale
            result.decision_rationale = self._generate_decision_rationale(
                original_code, optimized_code, features, result
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in explainability analysis: {e}")
            return ExplainabilityResult(
                decision_rationale=f"Error in explainability analysis: {str(e)}"
            )
    
    def _generate_decision_rationale(self, original_code: str, optimized_code: str,
                                   features: Dict[str, Any], 
                                   explainability_result: ExplainabilityResult) -> str:
        """Generate human-readable decision rationale"""
        
        rationale_parts = []
        
        # Analyze code changes
        if original_code != optimized_code:
            rationale_parts.append("The code was modified to improve performance.")
            
            # Check for specific patterns
            if features.get('recursive_calls', 0) > 0:
                rationale_parts.append("Recursive patterns were detected and optimized.")
            
            if features.get('nested_loops', 0) > 0:
                rationale_parts.append("Nested loop structures were identified for optimization.")
            
            if features.get('num_loops', 0) > 0:
                rationale_parts.append("Loop structures were analyzed for efficiency improvements.")
        
        # Add SHAP insights
        if explainability_result.shap_values:
            top_shap_features = sorted(
                explainability_result.shap_values.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:3]
            
            if top_shap_features:
                feature_names = [f[0].replace('_', ' ') for f in top_shap_features]
                rationale_parts.append(
                    f"Key factors in the decision: {', '.join(feature_names)}."
                )
        
        # Add complexity insights
        complexity_features = [
            'recursive_calls', 'nested_loops', 'num_loops', 'fibonacci_pattern'
        ]
        detected_patterns = [f for f in complexity_features if features.get(f, 0) > 0]
        
        if detected_patterns:
            pattern_names = [p.replace('_', ' ') for p in detected_patterns]
            rationale_parts.append(
                f"Detected algorithmic patterns: {', '.join(pattern_names)}."
            )
        
        # Default rationale if nothing specific found
        if not rationale_parts:
            rationale_parts.append("The optimization decision was based on general code analysis.")
        
        return " ".join(rationale_parts)
    
    def generate_shap_analysis(self, code: str, model: Any) -> Dict[str, float]:
        """Generate SHAP analysis for the given code and model"""
        if not self.shap_analyzer or not self.complexity_predictor:
            return {}
        
        try:
            features = self.complexity_predictor.extract_features(code)
            feature_vector = np.array([features.get(name, 0) for name in self.feature_names]).reshape(1, -1)
            
            return self.shap_analyzer.explain_prediction(feature_vector, self.feature_names)
            
        except Exception as e:
            logger.error(f"Error generating SHAP analysis: {e}")
            return {}
    
    def create_explanation_report(self, code: str, optimization_result: Any, 
                                save_path: Optional[str] = None) -> str:
        """Create a comprehensive explanation report"""
        
        report_lines = [
            "# EFFICODE Explainability Report",
            f"Generated on: {pd.Timestamp.now()}",
            "",
            "## Code Analysis",
            f"```python\n{code}\n```",
            ""
        ]
        
        # Add feature analysis
        if self.complexity_predictor:
            features = self.complexity_predictor.extract_features(code)
            
            report_lines.extend([
                "## Feature Analysis",
                f"- Code length: {features.get('code_length', 0)} characters",
                f"- Number of functions: {features.get('num_functions', 0)}",
                f"- Number of loops: {features.get('num_loops', 0)}",
                f"- Recursive calls: {features.get('recursive_calls', 0)}",
                f"- Nesting depth: {features.get('max_nesting_depth', 0)}",
                ""
            ])
        
        # Add explainability analysis
        explainability = self.explain_optimization(code, code, None)
        
        if explainability.shap_values:
            report_lines.extend([
                "## SHAP Feature Importance",
                ""
            ])
            
            for feature, importance in sorted(explainability.shap_values.items(), 
                                            key=lambda x: abs(x[1]), reverse=True)[:10]:
                report_lines.append(f"- {feature}: {importance:.4f}")
            
            report_lines.append("")
        
        if explainability.decision_rationale:
            report_lines.extend([
                "## Decision Rationale",
                explainability.decision_rationale,
                ""
            ])
        
        report_content = "\n".join(report_lines)
        
        # Save report if path provided
        if save_path:
            try:
                with open(save_path, 'w') as f:
                    f.write(report_content)
                logger.info(f"Explanation report saved to {save_path}")
            except Exception as e:
                logger.error(f"Error saving report: {e}")
        
        return report_content
    
    def is_available(self) -> Dict[str, bool]:
        """Check availability of explainability components"""
        return {
            'shap': SHAP_AVAILABLE and self.shap_analyzer is not None,
            'lime': LIME_AVAILABLE and self.lime_analyzer is not None,
            'complexity_predictor': self.complexity_predictor is not None
        }