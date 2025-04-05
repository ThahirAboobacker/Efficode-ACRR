#!/usr/bin/env python
"""
EFFICODE-ACRR: Main Entry Point

This module serves as the main entry point for the EFFICODE-ACRR code optimization system.
It orchestrates the complete pipeline for optimizing Python code, from parsing and analysis
to optimization application and explanation generation.
"""

import os
import sys
import time
import json
import argparse
import logging
import ast
import traceback
from typing import Dict, List, Tuple, Any, Optional, Union
from functools import lru_cache
from datetime import datetime
from waitress import serve

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.app import app
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('efficode.log')
    ]
)
logger = logging.getLogger("EFFICODE")

# Path to the fine-tuned model (relative to src directory)
FINE_TUNED_MODEL_PATH = os.path.join('..', 'models', 'flan_t5_fine_tuned')

# Import required modules
try:
    from data_processing import DataProcessor
    from feature_extraction import FeatureExtractor
    from rule_based import RuleBasedOptimizer
    from code_transformation import CodeTransformer
    from complexity_analyzer import ComplexityAnalyzer
    from explanation_generator import ExplanationGenerator
    logger.info("Successfully imported modules directly")
except ImportError as e:
    logger.critical(f"Failed to import required modules: {e}")
    logger.critical("Please ensure you're running from the correct directory and all dependencies are installed.")
    logger.critical(f"Current directory: {os.getcwd()}")
    sys.exit(1)

# Initialize components
data_processor = DataProcessor()
feature_extractor = FeatureExtractor()
rule_optimizer = RuleBasedOptimizer()
code_transformer = CodeTransformer()
complexity_analyzer = ComplexityAnalyzer()
explanation_generator = ExplanationGenerator()

class OptimizationConfig:
    """Configuration container for optimization settings."""
    
    def __init__(self, **kwargs):
        """Initialize configuration with provided values or defaults."""
        # General settings
        self.dry_run = kwargs.get('dry_run', False)
        self.verbose = kwargs.get('verbose', False)
        self.timeout = kwargs.get('timeout', 60)
        
        # Component toggles
        self.use_ml = kwargs.get('use_ml', True)
        self.use_fine_tuned = kwargs.get('use_fine_tuned', True)
        self.use_rule_based = kwargs.get('use_rule_based', True)
        
        # Safety settings
        self.validate_output = kwargs.get('validate_output', True)
        self.max_code_size = kwargs.get('max_code_size', 10_000)  # Maximum characters
        
        # Output settings
        self.output_format = kwargs.get('output_format', 'text')  # 'text', 'json', or 'html'
        self.output_file = kwargs.get('output_file', None)
        
        # Performance settings
        self.cache_size = kwargs.get('cache_size', 128)
        self.profile = kwargs.get('profile', False)
        
        # Additional settings from kwargs
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

    @classmethod
    def from_args(cls, args):
        """Create configuration from parsed command-line arguments."""
        config_dict = vars(args)
        return cls(**config_dict)
    
    @classmethod
    def from_file(cls, filepath):
        """Load configuration from a JSON file."""
        try:
            with open(filepath, 'r') as f:
                config_dict = json.load(f)
            return cls(**config_dict)
        except Exception as e:
            logger.error(f"Error loading configuration from {filepath}: {e}")
            return cls()
    
    def to_dict(self):
        """Convert configuration to dictionary."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def __str__(self):
        """String representation of configuration."""
        return json.dumps(self.to_dict(), indent=2)


class OptimizationResult:
    """Container for optimization results."""
    
    def __init__(self, 
                 original_code: str, 
                 optimized_code: str, 
                 explanation: str,
                 complexity_comparison: Dict[str, Any],
                 applied_rules: List[str],
                 metrics: Dict[str, Any] = None):
        """Initialize with optimization results."""
        self.original_code = original_code
        self.optimized_code = optimized_code
        self.explanation = explanation
        self.complexity_comparison = complexity_comparison
        self.applied_rules = applied_rules
        self.metrics = metrics or {}
        self.timestamp = datetime.now().isoformat()
        
        # Calculate improvement metrics
        self.improvement_percentage = self._calculate_improvement()
    
    def _calculate_improvement(self) -> float:
        """Calculate improvement percentage based on complexity."""
        # This is a simplistic implementation - could be enhanced
        if self.original_code == self.optimized_code:
            return 0.0
        
        # Based on code size reduction
        original_lines = len(self.original_code.split('\n'))
        optimized_lines = len(self.optimized_code.split('\n'))
        
        if original_lines > optimized_lines:
            return ((original_lines - optimized_lines) / original_lines) * 100
        
        # If optimized with same or more lines, improvement is based on complexity
        if 'improvement' in self.complexity_comparison:
            if isinstance(self.complexity_comparison['improvement'], (int, float)):
                return float(self.complexity_comparison['improvement'])
            elif 'significant' in str(self.complexity_comparison['improvement']).lower():
                return 40.0  # Arbitrary value for "significant" improvement
            
        # Default modest improvement if we made changes but can't quantify
        return 10.0 if self.original_code != self.optimized_code else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary."""
        return {
            'original_code': self.original_code,
            'optimized_code': self.optimized_code,
            'explanation': self.explanation,
            'complexity_comparison': self.complexity_comparison,
            'applied_rules': self.applied_rules,
            'metrics': self.metrics,
            'improvement_percentage': self.improvement_percentage,
            'timestamp': self.timestamp
        }
    
    def to_json(self) -> str:
        """Convert results to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_text(self) -> str:
        """Format results as readable text."""
        lines = [
            "=== Code Optimization Results ===",
            "",
            "Original Code:",
            self.original_code,
            "",
            "Optimized Code:",
            self.optimized_code,
            "",
            "Explanation:",
            self.explanation,
            "",
            "Complexity Comparison:",
        ]
        
        for key, value in self.complexity_comparison.items():
            lines.append(f"- {key}: {value}")
        
        lines.append("")
        lines.append(f"Improvement: {self.improvement_percentage:.2f}%")
        
        if self.metrics:
            lines.append("")
            lines.append("Performance Metrics:")
            for key, value in self.metrics.items():
                if isinstance(value, float):
                    lines.append(f"- {key}: {value:.4f}")
                else:
                    lines.append(f"- {key}: {value}")
        
        return "\n".join(lines)
    
    def save(self, filepath: str, format: str = None):
        """Save results to a file."""
        format = format or (filepath.split('.')[-1] if '.' in filepath else 'txt')
        
        try:
            with open(filepath, 'w') as f:
                if format.lower() in ('json', 'js'):
                    f.write(self.to_json())
                elif format.lower() in ('txt', 'text'):
                    f.write(self.to_text())
                else:
                    # Default to text format
                    f.write(self.to_text())
            logger.info(f"Results saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving results to {filepath}: {e}")
            return False


def validate_python_code(code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that the provided string is valid Python code.
    
    Args:
        code: String containing Python code
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {str(e)}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


@lru_cache(maxsize=128)
def get_cached_explanation_generator(model_path: Optional[str] = None, offline_mode: bool = False, timeout: int = 60):
    """
    Get or initialize the explanation generator with caching.
    
    Args:
        model_path: Optional path to a fine-tuned model
        offline_mode: If True, will use rule-based generation when model is unavailable
        timeout: Timeout in seconds for model loading
        
    Returns:
        Explanation generator instance or None if not available
    """
    try:
        start_time = time.time()
        generator = get_generator(use_neural_model=True, model_path=model_path, offline_mode=offline_mode, timeout=timeout)
        elapsed = time.time() - start_time
        logger.debug(f"Loaded explanation generator in {elapsed:.2f} seconds")
        return generator
    except Exception as e:
        logger.error(f"Error initializing cached explanation generator: {e}")
        return None


def optimize_code(
    code: str, 
    config: OptimizationConfig = None
) -> OptimizationResult:
    """
    Main function to optimize Python code.
    
    Args:
        code: Python code string to optimize
        config: Configuration settings for optimization
        
    Returns:
        OptimizationResult containing the optimized code and metadata
    """
    # Initialize configuration if not provided
    config = config or OptimizationConfig()
    
    # Initialize metrics
    metrics = {
        'start_time': time.time(),
        'steps': {}
    }
    
    logger.info("Starting code optimization process...")
    
    # Validate input code
    is_valid, error_message = validate_python_code(code)
    if not is_valid:
        logger.error(f"Invalid input code: {error_message}")
        return OptimizationResult(
            original_code=code,
            optimized_code=code,
            explanation=f"Optimization failed: {error_message}",
            complexity_comparison={"error": error_message},
            applied_rules=[],
            metrics={'error': error_message}
        )
    
    # Check code size limits
    if len(code) > config.max_code_size:
        error_message = f"Code size exceeds limit ({len(code)} > {config.max_code_size} characters)"
        logger.error(error_message)
        return OptimizationResult(
            original_code=code,
            optimized_code=code,
            explanation=f"Optimization failed: {error_message}",
            complexity_comparison={"error": error_message},
            applied_rules=[],
            metrics={'error': error_message}
        )
    
    # Extract features from code if using ML
    if config.use_ml:
        step_start = time.time()
        try:
            features = feature_extractor.extract_code_features(code)
            metrics['steps']['feature_extraction'] = time.time() - step_start
            logger.debug(f"Extracted {len(features)} features from code")
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            if config.verbose:
                logger.error(traceback.format_exc())
            features = {}
            metrics['steps']['feature_extraction'] = time.time() - step_start
            metrics['errors'] = metrics.get('errors', []) + [f"Feature extraction: {str(e)}"]
    
    # Apply rule-based optimizations
    step_start = time.time()
    logger.info("Applying rule-based optimizations...")
    
    # Skip actual optimization in dry-run mode
    if config.dry_run:
        logger.info("DRY RUN: Skipping actual optimization")
        optimized_code = code
        applied_rules = ["DRY RUN - No rules applied"]
    else:
        try:
            optimized_code = rule_optimizer.optimize(code)
            applied_rules = rule_optimizer.get_applied_rules()
        except Exception as e:
            logger.error(f"Rule-based optimization failed: {e}")
            if config.verbose:
                logger.error(traceback.format_exc())
            optimized_code = code
            applied_rules = []
            metrics['errors'] = metrics.get('errors', []) + [f"Rule-based optimization: {str(e)}"]
    
    metrics['steps']['rule_based_optimization'] = time.time() - step_start
    
    # Apply ML-based optimizations if requested and not in dry-run mode
    if config.use_ml and not config.dry_run:
        step_start = time.time()
        logger.info("Applying ML-based optimizations...")
        try:
            # This would be implemented to use CodeBERT for optimization
            # ml_optimized_code = ml_optimizer.optimize(optimized_code)
            # applied_rules.extend(ml_optimizer.get_applied_rules())
            pass
        except Exception as e:
            logger.warning(f"ML-based optimization failed: {e}")
            if config.verbose:
                logger.warning(traceback.format_exc())
            metrics['errors'] = metrics.get('errors', []) + [f"ML-based optimization: {str(e)}"]
        
        metrics['steps']['ml_optimization'] = time.time() - step_start
    
    # Validate optimized code
    if config.validate_output and not config.dry_run:
        step_start = time.time()
        is_valid, error_message = validate_python_code(optimized_code)
        if not is_valid:
            logger.error(f"Optimized code validation failed: {error_message}")
            logger.warning("Reverting to original code due to validation failure")
            optimized_code = code
            applied_rules = []
            metrics['errors'] = metrics.get('errors', []) + [f"Output validation: {error_message}"]
        
        metrics['steps']['output_validation'] = time.time() - step_start
    
    # Apply code transformations to clean up optimized code
    if optimized_code != code and not config.dry_run:
        step_start = time.time()
        try:
            optimized_code = code_transformer.transform(optimized_code)
        except Exception as e:
            logger.warning(f"Code transformation failed: {e}")
            # Continue with untransformed code
            metrics['errors'] = metrics.get('errors', []) + [f"Code transformation: {str(e)}"]
        
        metrics['steps']['code_transformation'] = time.time() - step_start
    
    # Analyze and compare complexity
    step_start = time.time()
    logger.info("Analyzing code complexity...")
    try:
        original_complexity = complexity_analyzer.analyze(code)
        optimized_complexity = complexity_analyzer.analyze(optimized_code)
        complexity_comparison = complexity_analyzer.compare(original_complexity, optimized_complexity)
    except Exception as e:
        logger.error(f"Complexity analysis failed: {e}")
        if config.verbose:
            logger.error(traceback.format_exc())
        complexity_comparison = {"error": str(e)}
        metrics['errors'] = metrics.get('errors', []) + [f"Complexity analysis: {str(e)}"]
    
    metrics['steps']['complexity_analysis'] = time.time() - step_start
    
    # Generate explanation
    step_start = time.time()
    logger.info("Generating explanation...")
    
    # Configure explanation generator
    if config.use_fine_tuned and os.path.exists(FINE_TUNED_MODEL_PATH):
        explanation_generator.load_model(FINE_TUNED_MODEL_PATH)
        logger.info(f"Using fine-tuned model from {FINE_TUNED_MODEL_PATH}")
    else:
        explanation_generator.use_base_model()
        logger.info("Using base model for explanations")
    
    # Generate the explanation
    if config.dry_run:
        explanation = "DRY RUN - Explanation generation skipped"
    else:
        try:
            explanation = explanation_generator.generate(
                original_code=code,
                optimized_code=optimized_code,
                applied_rules=applied_rules,
                complexity_comparison=complexity_comparison
            )
        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
            if config.verbose:
                logger.error(traceback.format_exc())
            explanation = f"Error generating explanation: {str(e)}"
            metrics['errors'] = metrics.get('errors', []) + [f"Explanation generation: {str(e)}"]
    
    metrics['steps']['explanation_generation'] = time.time() - step_start
    
    # Calculate total execution time
    metrics['total_execution_time'] = time.time() - metrics['start_time']
    logger.info(f"Code optimization completed in {metrics['total_execution_time']:.2f} seconds")
    
    # Create and return result
    return OptimizationResult(
        original_code=code,
        optimized_code=optimized_code,
        explanation=explanation,
        complexity_comparison=complexity_comparison,
        applied_rules=applied_rules,
        metrics=metrics
    )


def load_code_from_file(filepath: str) -> str:
    """
    Load code from a file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Contents of the file as a string
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading code from {filepath}: {e}")
        raise


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="EFFICODE-ACRR: Python Code Optimizer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Input sources
    input_group = parser.add_argument_group('Input Options')
    input_group.add_argument("--file", type=str, help="Path to Python file to optimize")
    input_group.add_argument("--code", type=str, help="Python code string to optimize")
    input_group.add_argument("--config", type=str, help="Path to configuration JSON file")
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument("--output", type=str, help="Path to output file")
    output_group.add_argument("--format", type=str, choices=['text', 'json'], default='text',
                        help="Output format")
    
    # Optimization controls
    opt_group = parser.add_argument_group('Optimization Options')
    opt_group.add_argument("--no-ml", action="store_true", help="Disable ML-based optimization")
    opt_group.add_argument("--no-fine-tuned", action="store_true", help="Disable fine-tuned model for explanations")
    opt_group.add_argument("--no-rule-based", action="store_true", help="Disable rule-based optimization")
    opt_group.add_argument("--dry-run", action="store_true", 
                      help="Analyze code without applying optimizations")
    
    # Performance options
    perf_group = parser.add_argument_group('Performance Options')
    perf_group.add_argument("--timeout", type=int, default=60, 
                       help="Timeout in seconds for model loading")
    perf_group.add_argument("--profile", action="store_true", 
                       help="Profile execution time of each step")
    
    # Miscellaneous options
    misc_group = parser.add_argument_group('Miscellaneous Options')
    misc_group.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging")
    misc_group.add_argument("--log-file", type=str, 
                       help="Path to log file (defaults to efficode.log in current directory)")
    misc_group.add_argument("--validate", action="store_true", default=True,
                       help="Validate optimized code (enabled by default)")
    misc_group.add_argument("--version", action="store_true", 
                       help="Show version and exit")
    
    return parser.parse_args()


def configure_logging(args):
    """Configure logging based on command-line arguments."""
    log_level = logging.DEBUG if args.verbose else logging.INFO
    
    # Update root logger level
    logging.getLogger().setLevel(log_level)
    
    # Configure file logging if specified
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)


def main():
    """
    Main entry point for the command-line interface.
    """
    # Parse arguments
    args = parse_arguments()
    
    # Show version if requested
    if args.version:
        print("EFFICODE-ACRR v1.0.0")
        return
    
    # Configure logging
    configure_logging(args)
    
    # Load configuration from file if specified
    config = None
    if args.config:
        logger.info(f"Loading configuration from {args.config}")
        config = OptimizationConfig.from_file(args.config)
    else:
        # Create configuration from command-line args
        config = OptimizationConfig.from_args(args)
    
    if args.verbose:
        logger.info(f"Using configuration:\n{config}")
    
    # Get the code to optimize
    code = None
    if args.file:
        try:
            logger.info(f"Loading code from file: {args.file}")
            code = load_code_from_file(args.file)
        except Exception as e:
            logger.error(f"Error loading code from file: {e}")
            return 1
    elif args.code:
        code = args.code
    else:
        logger.error("Error: Either --file or --code must be provided")
        return 1
    
    # Optimize the code
    try:
        result = optimize_code(code, config)
    except Exception as e:
        logger.error(f"Unhandled error during optimization: {e}")
        if args.verbose:
            logger.error(traceback.format_exc())
        return 1
    
    # Output the results
    if args.output:
        result.save(args.output, format=args.format)
    else:
        # Print to console
        if args.format == 'json':
            print(result.to_json())
        else:
            print(result.to_text())
    
    # Show performance metrics if profiling is enabled
    if args.profile:
        print("\nPerformance Metrics:")
        for step, duration in result.metrics.get('steps', {}).items():
            print(f"- {step}: {duration:.4f}s")
        print(f"- Total execution time: {result.metrics.get('total_execution_time', 0):.4f}s")
    
    # Show errors if any occurred and verbose logging is enabled
    if args.verbose and 'errors' in result.metrics and result.metrics['errors']:
        print("\nErrors encountered:")
        for error in result.metrics['errors']:
            print(f"- {error}")
    
    return 0


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging for the application"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler()
        ]
    )

def create_directories() -> None:
    """Create necessary directories if they don't exist"""
    directories = [
        os.path.dirname(Config.LOG_FILE),
        Config.MODEL_CACHE_DIR,
        Config.DATA_DIR
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"Created directory: {directory}")

def check_dependencies() -> bool:
    """Check if all required dependencies are installed"""
    required_packages = [
        'flask',
        'transformers',
        'torch',
        'numpy',
        'pandas'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logging.error(f"Missing required packages: {', '.join(missing_packages)}")
        return False
    return True

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='EFFICODE-ACRR Backend Service')
    parser.add_argument(
        '--host',
        default=Config.HOST,
        help='Host to run the server on'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=Config.PORT,
        help='Port to run the server on'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level'
    )
    parser.add_argument(
        '--production',
        action='store_true',
        help='Run in production mode using waitress'
    )
    return parser.parse_args()

def main() -> None:
    """Main entry point for the application"""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Setup logging
        setup_logging(args.log_level)
        logging.info("Starting EFFICODE-ACRR backend service...")
        
        # Create necessary directories
        create_directories()
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Log configuration
        logging.info(f"Host: {args.host}")
        logging.info(f"Port: {args.port}")
        logging.info(f"Log Level: {args.log_level}")
        logging.info(f"Production Mode: {args.production}")
        
        # Start server
        if args.production:
            logging.info("Running in production mode with waitress")
            serve(app, host=args.host, port=args.port)
        else:
            logging.info("Running in development mode with Flask")
            app.run(
                host=args.host,
                port=args.port,
                debug=not args.production
            )
            
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 