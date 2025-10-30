"""
Core data models and interfaces for EFFICODE-ACRR
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
from datetime import datetime
import json

class OptimizationLevel(Enum):
    """Optimization levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ValidationStatus(Enum):
    """Validation status for optimized code"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

@dataclass
class OptimizationRequest:
    """Request for code optimization"""
    code: str
    optimization_level: OptimizationLevel = OptimizationLevel.MEDIUM
    test_inputs: Optional[List[Any]] = None
    timeout: int = 60
    enable_explainability: bool = False
    target_complexity: Optional[str] = None
    use_ml: bool = True
    use_rule_based: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'code': self.code,
            'optimization_level': self.optimization_level.value,
            'test_inputs': self.test_inputs,
            'timeout': self.timeout,
            'enable_explainability': self.enable_explainability,
            'target_complexity': self.target_complexity,
            'use_ml': self.use_ml,
            'use_rule_based': self.use_rule_based
        }

@dataclass
class ComplexityPrediction:
    """Complexity prediction result"""
    symbolic_complexity: str  # e.g., "O(n log n)"
    numeric_estimate: float   # runtime estimate in seconds
    confidence: float         # prediction confidence [0, 1]
    feature_importance: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbolic_complexity': self.symbolic_complexity,
            'numeric_estimate': self.numeric_estimate,
            'confidence': self.confidence,
            'feature_importance': self.feature_importance
        }

@dataclass
class ExplainabilityResult:
    """Result from explainability analysis"""
    shap_values: Optional[Dict[str, float]] = None
    lime_explanation: Optional[Dict[str, Any]] = None
    attention_weights: Optional[Dict[str, float]] = None
    key_features: List[str] = field(default_factory=list)
    decision_rationale: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'shap_values': self.shap_values,
            'lime_explanation': self.lime_explanation,
            'attention_weights': self.attention_weights,
            'key_features': self.key_features,
            'decision_rationale': self.decision_rationale
        }

@dataclass
class OptimizationCandidate:
    """A candidate optimization result"""
    optimized_code: str
    confidence_score: float
    applied_techniques: List[str]
    complexity_improvement: Dict[str, Any]
    validation_status: ValidationStatus
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'optimized_code': self.optimized_code,
            'confidence_score': self.confidence_score,
            'applied_techniques': self.applied_techniques,
            'complexity_improvement': self.complexity_improvement,
            'validation_status': self.validation_status.value,
            'processing_time': self.processing_time
        }

@dataclass
class OptimizationResult:
    """Complete optimization result"""
    original_code: str
    optimized_code: str
    complexity_before: str
    complexity_after: str
    explanation: str
    applied_techniques: List[str]
    performance_improvement: float
    validation_status: ValidationStatus
    explainability_data: Optional[ExplainabilityResult] = None
    processing_time: float = 0.0
    confidence_score: float = 0.0
    candidates: List[OptimizationCandidate] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'original_code': self.original_code,
            'optimized_code': self.optimized_code,
            'complexity_before': self.complexity_before,
            'complexity_after': self.complexity_after,
            'explanation': self.explanation,
            'applied_techniques': self.applied_techniques,
            'performance_improvement': self.performance_improvement,
            'validation_status': self.validation_status.value,
            'explainability_data': self.explainability_data.to_dict() if self.explainability_data else None,
            'processing_time': self.processing_time,
            'confidence_score': self.confidence_score,
            'candidates': [c.to_dict() for c in self.candidates],
            'timestamp': self.timestamp.isoformat()
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

@dataclass
class TrainingExample:
    """Training example for ML models"""
    original_code: str
    optimized_code: str
    complexity_before: str
    complexity_after: str
    explanation: str
    applied_rules: List[str]
    category: str = "general"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'original_code': self.original_code,
            'optimized_code': self.optimized_code,
            'complexity_before': self.complexity_before,
            'complexity_after': self.complexity_after,
            'explanation': self.explanation,
            'applied_rules': self.applied_rules,
            'category': self.category
        }

@dataclass
class ModelMetrics:
    """Metrics for model evaluation"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    bleu_score: Optional[float] = None
    complexity_accuracy: Optional[float] = None
    optimization_success_rate: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'bleu_score': self.bleu_score,
            'complexity_accuracy': self.complexity_accuracy,
            'optimization_success_rate': self.optimization_success_rate
        }

# Base interfaces for ML components
class BaseOptimizer:
    """Base interface for optimizers"""
    
    def optimize(self, code: str, level: OptimizationLevel = OptimizationLevel.MEDIUM) -> OptimizationResult:
        """Optimize the given code"""
        raise NotImplementedError
    
    def get_applied_rules(self) -> List[Dict[str, Any]]:
        """Get list of applied optimization rules"""
        raise NotImplementedError

class BaseComplexityPredictor:
    """Base interface for complexity predictors"""
    
    def predict_complexity(self, code: str) -> ComplexityPrediction:
        """Predict the complexity of the given code"""
        raise NotImplementedError
    
    def extract_features(self, code: str) -> Dict[str, Any]:
        """Extract features from code for prediction"""
        raise NotImplementedError

class BaseExplainabilityEngine:
    """Base interface for explainability engines"""
    
    def explain_optimization(self, original_code: str, optimized_code: str, 
                           model_output: Any) -> ExplainabilityResult:
        """Generate explainability analysis for optimization decision"""
        raise NotImplementedError
    
    def generate_shap_analysis(self, code: str, model: Any) -> Dict[str, float]:
        """Generate SHAP analysis for the given code and model"""
        raise NotImplementedError

class BaseDatasetManager:
    """Base interface for dataset management"""
    
    def generate_synthetic_data(self, num_samples: int) -> List[TrainingExample]:
        """Generate synthetic training data"""
        raise NotImplementedError
    
    def load_dataset(self, path: str) -> List[TrainingExample]:
        """Load dataset from file"""
        raise NotImplementedError
    
    def save_dataset(self, examples: List[TrainingExample], path: str) -> bool:
        """Save dataset to file"""
        raise NotImplementedError

class BaseModelTrainer:
    """Base interface for model training"""
    
    def train_model(self, training_data: List[TrainingExample], 
                   validation_data: List[TrainingExample]) -> Dict[str, Any]:
        """Train a model on the given data"""
        raise NotImplementedError
    
    def evaluate_model(self, model: Any, test_data: List[TrainingExample]) -> ModelMetrics:
        """Evaluate model performance"""
        raise NotImplementedError
    
    def save_model(self, model: Any, path: str) -> bool:
        """Save trained model"""
        raise NotImplementedError
    
    def load_model(self, path: str) -> Any:
        """Load trained model"""
        raise NotImplementedError