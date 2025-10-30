"""
Model Training Pipeline for EFFICODE-ACRR
Handles training of all ML models with evaluation and versioning
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

from ...data_models import TrainingExample, ModelMetrics, BaseModelTrainer
from ...config import Config
from ..models.ml_optimizer import MLOptimizer
from ..models.complexity_predictor import ComplexityPredictor
from ...dataset_manager import DatasetManager

logger = logging.getLogger('efficode.model_trainer')

class ModelTrainer(BaseModelTrainer):
    """Main model trainer for all EFFICODE models"""
    
    def __init__(self):
        self.dataset_manager = DatasetManager()
        self.models = {}
        self.training_history = []
    
    def train_all_models(self, num_samples: int = 10000) -> Dict[str, Any]:
        """Train all models in the EFFICODE system"""
        logger.info("Starting comprehensive model training pipeline...")
        
        # Generate training data
        logger.info(f"Generating {num_samples} training examples...")
        training_examples = self.dataset_manager.generate_synthetic_data(num_samples)
        
        # Split data
        train_data, val_data, test_data = self.dataset_manager.split_dataset(
            training_examples,
            Config.DATASET_CONFIG['train_split'],
            Config.DATASET_CONFIG['val_split'],
            Config.DATASET_CONFIG['test_split']
        )
        
        results = {}
        
        # Train complexity predictor
        logger.info("Training complexity predictor...")
        complexity_results = self.train_complexity_predictor(train_data, val_data, test_data)
        results['complexity_predictor'] = complexity_results
        
        # Train ML optimizer (if resources allow)
        try:
            logger.info("Training ML optimizer...")
            optimizer_results = self.train_ml_optimizer(train_data, val_data)
            results['ml_optimizer'] = optimizer_results
        except Exception as e:
            logger.warning(f"ML optimizer training failed: {e}")
            results['ml_optimizer'] = {'error': str(e)}
        
        # Save training history
        self._save_training_history(results)
        
        logger.info("Model training pipeline completed!")
        return results
    
    def train_complexity_predictor(self, train_data: List[TrainingExample], 
                                 val_data: List[TrainingExample],
                                 test_data: List[TrainingExample]) -> Dict[str, Any]:
        """Train the complexity prediction model"""
        
        # Train Random Forest model
        rf_predictor = ComplexityPredictor(model_type='random_forest')
        rf_results = rf_predictor.train_model(train_data)
        
        # Evaluate on test data
        rf_metrics = self.evaluate_complexity_model(rf_predictor, test_data)
        
        # Save model
        rf_model_path = Config.get_model_path('complexity_rf')
        rf_predictor.save_model(str(rf_model_path))
        
        # Train LightGBM model
        try:
            lgb_predictor = ComplexityPredictor(model_type='lightgbm')
            lgb_results = lgb_predictor.train_model(train_data)
            lgb_metrics = self.evaluate_complexity_model(lgb_predictor, test_data)
            
            # Save LightGBM model
            lgb_model_path = Config.get_model_path('complexity_lgb')
            lgb_predictor.save_model(str(lgb_model_path))
            
        except Exception as e:
            logger.warning(f"LightGBM training failed: {e}")
            lgb_results = {'error': str(e)}
            lgb_metrics = None
        
        # Store models
        self.models['complexity_rf'] = rf_predictor
        if 'error' not in lgb_results:
            self.models['complexity_lgb'] = lgb_predictor
        
        return {
            'random_forest': {
                'training_results': rf_results,
                'test_metrics': rf_metrics.to_dict() if rf_metrics else None,
                'model_path': str(rf_model_path)
            },
            'lightgbm': {
                'training_results': lgb_results,
                'test_metrics': lgb_metrics.to_dict() if lgb_metrics else None,
                'model_path': str(lgb_model_path) if 'error' not in lgb_results else None
            }
        }
    
    def train_ml_optimizer(self, train_data: List[TrainingExample], 
                          val_data: List[TrainingExample]) -> Dict[str, Any]:
        """Train the ML-based optimizer"""
        
        # Initialize ML optimizer
        ml_optimizer = MLOptimizer()
        
        # Load base models
        if not ml_optimizer.load_models():
            logger.warning("Could not load base models, skipping ML optimizer training")
            return {'error': 'Base models not available'}
        
        # Fine-tune models
        output_dir = Config.MODEL_CACHE_DIR / 'ml_optimizer_finetuned'
        output_dir.mkdir(exist_ok=True)
        
        try:
            ml_optimizer.fine_tune_models(train_data, str(output_dir))
            
            # Evaluate the fine-tuned model
            metrics = self.evaluate_ml_optimizer(ml_optimizer, val_data)
            
            self.models['ml_optimizer'] = ml_optimizer
            
            return {
                'fine_tuning_completed': True,
                'output_directory': str(output_dir),
                'evaluation_metrics': metrics.to_dict() if metrics else None
            }
            
        except Exception as e:
            logger.error(f"ML optimizer fine-tuning failed: {e}")
            return {'error': str(e)}
    
    def evaluate_complexity_model(self, model: ComplexityPredictor, 
                                test_data: List[TrainingExample]) -> Optional[ModelMetrics]:
        """Evaluate complexity prediction model"""
        try:
            predictions = []
            true_labels = []
            
            for example in test_data:
                prediction = model.predict_complexity(example.original_code)
                predictions.append(prediction.symbolic_complexity)
                true_labels.append(example.complexity_before)
            
            # Calculate metrics
            accuracy = accuracy_score(true_labels, predictions)
            precision, recall, f1, _ = precision_recall_fscore_support(
                true_labels, predictions, average='weighted', zero_division=0
            )
            
            # Create confusion matrix
            self._plot_confusion_matrix(true_labels, predictions, 'complexity_predictor')
            
            return ModelMetrics(
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                complexity_accuracy=accuracy
            )
            
        except Exception as e:
            logger.error(f"Error evaluating complexity model: {e}")
            return None
    
    def evaluate_ml_optimizer(self, optimizer: MLOptimizer, 
                            test_data: List[TrainingExample]) -> Optional[ModelMetrics]:
        """Evaluate ML optimizer model"""
        try:
            successful_optimizations = 0
            total_optimizations = 0
            
            for example in test_data:
                candidates = optimizer.optimize(example.original_code)
                total_optimizations += 1
                
                # Check if any candidate is different from original
                if any(c.optimized_code != example.original_code for c in candidates):
                    successful_optimizations += 1
            
            optimization_success_rate = successful_optimizations / total_optimizations if total_optimizations > 0 else 0
            
            return ModelMetrics(
                accuracy=optimization_success_rate,
                precision=optimization_success_rate,
                recall=optimization_success_rate,
                f1_score=optimization_success_rate,
                optimization_success_rate=optimization_success_rate
            )
            
        except Exception as e:
            logger.error(f"Error evaluating ML optimizer: {e}")
            return None
    
    def _plot_confusion_matrix(self, true_labels: List[str], predictions: List[str], 
                              model_name: str):
        """Plot and save confusion matrix"""
        try:
            # Get unique labels
            labels = sorted(list(set(true_labels + predictions)))
            
            # Create confusion matrix
            cm = confusion_matrix(true_labels, predictions, labels=labels)
            
            # Plot
            plt.figure(figsize=(10, 8))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                       xticklabels=labels, yticklabels=labels)
            plt.title(f'Confusion Matrix - {model_name}')
            plt.xlabel('Predicted')
            plt.ylabel('Actual')
            
            # Save plot
            plot_path = Config.LOG_DIR / f'{model_name}_confusion_matrix.png'
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Confusion matrix saved to {plot_path}")
            
        except Exception as e:
            logger.error(f"Error creating confusion matrix: {e}")
    
    def _save_training_history(self, results: Dict[str, Any]):
        """Save training history and results"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'config': {
                'dataset_config': Config.DATASET_CONFIG,
                'ml_config': Config.ML_CONFIG,
                'complexity_config': Config.COMPLEXITY_CONFIG
            }
        }
        
        self.training_history.append(history_entry)
        
        # Save to file
        history_file = Config.LOG_DIR / 'training_history.json'
        try:
            with open(history_file, 'w') as f:
                json.dump(self.training_history, f, indent=2)
            logger.info(f"Training history saved to {history_file}")
        except Exception as e:
            logger.error(f"Error saving training history: {e}")
    
    def load_trained_models(self) -> Dict[str, Any]:
        """Load all trained models"""
        loaded_models = {}
        
        # Load complexity predictors
        rf_path = Config.get_model_path('complexity_rf')
        if rf_path and rf_path.exists():
            rf_predictor = ComplexityPredictor(model_type='random_forest')
            if rf_predictor.load_model(str(rf_path)):
                loaded_models['complexity_rf'] = rf_predictor
                logger.info("Loaded Random Forest complexity predictor")
        
        lgb_path = Config.get_model_path('complexity_lgb')
        if lgb_path and lgb_path.exists():
            lgb_predictor = ComplexityPredictor(model_type='lightgbm')
            if lgb_predictor.load_model(str(lgb_path)):
                loaded_models['complexity_lgb'] = lgb_predictor
                logger.info("Loaded LightGBM complexity predictor")
        
        # Load ML optimizer
        ml_optimizer = MLOptimizer()
        if ml_optimizer.load_models():
            loaded_models['ml_optimizer'] = ml_optimizer
            logger.info("Loaded ML optimizer")
        
        self.models = loaded_models
        return loaded_models
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        info = {
            'available_models': list(self.models.keys()),
            'model_paths': {name: str(path) for name, path in Config.MODEL_PATHS.items()},
            'training_history_length': len(self.training_history)
        }
        
        # Add model-specific info
        for name, model in self.models.items():
            if hasattr(model, 'is_trained'):
                info[f'{name}_trained'] = model.is_trained
            if hasattr(model, 'model_type'):
                info[f'{name}_type'] = model.model_type
        
        return info
    
    def benchmark_models(self, test_data: List[TrainingExample]) -> Dict[str, Any]:
        """Benchmark all models on test data"""
        logger.info("Starting model benchmarking...")
        
        benchmark_results = {}
        
        # Benchmark complexity predictors
        for name, model in self.models.items():
            if isinstance(model, ComplexityPredictor):
                start_time = time.time()
                metrics = self.evaluate_complexity_model(model, test_data)
                end_time = time.time()
                
                benchmark_results[name] = {
                    'metrics': metrics.to_dict() if metrics else None,
                    'inference_time': end_time - start_time,
                    'examples_per_second': len(test_data) / (end_time - start_time)
                }
        
        # Benchmark ML optimizer
        if 'ml_optimizer' in self.models:
            start_time = time.time()
            metrics = self.evaluate_ml_optimizer(self.models['ml_optimizer'], test_data[:100])  # Limit for speed
            end_time = time.time()
            
            benchmark_results['ml_optimizer'] = {
                'metrics': metrics.to_dict() if metrics else None,
                'inference_time': end_time - start_time,
                'examples_per_second': 100 / (end_time - start_time)
            }
        
        logger.info("Model benchmarking completed")
        return benchmark_results

class HyperparameterOptimizer:
    """Hyperparameter optimization for models"""
    
    def __init__(self, trainer: ModelTrainer):
        self.trainer = trainer
    
    def optimize_complexity_predictor(self, train_data: List[TrainingExample], 
                                    val_data: List[TrainingExample]) -> Dict[str, Any]:
        """Optimize hyperparameters for complexity predictor"""
        logger.info("Starting hyperparameter optimization for complexity predictor...")
        
        # Parameter grid for Random Forest
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 15, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        best_score = 0
        best_params = {}
        results = []
        
        # Grid search (simplified)
        for n_est in param_grid['n_estimators']:
            for max_d in param_grid['max_depth']:
                try:
                    # Create and train model with these parameters
                    predictor = ComplexityPredictor(model_type='random_forest')
                    
                    # Temporarily modify config
                    original_config = Config.COMPLEXITY_CONFIG.copy()
                    Config.COMPLEXITY_CONFIG['n_estimators'] = n_est
                    Config.COMPLEXITY_CONFIG['max_depth'] = max_d
                    
                    # Train and evaluate
                    predictor.train_model(train_data)
                    metrics = self.trainer.evaluate_complexity_model(predictor, val_data)
                    
                    # Restore config
                    Config.COMPLEXITY_CONFIG = original_config
                    
                    if metrics and metrics.accuracy > best_score:
                        best_score = metrics.accuracy
                        best_params = {'n_estimators': n_est, 'max_depth': max_d}
                    
                    results.append({
                        'params': {'n_estimators': n_est, 'max_depth': max_d},
                        'score': metrics.accuracy if metrics else 0
                    })
                    
                except Exception as e:
                    logger.error(f"Error in hyperparameter optimization: {e}")
                    continue
        
        logger.info(f"Best parameters: {best_params}, Best score: {best_score}")
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'all_results': results
        }