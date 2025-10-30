"""
Enhanced Validation Sandbox with Performance Profiling for EFFICODE-ACRR
Provides secure code execution, functional equivalence testing, and performance measurement
"""

import os
import sys
import time
import psutil
import logging
import tempfile
import subprocess
import threading
import resource
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from pathlib import Path
import ast
import traceback
import statistics
from contextlib import contextmanager

from data_models import ValidationStatus
from config import Config

logger = logging.getLogger('efficode.validation')

@dataclass
class ExecutionResult:
    """Result of code execution"""
    output: Any
    execution_time: float
    memory_usage: float
    cpu_usage: float
    success: bool
    error_message: Optional[str] = None
    stdout: str = ""
    stderr: str = ""

@dataclass
class PerformanceMetrics:
    """Performance metrics for code execution"""
    execution_times: List[float]
    memory_usage: List[float]
    cpu_usage: List[float]
    avg_execution_time: float
    std_execution_time: float
    avg_memory_usage: float
    peak_memory_usage: float
    improvement_percentage: float = 0.0
    statistical_significance: float = 0.0

@dataclass
class SecurityIssue:
    """Security issue detected in code"""
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None

class SecurityValidator:
    """Validates code for security issues"""
    
    def __init__(self):
        self.dangerous_imports = {
            'os': ['system', 'popen', 'spawn*', 'exec*'],
            'subprocess': ['call', 'run', 'Popen', 'check_output'],
            'eval': ['eval', 'exec', 'compile'],
            'importlib': ['import_module', '__import__'],
            'sys': ['exit', 'argv'],
            'socket': ['*'],
            'urllib': ['*'],
            'requests': ['*'],
            'http': ['*']
        }
        
        self.dangerous_functions = [
            'eval', 'exec', 'compile', '__import__',
            'open', 'file', 'input', 'raw_input'
        ]
        
        self.dangerous_attributes = [
            '__globals__', '__locals__', '__builtins__',
            '__code__', '__func__', '__self__'
        ]
    
    def validate_code_input(self, code: str) -> List[SecurityIssue]:
        """Validate code for security issues"""
        issues = []
        
        try:
            # Parse the code to AST
            tree = ast.parse(code)
            
            # Check for dangerous imports
            issues.extend(self._check_dangerous_imports(tree, code))
            
            # Check for dangerous function calls
            issues.extend(self._check_dangerous_functions(tree, code))
            
            # Check for dangerous attribute access
            issues.extend(self._check_dangerous_attributes(tree, code))
            
            # Check for eval/exec usage
            issues.extend(self._check_eval_exec(tree, code))
            
        except SyntaxError as e:
            issues.append(SecurityIssue(
                severity='medium',
                description=f'Syntax error in code: {str(e)}',
                line_number=getattr(e, 'lineno', None)
            ))
        
        return issues
    
    def _check_dangerous_imports(self, tree: ast.AST, code: str) -> List[SecurityIssue]:
        """Check for dangerous imports"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.dangerous_imports:
                        issues.append(SecurityIssue(
                            severity='high',
                            description=f'Potentially dangerous import: {alias.name}',
                            line_number=node.lineno,
                            suggestion=f'Avoid importing {alias.name} for security reasons'
                        ))
            
            elif isinstance(node, ast.ImportFrom):
                if node.module in self.dangerous_imports:
                    for alias in node.names:
                        dangerous_funcs = self.dangerous_imports[node.module]
                        if '*' in dangerous_funcs or alias.name in dangerous_funcs:
                            issues.append(SecurityIssue(
                                severity='high',
                                description=f'Dangerous import: {node.module}.{alias.name}',
                                line_number=node.lineno,
                                suggestion=f'Avoid importing {alias.name} from {node.module}'
                            ))
        
        return issues
    
    def _check_dangerous_functions(self, tree: ast.AST, code: str) -> List[SecurityIssue]:
        """Check for dangerous function calls"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None
                
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                
                if func_name in self.dangerous_functions:
                    issues.append(SecurityIssue(
                        severity='critical',
                        description=f'Dangerous function call: {func_name}',
                        line_number=node.lineno,
                        suggestion=f'Remove or replace {func_name} call'
                    ))
        
        return issues
    
    def _check_dangerous_attributes(self, tree: ast.AST, code: str) -> List[SecurityIssue]:
        """Check for dangerous attribute access"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if node.attr in self.dangerous_attributes:
                    issues.append(SecurityIssue(
                        severity='high',
                        description=f'Dangerous attribute access: {node.attr}',
                        line_number=node.lineno,
                        suggestion=f'Avoid accessing {node.attr} attribute'
                    ))
        
        return issues
    
    def _check_eval_exec(self, tree: ast.AST, code: str) -> List[SecurityIssue]:
        """Check for eval/exec usage"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        issues.append(SecurityIssue(
                            severity='critical',
                            description=f'Dynamic code execution: {node.func.id}',
                            line_number=node.lineno,
                            suggestion=f'Remove {node.func.id} call - security risk'
                        ))
        
        return issues

class PerformanceProfiler:
    """Profiles code execution performance"""
    
    def __init__(self):
        self.process = None
    
    def profile_execution_time(self, func: Callable, *args, **kwargs) -> Tuple[Any, float]:
        """Profile execution time of a function"""
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            return result, end_time - start_time
        except Exception as e:
            end_time = time.perf_counter()
            raise e
    
    def profile_memory_usage(self, func: Callable, *args, **kwargs) -> Tuple[Any, float, float]:
        """Profile memory usage of a function"""
        process = psutil.Process()
        
        # Get initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            result = func(*args, **kwargs)
            
            # Get peak memory
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = peak_memory - initial_memory
            
            return result, memory_used, peak_memory
        except Exception as e:
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = peak_memory - initial_memory
            raise e
    
    def profile_comprehensive(self, func: Callable, *args, **kwargs) -> ExecutionResult:
        """Comprehensive profiling including time, memory, and CPU"""
        process = psutil.Process()
        
        # Initial measurements
        initial_memory = process.memory_info().rss / 1024 / 1024
        initial_cpu_time = process.cpu_times()
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            success = True
            error_message = None
        except Exception as e:
            result = None
            success = False
            error_message = str(e)
        
        # Final measurements
        end_time = time.perf_counter()
        final_memory = process.memory_info().rss / 1024 / 1024
        final_cpu_time = process.cpu_times()
        
        execution_time = end_time - start_time
        memory_usage = final_memory - initial_memory
        cpu_usage = (final_cpu_time.user - initial_cpu_time.user) + (final_cpu_time.system - initial_cpu_time.system)
        
        return ExecutionResult(
            output=result,
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            success=success,
            error_message=error_message
        )

class ValidationSandbox:
    """Enhanced validation sandbox with security and performance profiling"""
    
    def __init__(self, container_runtime: str = 'process'):
        self.container_runtime = container_runtime
        self.security_validator = SecurityValidator()
        self.profiler = PerformanceProfiler()
        self.timeout = Config.VALIDATION_CONFIG['sandbox_timeout']
        self.max_memory = Config.VALIDATION_CONFIG['max_memory_mb']
    
    def execute_code_safely(self, code: str, test_inputs: List[Any] = None, 
                          globals_dict: Dict[str, Any] = None) -> ExecutionResult:
        """Execute code safely with resource limits"""
        
        # Security validation
        security_issues = self.security_validator.validate_code_input(code)
        critical_issues = [issue for issue in security_issues if issue.severity == 'critical']
        
        if critical_issues:
            return ExecutionResult(
                output=None,
                execution_time=0.0,
                memory_usage=0.0,
                cpu_usage=0.0,
                success=False,
                error_message=f"Security violation: {critical_issues[0].description}"
            )
        
        # Set up execution environment
        if globals_dict is None:
            globals_dict = {
                '__builtins__': {
                    'len': len, 'range': range, 'enumerate': enumerate,
                    'sum': sum, 'max': max, 'min': min, 'abs': abs,
                    'int': int, 'float': float, 'str': str, 'bool': bool,
                    'list': list, 'dict': dict, 'set': set, 'tuple': tuple,
                    'print': print  # Allow print for debugging
                }
            }
        
        # Execute with resource limits
        def execute_with_limits():
            try:
                # Set memory limit (Unix only)
                if hasattr(resource, 'RLIMIT_AS'):
                    resource.setrlimit(resource.RLIMIT_AS, (self.max_memory * 1024 * 1024, -1))
                
                # Compile and execute code
                compiled_code = compile(code, '<sandbox>', 'exec')
                local_vars = {}
                exec(compiled_code, globals_dict, local_vars)
                
                # If test inputs provided, try to call the main function
                if test_inputs and local_vars:
                    # Find the first function defined
                    for name, obj in local_vars.items():
                        if callable(obj) and not name.startswith('_'):
                            try:
                                result = obj(*test_inputs)
                                return result
                            except Exception as e:
                                return f"Function execution error: {str(e)}"
                
                return local_vars
                
            except Exception as e:
                return f"Execution error: {str(e)}"
        
        # Profile the execution
        try:
            execution_result = self.profiler.profile_comprehensive(execute_with_limits)
            return execution_result
        except Exception as e:
            return ExecutionResult(
                output=None,
                execution_time=0.0,
                memory_usage=0.0,
                cpu_usage=0.0,
                success=False,
                error_message=f"Sandbox error: {str(e)}"
            )
    
    def compare_outputs(self, original_result: ExecutionResult, 
                       optimized_result: ExecutionResult) -> bool:
        """Compare outputs for functional equivalence"""
        
        if not original_result.success or not optimized_result.success:
            return False
        
        try:
            # Compare outputs
            return self._deep_compare(original_result.output, optimized_result.output)
        except Exception as e:
            logger.error(f"Error comparing outputs: {e}")
            return False
    
    def _deep_compare(self, obj1: Any, obj2: Any) -> bool:
        """Deep comparison of two objects"""
        if type(obj1) != type(obj2):
            return False
        
        if isinstance(obj1, (list, tuple)):
            if len(obj1) != len(obj2):
                return False
            return all(self._deep_compare(a, b) for a, b in zip(obj1, obj2))
        
        elif isinstance(obj1, dict):
            if set(obj1.keys()) != set(obj2.keys()):
                return False
            return all(self._deep_compare(obj1[k], obj2[k]) for k in obj1.keys())
        
        elif isinstance(obj1, float):
            # Handle floating point comparison with tolerance
            return abs(obj1 - obj2) < 1e-9
        
        else:
            return obj1 == obj2
    
    def measure_performance(self, code: str, test_inputs: List[List[Any]] = None, 
                          num_runs: int = 5) -> PerformanceMetrics:
        """Measure performance with multiple runs for statistical significance"""
        
        execution_times = []
        memory_usages = []
        cpu_usages = []
        
        for i in range(num_runs):
            # Use different test inputs if available
            current_inputs = test_inputs[i % len(test_inputs)] if test_inputs else None
            
            result = self.execute_code_safely(code, current_inputs)
            
            if result.success:
                execution_times.append(result.execution_time)
                memory_usages.append(result.memory_usage)
                cpu_usages.append(result.cpu_usage)
            else:
                logger.warning(f"Run {i+1} failed: {result.error_message}")
        
        if not execution_times:
            return PerformanceMetrics(
                execution_times=[],
                memory_usage=[],
                cpu_usage=[],
                avg_execution_time=0.0,
                std_execution_time=0.0,
                avg_memory_usage=0.0,
                peak_memory_usage=0.0
            )
        
        return PerformanceMetrics(
            execution_times=execution_times,
            memory_usage=memory_usages,
            cpu_usage=cpu_usages,
            avg_execution_time=statistics.mean(execution_times),
            std_execution_time=statistics.stdev(execution_times) if len(execution_times) > 1 else 0.0,
            avg_memory_usage=statistics.mean(memory_usages),
            peak_memory_usage=max(memory_usages)
        )
    
    def compare_performance(self, original_code: str, optimized_code: str,
                          test_inputs: List[List[Any]] = None, 
                          num_runs: int = 5) -> Tuple[PerformanceMetrics, PerformanceMetrics, Dict[str, Any]]:
        """Compare performance between original and optimized code"""
        
        logger.info("Measuring original code performance...")
        original_metrics = self.measure_performance(original_code, test_inputs, num_runs)
        
        logger.info("Measuring optimized code performance...")
        optimized_metrics = self.measure_performance(optimized_code, test_inputs, num_runs)
        
        # Calculate improvement statistics
        comparison = self._calculate_improvement_statistics(original_metrics, optimized_metrics)
        
        return original_metrics, optimized_metrics, comparison
    
    def _calculate_improvement_statistics(self, original: PerformanceMetrics, 
                                        optimized: PerformanceMetrics) -> Dict[str, Any]:
        """Calculate improvement statistics and statistical significance"""
        
        if not original.execution_times or not optimized.execution_times:
            return {'error': 'Insufficient data for comparison'}
        
        # Calculate percentage improvements
        time_improvement = ((original.avg_execution_time - optimized.avg_execution_time) / 
                           original.avg_execution_time * 100) if original.avg_execution_time > 0 else 0
        
        memory_improvement = ((original.avg_memory_usage - optimized.avg_memory_usage) / 
                             original.avg_memory_usage * 100) if original.avg_memory_usage > 0 else 0
        
        # Statistical significance (simplified t-test)
        statistical_significance = self._simple_t_test(
            original.execution_times, optimized.execution_times
        )
        
        return {
            'time_improvement_percent': time_improvement,
            'memory_improvement_percent': memory_improvement,
            'statistical_significance': statistical_significance,
            'original_avg_time': original.avg_execution_time,
            'optimized_avg_time': optimized.avg_execution_time,
            'original_std_time': original.std_execution_time,
            'optimized_std_time': optimized.std_execution_time,
            'confidence_level': 'high' if statistical_significance < 0.05 else 'low'
        }
    
    def _simple_t_test(self, sample1: List[float], sample2: List[float]) -> float:
        """Simple t-test for statistical significance"""
        try:
            if len(sample1) < 2 or len(sample2) < 2:
                return 1.0  # No significance
            
            mean1, mean2 = statistics.mean(sample1), statistics.mean(sample2)
            std1, std2 = statistics.stdev(sample1), statistics.stdev(sample2)
            n1, n2 = len(sample1), len(sample2)
            
            # Pooled standard error
            pooled_se = ((std1**2 / n1) + (std2**2 / n2)) ** 0.5
            
            if pooled_se == 0:
                return 1.0
            
            # t-statistic
            t_stat = abs(mean1 - mean2) / pooled_se
            
            # Simplified p-value approximation
            # For proper implementation, use scipy.stats.ttest_ind
            if t_stat > 2.0:
                return 0.05  # Significant
            elif t_stat > 1.5:
                return 0.1   # Marginally significant
            else:
                return 0.5   # Not significant
                
        except Exception:
            return 1.0  # No significance if calculation fails
    
    def detect_security_issues(self, code: str) -> List[SecurityIssue]:
        """Detect security issues in code"""
        return self.security_validator.validate_code_input(code)
    
    def validate_optimization(self, original_code: str, optimized_code: str,
                            test_cases: List[List[Any]] = None) -> Dict[str, Any]:
        """Complete validation of an optimization"""
        
        validation_result = {
            'functional_equivalence': False,
            'performance_improvement': 0.0,
            'security_issues': [],
            'validation_status': ValidationStatus.FAILED,
            'details': {}
        }
        
        try:
            # Security check
            security_issues = self.detect_security_issues(optimized_code)
            validation_result['security_issues'] = [
                {
                    'severity': issue.severity,
                    'description': issue.description,
                    'line_number': issue.line_number
                }
                for issue in security_issues
            ]
            
            # Check for critical security issues
            critical_issues = [issue for issue in security_issues if issue.severity == 'critical']
            if critical_issues:
                validation_result['validation_status'] = ValidationStatus.FAILED
                validation_result['details']['error'] = 'Critical security issues detected'
                return validation_result
            
            # Functional equivalence testing
            if test_cases:
                equivalence_results = []
                for test_case in test_cases:
                    original_result = self.execute_code_safely(original_code, test_case)
                    optimized_result = self.execute_code_safely(optimized_code, test_case)
                    
                    equivalent = self.compare_outputs(original_result, optimized_result)
                    equivalence_results.append(equivalent)
                
                functional_equivalence = all(equivalence_results)
                validation_result['functional_equivalence'] = functional_equivalence
                validation_result['details']['equivalence_tests'] = len(equivalence_results)
                validation_result['details']['passed_tests'] = sum(equivalence_results)
            else:
                # Basic execution test
                original_result = self.execute_code_safely(original_code)
                optimized_result = self.execute_code_safely(optimized_code)
                
                functional_equivalence = (original_result.success and optimized_result.success)
                validation_result['functional_equivalence'] = functional_equivalence
            
            # Performance comparison
            if functional_equivalence:
                original_perf, optimized_perf, comparison = self.compare_performance(
                    original_code, optimized_code, test_cases
                )
                
                validation_result['performance_improvement'] = comparison.get('time_improvement_percent', 0.0)
                validation_result['details']['performance_comparison'] = comparison
                validation_result['validation_status'] = ValidationStatus.PASSED
            else:
                validation_result['validation_status'] = ValidationStatus.FAILED
                validation_result['details']['error'] = 'Functional equivalence test failed'
        
        except Exception as e:
            validation_result['validation_status'] = ValidationStatus.ERROR
            validation_result['details']['error'] = str(e)
            logger.error(f"Validation error: {e}")
        
        return validation_result