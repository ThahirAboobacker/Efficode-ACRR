# EFFICODE-ACRR

A Python code optimization tool that focuses on data structures and algorithms using rule-based systems and machine learning models.

## Project Overview

EFFICODE-ACRR is designed to:
1. Receive Python code as input
2. Optimize the code using rule-based systems
3. Apply machine learning models (CodeBERT) for advanced optimizations
4. Compare the complexities of input and output code using RandomForest
5. Generate explanations about the optimizations using Flan-T5

## Project Structure

```
EFFICODE-ACRR/
└─ backend/
   ├─ data/                      # Data directory
   │   ├── raw/                  # Raw datasets
   │   └── processed/            # Processed datasets
   │
   ├── models/                   # Trained model storage
   │   ├── codebert/
   │   ├── random_forest/
   │   └── flan_t5/
   │
   ├── src/                      # Source code
   │   ├── data_processing.py    # Dataset loading and preprocessing
   │   ├── feature_extraction.py # Code feature extraction
   │   ├── rule_based.py         # Rule-based optimization
   │   ├── model_training.py     # Training pipelines for all models
   │   ├── code_transformation.py # Code transformation utilities
   │   ├── complexity_analyzer.py # Complexity analysis and comparison
   │   ├── explanation_generator.py # Generate explanations with Flan T5
   │   ├── utils.py              # Common utilities and helpers
   │   └── main.py               # Main pipeline and API
   │
   ├── notebooks/                # Jupyter notebooks for experimentation
   │   ├── data_exploration.ipynb
   │   └── model_evaluation.ipynb
   │
   ├── tests/                    # Test cases
   │   └── test_optimizer.py
   │
├── requirements.txt             # Project dependencies
├── setup.py                     # Package setup
├── README.md                    # Project documentation
└── .gitignore                   # Git ignore file
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Efficode-ACRR.git
cd Efficode-ACRR
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

## Usage

### Running the Optimizer

```python
from backend.src.main import optimize_code

# Example code to optimize
code = """
def find_max(arr):
    max_val = arr[0]
    for i in range(1, len(arr)):
        if arr[i] > max_val:
            max_val = arr[i]
    return max_val
"""

# Optimize the code
optimized_code, explanation, complexity_comparison = optimize_code(code)

# Print results
print("Optimized Code:")
print(optimized_code)
print("\nExplanation:")
print(explanation)
print("\nComplexity Comparison:")
print(complexity_comparison)
```

## Development

### Training Models

To train the models, run:

```bash
python backend/src/model_training.py
```

### Running Tests

```bash
python -m unittest discover backend/tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

- EFFICODE-ACRR Team 