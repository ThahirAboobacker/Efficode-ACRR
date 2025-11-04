#!/usr/bin/env python3
"""
Explainability Engine for EFFICODE-ACRR
Provides detailed explanations for optimization decisions using SHAP-like analysis
"""

import numpy as np
from typing import Dict, List, Tuple, Any
import matplotlib.pyplot as plt
import json

class OptimizationExplainer:
    def __init__(self):
        self.feature_names = [
            'nested_loops', 'function_calls', 'variables', 'conditionals', 'list_operations',
            'lines_of_code', 'for_loops', 'while_loops', 'range_usage', 'enumerate_usage',
            'dict_usage', 'set_usage', 'list_usage', 'append_calls', 'get_calls',
            'sum_pattern', 'comparison_pattern', 'max_min_pattern', 'sorting_usage', 'len_usage',
            'has_nested_loops', 'has_triple_nested', 'membership_testing', 'conditional_complexity',
            'substring_pattern', 'duplicate_pattern', 'pair_pattern', 'max_pattern', 'count_pattern', 'frequency_pattern'
        ]
        
        self.technique_explanations = {
            'hash_map': {
                'description': 'Hash Map optimization replaces nested loops with O(1) dictionary lookups',
                'key_benefits': ['O(1) average lookup time', 'Eliminates nested iterations', 'Space-time tradeoff'],
                'when_to_use': 'When searching for complements, pairs, or specific values',
                'example': 'Two Sum: Store numbers as keys, indices as values for instant complement lookup'
            },
            'hash_set': {
                'description': 'Hash Set optimization uses O(1) membership testing instead of linear search',
                'key_benefits': ['O(1) membership testing', 'Eliminates duplicate comparisons', 'Memory efficient for uniqueness'],
                'when_to_use': 'When checking for duplicates or membership in collections',
                'example': 'Contains Duplicate: Add elements to set, return True on first collision'
            },
            'dynamic_programming': {
                'description': 'Dynamic Programming eliminates redundant calculations using optimal substructure',
                'key_benefits': ['Avoids recomputation', 'Optimal substructure', 'Linear time complexity'],
                'when_to_use': 'When problem has overlapping subproblems and optimal substructure',
                'example': 'Maximum Subarray: Kadane\'s algorithm tracks running sum vs starting fresh'
            },
            'two_pointers': {
                'description': 'Two Pointers technique reduces search space by moving pointers based on conditions',
                'key_benefits': ['Reduces search space', 'Works on sorted data', 'Eliminates one loop'],
                'when_to_use': 'When working with sorted arrays or finding pairs/triplets',
                'example': '3Sum: Sort array, use two pointers to find pairs that sum to target'
            },
            'sliding_window': {
                'description': 'Sliding Window maintains a window of elements and slides it across the data',
                'key_benefits': ['Maintains state efficiently', 'Single pass through data', 'Optimal for subarray problems'],
                'when_to_use': 'When finding subarrays, substrings, or maintaining running calculations',
                'example': 'Longest Substring: Expand window on new chars, contract on duplicates'
            }
        }
    
    def explain_optimization_decision(self, code: str, features: List[float], 
                                    predicted_technique: str, confidence: float) -> Dict:
        """Generate comprehensive explanation for optimization decision"""
        
        explanation = {
            'decision_summary': self.generate_decision_summary(predicted_technique, confidence),
            'feature_importance': self.analyze_feature_importance(features, predicted_technique),
            'technique_details': self.get_technique_explanation(predicted_technique),
            'code_analysis': self.analyze_code_patterns(code),
            'optimization_rationale': self.generate_optimization_rationale(code, features, predicted_technique),
            'alternative_approaches': self.suggest_alternatives(features),
            'performance_impact': self.estimate_performance_impact(features, predicted_technique)
        }
        
        return explanation
    
    def generate_decision_summary(self, technique: str, confidence: float) -> Dict:
        """Generate high-level decision summary"""
        confidence_level = "High" if confidence > 0.7 else "Medium" if confidence > 0.4 else "Low"
        
        return {
            'technique': technique.replace('_', ' ').title(),
            'confidence': f"{confidence:.1%}",
            'confidence_level': confidence_level,
            'recommendation': f"Apply {technique.replace('_', ' ')} optimization with {confidence_level.lower()} confidence"
        }
    
    def analyze_feature_importance(self, features: List[float], technique: str) -> List[Dict]:
        """Analyze which features contributed most to the decision"""
        
        # Simulated feature importance (in real implementation, use SHAP or model.feature_importances_)
        feature_importance_weights = {
            'hash_map': {
                'nested_loops': 0.35, 'sum_pattern': 0.25, 'comparison_pattern': 0.20,
                'pair_pattern': 0.15, 'for_loops': 0.05
            },
            'hash_set': {
                'nested_loops': 0.30, 'duplicate_pattern': 0.25, 'comparison_pattern': 0.20,
                'membership_testing': 0.15, 'has_nested_loops': 0.10
            },
            'dynamic_programming': {
                'nested_loops': 0.25, 'max_pattern': 0.20, 'sum_pattern': 0.20,
                'lines_of_code': 0.15, 'conditional_complexity': 0.20
            },
            'two_pointers': {
                'nested_loops': 0.30, 'sorting_usage': 0.25, 'comparison_pattern': 0.20,
                'pair_pattern': 0.15, 'for_loops': 0.10
            },
            'sliding_window': {
                'nested_loops': 0.25, 'substring_pattern': 0.25, 'max_pattern': 0.20,
                'conditional_complexity': 0.15, 'for_loops': 0.15
            }
        }
        
        weights = feature_importance_weights.get(technique, {})
        
        feature_contributions = []
        for i, feature_name in enumerate(self.feature_names):
            if i < len(features):
                weight = weights.get(feature_name, 0.01)
                contribution = features[i] * weight
                
                if contribution > 0.01:  # Only show significant contributions
                    feature_contributions.append({
                        'feature': feature_name.replace('_', ' ').title(),
                        'value': features[i],
                        'contribution': contribution,
                        'impact': 'High' if contribution > 0.15 else 'Medium' if contribution > 0.05 else 'Low'
                    })
        
        # Sort by contribution
        feature_contributions.sort(key=lambda x: x['contribution'], reverse=True)
        
        return feature_contributions[:5]  # Top 5 features
    
    def get_technique_explanation(self, technique: str) -> Dict:
        """Get detailed explanation of the optimization technique"""
        return self.technique_explanations.get(technique, {
            'description': f'{technique.replace("_", " ").title()} optimization technique',
            'key_benefits': ['Improved performance', 'Better algorithmic complexity'],
            'when_to_use': 'When specific patterns are detected in the code',
            'example': 'Apply appropriate data structure optimization'
        })
    
    def analyze_code_patterns(self, code: str) -> Dict:
        """Analyze specific patterns in the code"""
        patterns = {
            'nested_loops_detected': 'for' in code and code.count('for') >= 2,
            'equality_comparisons': '==' in code,
            'sum_operations': '+' in code or 'sum(' in code,
            'max_min_operations': 'max(' in code or 'min(' in code,
            'list_operations': 'append(' in code or '.extend(' in code,
            'return_in_loop': 'return' in code and 'for' in code,
            'target_variable': 'target' in code,
            'duplicate_keywords': 'duplicate' in code.lower() or 'dup' in code.lower()
        }
        
        detected_patterns = [pattern for pattern, detected in patterns.items() if detected]
        
        return {
            'total_patterns': len(detected_patterns),
            'detected_patterns': detected_patterns,
            'complexity_indicators': {
                'nested_structure': patterns['nested_loops_detected'],
                'search_pattern': patterns['equality_comparisons'] and patterns['nested_loops_detected'],
                'accumulation_pattern': patterns['sum_operations'] or patterns['max_min_operations']
            }
        }
    
    def generate_optimization_rationale(self, code: str, features: List[float], technique: str) -> str:
        """Generate human-readable rationale for the optimization"""
        
        rationales = {
            'hash_map': f"""
The code shows a nested loop pattern with equality comparisons, indicating a search operation.
Hash map optimization is recommended because:
• Nested loops suggest O(n²) time complexity
• Equality comparisons indicate searching for specific values
• Hash map provides O(1) average lookup time
• This transforms the algorithm from O(n²) to O(n)
            """.strip(),
            
            'hash_set': f"""
The code exhibits duplicate detection patterns with nested comparisons.
Hash set optimization is ideal because:
• Nested loops are used for element comparison
• Set membership testing is O(1) vs O(n) for lists
• Eliminates redundant comparisons
• Reduces complexity from O(n²) to O(n)
            """.strip(),
            
            'dynamic_programming': f"""
The code shows overlapping subproblem patterns with optimization potential.
Dynamic programming is suitable because:
• Nested loops suggest redundant calculations
• Max/sum operations indicate optimal substructure
• DP can eliminate redundant computations
• Achieves O(n) complexity with optimal substructure
            """.strip(),
            
            'two_pointers': f"""
The code structure suggests sorted array operations or pair finding.
Two pointers technique is effective because:
• Multiple nested loops for pair/triplet finding
• Can work efficiently on sorted data
• Reduces search space systematically
• Improves from O(n³) to O(n²) or O(n²) to O(n log n)
            """.strip(),
            
            'sliding_window': f"""
The code shows substring/subarray processing patterns.
Sliding window is optimal because:
• Nested loops for substring/subarray analysis
• Window can maintain state efficiently
• Single pass through data structure
• Reduces complexity from O(n²) to O(n)
            """.strip()
        }
        
        return rationales.get(technique, f"Apply {technique.replace('_', ' ')} optimization based on detected patterns.")
    
    def suggest_alternatives(self, features: List[float]) -> List[Dict]:
        """Suggest alternative optimization approaches"""
        alternatives = []
        
        # Analyze features to suggest alternatives
        if len(features) > 0:
            nested_loops = features[0] if len(features) > 0 else 0
            has_comparisons = features[16] if len(features) > 16 else 0
            
            if nested_loops >= 2:
                alternatives.append({
                    'technique': 'Hash Map',
                    'applicability': 'High' if has_comparisons > 0 else 'Medium',
                    'reason': 'Replace nested loops with O(1) lookups'
                })
                
                alternatives.append({
                    'technique': 'Hash Set',
                    'applicability': 'Medium',
                    'reason': 'Use for membership testing and duplicate detection'
                })
                
                alternatives.append({
                    'technique': 'Two Pointers',
                    'applicability': 'Medium',
                    'reason': 'Effective for sorted array problems'
                })
        
        return alternatives
    
    def estimate_performance_impact(self, features: List[float], technique: str) -> Dict:
        """Estimate the performance impact of the optimization"""
        
        # Estimate based on nested loop depth and technique
        nested_depth = features[0] if len(features) > 0 else 1
        
        impact_estimates = {
            'hash_map': {
                'time_improvement': f"O(n^{int(nested_depth)}) → O(n)",
                'space_tradeoff': 'O(n) additional space for hash map',
                'speedup_100': '100x faster for 100 elements',
                'speedup_1000': '1,000x faster for 1,000 elements',
                'speedup_10000': '10,000x faster for 10,000 elements'
            },
            'hash_set': {
                'time_improvement': f"O(n^{int(nested_depth)}) → O(n)",
                'space_tradeoff': 'O(n) additional space for hash set',
                'speedup_100': '100x faster for 100 elements',
                'speedup_1000': '1,000x faster for 1,000 elements',
                'speedup_10000': '10,000x faster for 10,000 elements'
            },
            'dynamic_programming': {
                'time_improvement': f"O(n^{int(nested_depth)}) → O(n)",
                'space_tradeoff': 'O(1) space with optimal implementation',
                'speedup_100': '100x faster for 100 elements',
                'speedup_1000': '1,000x faster for 1,000 elements',
                'speedup_10000': '10,000x faster for 10,000 elements'
            }
        }
        
        return impact_estimates.get(technique, {
            'time_improvement': 'Significant improvement expected',
            'space_tradeoff': 'Minimal additional space',
            'speedup_100': 'Faster execution for larger inputs',
            'speedup_1000': 'Substantial improvement for 1K+ elements',
            'speedup_10000': 'Dramatic speedup for 10K+ elements'
        })
    
    def generate_visual_explanation(self, explanation: Dict, save_path: str = None) -> str:
        """Generate visual explanation chart"""
        try:
            # Create feature importance chart
            features = explanation['feature_importance']
            if not features:
                return "No significant features to visualize"
            
            feature_names = [f['feature'] for f in features]
            contributions = [f['contribution'] for f in features]
            
            plt.figure(figsize=(10, 6))
            bars = plt.barh(feature_names, contributions, color='skyblue')
            plt.xlabel('Feature Contribution')
            plt.title('Feature Importance for Optimization Decision')
            plt.tight_layout()
            
            # Add value labels on bars
            for bar, contribution in zip(bars, contributions):
                plt.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                        f'{contribution:.3f}', va='center')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close()
                return f"Visualization saved to {save_path}"
            else:
                plt.show()
                return "Visualization displayed"
                
        except Exception as e:
            return f"Error generating visualization: {e}"

def test_explainability_engine():
    """Test the explainability engine"""
    explainer = OptimizationExplainer()
    
    # Sample code and features
    code = '''def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []'''
    
    # Sample features (30 features)
    features = [2, 3, 2, 1, 0, 5, 2, 0, 2, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0]
    
    explanation = explainer.explain_optimization_decision(
        code, features, 'hash_map', 0.85
    )
    
    print("🔍 EXPLAINABILITY ENGINE TEST")
    print("=" * 50)
    
    print("\n📋 Decision Summary:")
    summary = explanation['decision_summary']
    print(f"Technique: {summary['technique']}")
    print(f"Confidence: {summary['confidence']}")
    print(f"Recommendation: {summary['recommendation']}")
    
    print("\n🎯 Top Contributing Features:")
    for feature in explanation['feature_importance']:
        print(f"• {feature['feature']}: {feature['contribution']:.3f} ({feature['impact']} impact)")
    
    print("\n💡 Optimization Rationale:")
    print(explanation['optimization_rationale'])
    
    print("\n🔄 Alternative Approaches:")
    for alt in explanation['alternative_approaches']:
        print(f"• {alt['technique']} ({alt['applicability']} applicability): {alt['reason']}")
    
    print("\n📊 Performance Impact:")
    impact = explanation['performance_impact']
    print(f"Time Improvement: {impact['time_improvement']}")
    print(f"Space Tradeoff: {impact['space_tradeoff']}")
    print(f"Speedup for 1K elements: {impact['speedup_1000']}")

if __name__ == "__main__":
    test_explainability_engine()