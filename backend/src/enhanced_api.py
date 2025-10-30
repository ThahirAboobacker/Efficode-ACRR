"""
Enhanced API for EFFICODE-ACRR with full ML capabilities
Integrates all components: ML optimization, complexity prediction, explainability, and validation
"""

import os
import sys
import logging
import time
import json
import traceback
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import threading
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

# Add project paths
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from data_models import (
    OptimizationRequest, OptimizationResult, OptimizationLevel, 
    ValidationStatus, OptimizationCandidate
)
from config import Config
from dataset_manager import DatasetManager
from ml.models.ml_optimizer import MLOptimizer
from ml.models.complexity_predictor import ComplexityPredictor
from ml.models.explainability_engine import ExplainabilityEngine
from ml.training.model_trainer import ModelTrainer
from validation_sandbox import ValidationSandbox
from rule_based import RuleBasedOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Config.LOG_FILE)
    ]
)
logger = logging.getLogger('efficode.api')

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

# Global components
ml_optimizer = None
complexity_predictor = None
explainability_engine = None
rule_based_optimizer = None
validation_sandbox = None
model_trainer = None
dataset_manager = None
thread_pool = ThreadPoolExecutor(max_workers=4)

def initialize_components():
    """Initialize all EFFICODE components"""
    global ml_optimizer, complexity_predictor, explainability_engine
    global rule_based_optimizer, validation_sandbox, model_trainer, dataset_manager
    
    logger.info("Initializing EFFICODE components...")
    
    try:
        # Create directories
        Config.create_directories()
        
        # Initialize dataset manager
        dataset_manager = DatasetManager()
        logger.info("Dataset manager initialized")
        
        # Initialize rule-based optimizer (always available)
        rule_based_optimizer = RuleBasedOptimizer()
        logger.info("Rule-based optimizer initialized")
        
        # Initialize validation sandbox
        validation_sandbox = ValidationSandbox()
        logger.info("Validation sandbox initialized")
        
        # Initialize model trainer
        model_trainer = ModelTrainer()
        
        # Try to load trained models
        trained_models = model_trainer.load_trained_models()
        
        # Initialize ML optimizer
        if Config.OPTIMIZATION_CONFIG['use_neural_model']:
            try:
                ml_optimizer = MLOptimizer()
                if ml_optimizer.load_models():
                    logger.info("ML optimizer initialized with pre-trained models")
                else:
                    logger.warning("ML optimizer initialized but no pre-trained models found")
            except Exception as e:
                logger.warning(f"Could not initialize ML optimizer: {e}")
                ml_optimizer = None
        
        # Initialize complexity predictor
        try:
            complexity_predictor = ComplexityPredictor()
            if 'complexity_rf' in trained_models:
                complexity_predictor = trained_models['complexity_rf']
                logger.info("Complexity predictor loaded from trained model")
            else:
                logger.info("Complexity predictor initialized (not trained)")
        except Exception as e:
            logger.warning(f"Could not initialize complexity predictor: {e}")
            complexity_predictor = None
        
        # Initialize explainability engine
        if Config.EXPLAINABILITY_CONFIG['enable_shap'] or Config.EXPLAINABILITY_CONFIG['enable_lime']:
            try:
                explainability_engine = ExplainabilityEngine()
                if complexity_predictor:
                    explainability_engine.initialize(complexity_predictor)
                logger.info("Explainability engine initialized")
            except Exception as e:
                logger.warning(f"Could not initialize explainability engine: {e}")
                explainability_engine = None
        
        logger.info("EFFICODE components initialization completed")
        
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        logger.error(traceback.format_exc())

class HybridOptimizer:
    """Hybrid optimizer combining rule-based and ML approaches"""
    
    def __init__(self):
        self.applied_techniques = []
    
    def optimize(self, request: OptimizationRequest) -> OptimizationResult:
        """Perform hybrid optimization"""
        start_time = time.time()
        self.applied_techniques = []
        
        original_code = request.code
        candidates = []
        
        # Step 1: Rule-based optimization
        if request.use_rule_based and rule_based_optimizer:
            try:
                rule_optimized, orig_complexity, opt_complexity, rule_explanation = rule_based_optimizer.optimize(
                    original_code, request.optimization_level.value
                )
                
                if rule_optimized != original_code:
                    candidate = OptimizationCandidate(
                        optimized_code=rule_optimized,
                        confidence_score=0.9,  # High confidence for rule-based
                        applied_techniques=['rule_based'],
                        complexity_improvement={
                            'original': orig_complexity,
                            'optimized': opt_complexity,
                            'explanation': rule_explanation
                        },
                        validation_status=ValidationStatus.SKIPPED
                    )
                    candidates.append(candidate)
                    self.applied_techniques.extend(['rule_based'])
                    
            except Exception as e:
                logger.error(f"Rule-based optimization failed: {e}")
        
        # Step 2: ML-based optimization
        if request.use_ml and ml_optimizer:
            try:
                ml_candidates = ml_optimizer.optimize(original_code, request.optimization_level)
                candidates.extend(ml_candidates)
                self.applied_techniques.extend(['ml_optimization'])
                
            except Exception as e:
                logger.error(f"ML optimization failed: {e}")
        
        # Step 3: Rank candidates by confidence
        candidates.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Step 4: Validate best candidates
        best_candidate = None
        for candidate in candidates[:Config.OPTIMIZATION_CONFIG['max_candidates']]:
            if validation_sandbox:
                try:
                    validation_result = validation_sandbox.validate_optimization(
                        original_code, candidate.optimized_code
                    )
                    
                    if validation_result['functional_equivalence']:
                        candidate.validation_status = ValidationStatus.PASSED
                        candidate.complexity_improvement.update(validation_result.get('details', {}))
                        best_candidate = candidate
                        break
                    else:
                        candidate.validation_status = ValidationStatus.FAILED
                        
                except Exception as e:
                    logger.error(f"Validation failed: {e}")
                    candidate.validation_status = ValidationStatus.ERROR
        
        # Step 5: Generate complexity prediction
        complexity_before = "O(n)"
        complexity_after = "O(n)"
        
        if complexity_predictor:
            try:
                orig_prediction = complexity_predictor.predict_complexity(original_code)
                complexity_before = orig_prediction.symbolic_complexity
                
                if best_candidate:
                    opt_prediction = complexity_predictor.predict_complexity(best_candidate.optimized_code)
                    complexity_after = opt_prediction.symbolic_complexity
                    
            except Exception as e:
                logger.error(f"Complexity prediction failed: {e}")
        
        # Step 6: Generate explanation
        explanation = self._generate_explanation(original_code, best_candidate, candidates)
        
        # Step 7: Explainability analysis (if requested)
        explainability_data = None
        if request.enable_explainability and explainability_engine and best_candidate:
            try:
                explainability_data = explainability_engine.explain_optimization(
                    original_code, best_candidate.optimized_code, None
                )
            except Exception as e:
                logger.error(f"Explainability analysis failed: {e}")
        
        # Create final result
        processing_time = time.time() - start_time
        
        if best_candidate:
            result = OptimizationResult(
                original_code=original_code,
                optimized_code=best_candidate.optimized_code,
                complexity_before=complexity_before,
                complexity_after=complexity_after,
                explanation=explanation,
                applied_techniques=self.applied_techniques,
                performance_improvement=best_candidate.complexity_improvement.get('time_improvement_percent', 0.0),
                validation_status=best_candidate.validation_status,
                explainability_data=explainability_data,
                processing_time=processing_time,
                confidence_score=best_candidate.confidence_score,
                candidates=candidates
            )
        else:
            # No optimization found
            result = OptimizationResult(
                original_code=original_code,
                optimized_code=original_code,
                complexity_before=complexity_before,
                complexity_after=complexity_before,
                explanation="No suitable optimizations found that pass validation.",
                applied_techniques=[],
                performance_improvement=0.0,
                validation_status=ValidationStatus.PASSED,
                explainability_data=explainability_data,
                processing_time=processing_time,
                confidence_score=1.0,
                candidates=candidates
            )
        
        return result
    
    def _generate_explanation(self, original_code: str, best_candidate: Optional[OptimizationCandidate], 
                            all_candidates: List[OptimizationCandidate]) -> str:
        """Generate human-readable explanation"""
        
        if not best_candidate:
            return "No optimizations were applied. The code may already be optimal or no safe optimizations were found."
        
        explanation_parts = []
        
        # Describe applied techniques
        if 'rule_based' in self.applied_techniques:
            explanation_parts.append("Applied rule-based optimizations")
        
        if 'ml_optimization' in self.applied_techniques:
            explanation_parts.append("Applied machine learning-based optimizations")
        
        # Describe specific improvements
        complexity_improvement = best_candidate.complexity_improvement
        if 'original' in complexity_improvement and 'optimized' in complexity_improvement:
            orig_complexity = complexity_improvement['original']
            opt_complexity = complexity_improvement['optimized']
            if orig_complexity != opt_complexity:
                explanation_parts.append(f"Improved complexity from {orig_complexity} to {opt_complexity}")
        
        # Add performance information
        if 'time_improvement_percent' in complexity_improvement:
            improvement = complexity_improvement['time_improvement_percent']
            if improvement > 0:
                explanation_parts.append(f"Expected performance improvement: {improvement:.1f}%")
        
        # Add validation information
        if best_candidate.validation_status == ValidationStatus.PASSED:
            explanation_parts.append("Optimization validated for functional equivalence")
        
        return ". ".join(explanation_parts) + "."

# Initialize components on startup
initialize_components()
hybrid_optimizer = HybridOptimizer()

# API Routes

@app.before_request
def before_request():
    """Before request handler"""
    g.start_time = time.time()

@app.after_request
def after_request(response):
    """After request handler"""
    if hasattr(g, 'start_time'):
        elapsed = time.time() - g.start_time
        response.headers['X-Processing-Time'] = f"{elapsed:.3f}"
    return response

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'name': 'EFFICODE-ACRR',
        'version': Config.API_VERSION,
        'description': 'AI-Powered Python Code Optimization System',
        'endpoints': {
            'optimize': '/optimize',
            'predict_complexity': '/predict-complexity',
            'explain_optimization': '/explain-optimization',
            'batch_optimize': '/batch-optimize',
            'health': '/health',
            'models': '/models',
            'train': '/train'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check"""
    components_status = {
        'rule_based_optimizer': rule_based_optimizer is not None,
        'ml_optimizer': ml_optimizer is not None,
        'complexity_predictor': complexity_predictor is not None and getattr(complexity_predictor, 'is_trained', False),
        'explainability_engine': explainability_engine is not None,
        'validation_sandbox': validation_sandbox is not None,
        'dataset_manager': dataset_manager is not None
    }
    
    return jsonify({
        'status': 'healthy',
        'components': components_status,
        'config': {
            'use_ml': Config.OPTIMIZATION_CONFIG['use_neural_model'],
            'use_rule_based': Config.OPTIMIZATION_CONFIG['use_rule_based'],
            'enable_explainability': Config.EXPLAINABILITY_CONFIG['enable_shap'],
            'validation_enabled': Config.OPTIMIZATION_CONFIG['validation_enabled']
        }
    })

@app.route('/optimize', methods=['POST', 'OPTIONS'])
def optimize_code():
    """Main optimization endpoint with full ML capabilities"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    try:
        # Parse request
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'Missing required parameter: code'}), 400
        
        # Create optimization request
        opt_request = OptimizationRequest(
            code=data['code'],
            optimization_level=OptimizationLevel(data.get('level', 'medium')),
            test_inputs=data.get('test_inputs'),
            timeout=data.get('timeout', 60),
            enable_explainability=data.get('enable_explainability', False),
            target_complexity=data.get('target_complexity'),
            use_ml=data.get('use_ml', Config.OPTIMIZATION_CONFIG['use_neural_model']),
            use_rule_based=data.get('use_rule_based', Config.OPTIMIZATION_CONFIG['use_rule_based'])
        )
        
        # Validate code length
        if len(opt_request.code) > Config.OPTIMIZATION_CONFIG['max_code_length']:
            return jsonify({
                'error': f'Code too long (max {Config.OPTIMIZATION_CONFIG["max_code_length"]} characters)'
            }), 400
        
        # Perform optimization
        result = hybrid_optimizer.optimize(opt_request)
        
        # Convert to API response format
        response = {
            'original_code': result.original_code,
            'optimized_code': result.optimized_code,
            'original_complexity': result.complexity_before,
            'optimized_complexity': result.complexity_after,
            'explanation': result.explanation,
            'applied_techniques': result.applied_techniques,
            'performance_improvement': result.performance_improvement,
            'validation_status': result.validation_status.value,
            'processing_time': result.processing_time,
            'confidence_score': result.confidence_score,
            'status': 'success'
        }
        
        # Add explainability data if available
        if result.explainability_data:
            response['explainability'] = result.explainability_data.to_dict()
        
        # Add candidate information for debugging
        if data.get('include_candidates', False):
            response['candidates'] = [c.to_dict() for c in result.candidates]
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'status': 'error',
            'processing_time': time.time() - g.start_time if hasattr(g, 'start_time') else 0
        }), 500

@app.route('/predict-complexity', methods=['POST'])
def predict_complexity():
    """Standalone complexity prediction endpoint"""
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'Missing required parameter: code'}), 400
        
        if not complexity_predictor:
            return jsonify({'error': 'Complexity predictor not available'}), 503
        
        prediction = complexity_predictor.predict_complexity(data['code'])
        
        return jsonify({
            'complexity': prediction.symbolic_complexity,
            'numeric_estimate': prediction.numeric_estimate,
            'confidence': prediction.confidence,
            'feature_importance': prediction.feature_importance,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Complexity prediction error: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/explain-optimization', methods=['POST'])
def explain_optimization():
    """Detailed explainability analysis endpoint"""
    try:
        data = request.get_json()
        if not data or 'original_code' not in data or 'optimized_code' not in data:
            return jsonify({'error': 'Missing required parameters: original_code, optimized_code'}), 400
        
        if not explainability_engine:
            return jsonify({'error': 'Explainability engine not available'}), 503
        
        explanation = explainability_engine.explain_optimization(
            data['original_code'], 
            data['optimized_code'], 
            None
        )
        
        # Generate detailed report if requested
        if data.get('generate_report', False):
            report = explainability_engine.create_explanation_report(
                data['original_code'], 
                explanation
            )
            return jsonify({
                'explanation': explanation.to_dict(),
                'report': report,
                'status': 'success'
            })
        
        return jsonify({
            'explanation': explanation.to_dict(),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Explainability error: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/batch-optimize', methods=['POST'])
def batch_optimize():
    """Batch optimization endpoint for multiple code samples"""
    try:
        data = request.get_json()
        if not data or 'codes' not in data:
            return jsonify({'error': 'Missing required parameter: codes (list)'}), 400
        
        codes = data['codes']
        if len(codes) > 10:  # Limit batch size
            return jsonify({'error': 'Batch size limited to 10 items'}), 400
        
        # Process in parallel
        def optimize_single(code_data):
            try:
                opt_request = OptimizationRequest(
                    code=code_data['code'],
                    optimization_level=OptimizationLevel(code_data.get('level', 'medium')),
                    use_ml=data.get('use_ml', True),
                    use_rule_based=data.get('use_rule_based', True)
                )
                return hybrid_optimizer.optimize(opt_request).to_dict()
            except Exception as e:
                return {'error': str(e), 'code': code_data['code'][:100]}
        
        # Submit to thread pool
        futures = [thread_pool.submit(optimize_single, code_data) for code_data in codes]
        results = [future.result() for future in futures]
        
        return jsonify({
            'results': results,
            'total_processed': len(results),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Batch optimization error: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/models', methods=['GET'])
def get_models_info():
    """Get information about available models"""
    try:
        info = {
            'available_models': [],
            'model_status': {},
            'training_info': {}
        }
        
        if model_trainer:
            model_info = model_trainer.get_model_info()
            info.update(model_info)
        
        # Add component availability
        info['components'] = {
            'ml_optimizer': ml_optimizer is not None,
            'complexity_predictor': complexity_predictor is not None,
            'explainability_engine': explainability_engine is not None,
            'rule_based_optimizer': rule_based_optimizer is not None
        }
        
        return jsonify(info)
        
    except Exception as e:
        logger.error(f"Models info error: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/train', methods=['POST'])
def train_models():
    """Train or retrain models (admin endpoint)"""
    try:
        data = request.get_json() or {}
        num_samples = data.get('num_samples', 1000)
        
        if not model_trainer:
            return jsonify({'error': 'Model trainer not available'}), 503
        
        # Start training in background
        def train_async():
            try:
                results = model_trainer.train_all_models(num_samples)
                logger.info(f"Model training completed: {results}")
                return results
            except Exception as e:
                logger.error(f"Model training failed: {e}")
                return {'error': str(e)}
        
        # Submit training job
        future = thread_pool.submit(train_async)
        
        return jsonify({
            'message': 'Model training started',
            'num_samples': num_samples,
            'status': 'training_started'
        })
        
    except Exception as e:
        logger.error(f"Training error: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Enhanced EFFICODE API on {host}:{port}")
    app.run(host=host, port=port, debug=debug)