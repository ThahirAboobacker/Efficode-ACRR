"""
Data Processing Module for EFFICODE-ACRR

This module handles loading and preprocessing of algorithm datasets:
- Loading CSV data into pandas DataFrames
- Cleaning and standardizing code
- Extracting features from code
- Normalizing complexity labels
- Splitting data for training, validation, and testing
- Saving processed data

"""

import os
import pandas as pd
import numpy as np
import re
import ast
import json
import logging
from typing import Dict, List, Tuple, Union, Optional
import sys
from sklearn.model_selection import train_test_split
import warnings

# Local imports
from utils import count_code_elements, detect_algorithm_type, is_recursive, identify_data_structures, parse_python_code

# Configure warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_processing.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Data processor for algorithm optimization dataset"""
    
    def __init__(self, 
                 raw_dir: str = os.path.join('data', 'raw'),
                 processed_dir: str = os.path.join('data', 'processed'),
                 train_ratio: float = 0.7,
                 val_ratio: float = 0.15,
                 seed: int = 42):
        """
        Initialize the data processor
        
        Args:
            raw_dir: Directory containing raw CSV files
            processed_dir: Directory to save processed files
            train_ratio: Ratio of data for training
            val_ratio: Ratio of data for validation
            seed: Random seed for reproducibility
        """
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.seed = seed
        
        # Set random seed
        np.random.seed(seed)
        
        # Create output directory if it doesn't exist
        os.makedirs(processed_dir, exist_ok=True)
        
        # Complexity mapping for standardization
        self.complexity_mapping = {
            'O(1)': 1,                # Constant
            'O(log n)': 2,            # Logarithmic
            'O(log(n))': 2,           # Alternative logarithmic
            'O(n)': 3,                # Linear
            'O(n log n)': 4,          # Linearithmic
            'O(n*log n)': 4,          # Alternative linearithmic
            'O(n*log(n))': 4,         # Alternative linearithmic
            'O(n²)': 5,               # Quadratic
            'O(n^2)': 5,              # Alternative quadratic
            'O(n*n)': 5,              # Alternative quadratic
            'O(n³)': 6,               # Cubic
            'O(n^3)': 6,              # Alternative cubic
            'O(2^n)': 7,              # Exponential
            'O(n!)': 8                # Factorial
        }
        
        # Initialize reverse mapping
        self.complexity_reverse = {v: k for k, v in self.complexity_mapping.items()}
        
        logger.info("DataProcessor initialized")
    
    def load_dataset(self, file_path: str = None) -> pd.DataFrame:
        """
        Load and combine CSV datasets
        
        Args:
            file_path: Optional specific file to load, otherwise loads all CSVs in raw_dir
            
        Returns:
            Combined DataFrame of all datasets
        """
        combined_df = pd.DataFrame()
        
        if file_path:
            if os.path.exists(file_path):
                logger.info(f"Loading dataset from {file_path}")
                df = pd.read_csv(file_path)
                combined_df = pd.concat([combined_df, df], ignore_index=True)
            else:
                logger.error(f"File not found: {file_path}")
                raise FileNotFoundError(f"File not found: {file_path}")
        else:
            logger.info(f"Loading all datasets from {self.raw_dir}")
            files = [f for f in os.listdir(self.raw_dir) if f.endswith('.csv')]
            
            if not files:
                logger.error(f"No CSV files found in {self.raw_dir}")
                raise FileNotFoundError(f"No CSV files found in {self.raw_dir}")
            
            for file in files:
                file_path = os.path.join(self.raw_dir, file)
                logger.info(f"Loading {file}")
                df = pd.read_csv(file_path)
                combined_df = pd.concat([combined_df, df], ignore_index=True)
                logger.info(f"Loaded {len(df)} rows from {file}")
        
        # Standardize column names
        self._standardize_columns(combined_df)
        
        logger.info(f"Combined dataset: {len(combined_df)} rows, {combined_df.columns.tolist()} columns")
        return combined_df
    
    def _standardize_columns(self, df: pd.DataFrame) -> None:
        """
        Standardize column names in-place
        
        Args:
            df: DataFrame to standardize
        """
        # Column name mapping
        column_mapping = {
            'code': 'code',
            'Code': 'code',
            'time_complexity': 'time_complexity',
            'Time Complexity': 'time_complexity',
            'space_complexity': 'space_complexity', 
            'Space Complexity': 'space_complexity',
            'Algorithm Name': 'algorithm_name',
            'algorithm_name': 'algorithm_name',
            'Code Type': 'code_type',
            'code_type': 'code_type',
            'domain_tag': 'domain_tag',
            'Domain Tag': 'domain_tag',
            'Explanation': 'explanation',
            'explanation': 'explanation',
            'Alternative Algorithm': 'alternative_algorithm',
            'alternative_algorithm': 'alternative_algorithm',
            'Alternative Code': 'alternative_code',
            'alternative_code': 'alternative_code'
        }
        
        # Apply mapping to existing columns
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)
        
        # Check required columns
        required_columns = ['code', 'time_complexity', 'space_complexity']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            raise ValueError(f"Required columns not found: {missing_columns}")
    
    def preprocess_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the dataset: clean code, extract features, normalize complexity
        
        Args:
            df: DataFrame to preprocess
            
        Returns:
            Preprocessed DataFrame
        """
        logger.info("Preprocessing dataset...")
        
        # Clean code
        df['clean_code'] = df['code'].astype(str).apply(self._clean_code)
        
        # Filter out invalid code
        valid_mask = df['clean_code'].apply(self._validate_code)
        df = df[valid_mask].copy()
        logger.info(f"Valid code samples: {len(df)}")
        
        # Extract features from code
        df = self._extract_features(df)
        
        # Normalize complexity labels
        df = self._normalize_complexity(df)
        
        logger.info("Preprocessing complete")
        return df
    
    def _clean_code(self, code: str) -> str:
        """
        Clean and standardize Python code
        
        Args:
            code: Code string to clean
            
        Returns:
            Cleaned code string
        """
        if not isinstance(code, str) or not code.strip():
            return ""
        
        try:
            # Remove markdown code block markers if present
            code = re.sub(r'```python\s*', '', code)
            code = re.sub(r'```\s*$', '', code)
            
            # Remove comments
            code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
            code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
            code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
            
            # Preserve indentation while removing extra whitespace
            lines = []
            for line in code.split('\n'):
                indent = len(line) - len(line.lstrip())
                cleaned_line = line.strip()
                if cleaned_line:
                    lines.append(' ' * indent + cleaned_line)
            
            cleaned_code = '\n'.join(lines)
            
            # Remove multiple newlines
            cleaned_code = re.sub(r'\n\s*\n', '\n\n', cleaned_code)
            
            return cleaned_code.strip()
            
        except Exception as e:
            logger.warning(f"Error cleaning code: {e}")
            return code.strip()
    
    def _validate_code(self, code: str) -> bool:
        """
        Validate Python code syntax
        
        Args:
            code: Code string to validate
            
        Returns:
            True if code is valid Python, False otherwise
        """
        if not isinstance(code, str) or not code.strip():
            return False
        
        try:
            ast.parse(code)
            return True
        except:
            return False
    
    def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from code for model training
        
        Args:
            df: DataFrame with clean_code column
            
        Returns:
            DataFrame with extracted features
        """
        logger.info("Extracting code features...")
        
        # Extract code metrics
        metrics = df['clean_code'].apply(count_code_elements)
        
        # Add metrics as columns
        df['code_lines'] = metrics.apply(lambda x: x['lines'])
        df['code_chars'] = metrics.apply(lambda x: x['chars'])
        df['loop_count'] = metrics.apply(lambda x: x['loops'])
        df['loop_depth'] = metrics.apply(lambda x: x['max_loop_depth'])
        df['conditionals'] = metrics.apply(lambda x: x['conditionals'])
        df['functions'] = metrics.apply(lambda x: x['functions'])
        
        # Detect recursion
        df['is_recursive'] = df['clean_code'].apply(is_recursive)
        
        # Identify algorithm type if not already present
        if 'domain_tag' not in df.columns:
            df['domain_tag'] = df['clean_code'].apply(detect_algorithm_type)
        
        # Identify data structures
        df['data_structures'] = df['clean_code'].apply(lambda code: 
            ','.join(identify_data_structures(code)))
        
        logger.info("Feature extraction complete")
        return df
    
    def _normalize_complexity(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize and standardize complexity labels
        
        Args:
            df: DataFrame with time_complexity and space_complexity columns
            
        Returns:
            DataFrame with normalized complexity labels
        """
        logger.info("Normalizing complexity labels...")
        
        # Convert complexity to string form if it's not already
        if df['time_complexity'].dtype != 'object':
            df['time_complexity_str'] = df['time_complexity'].apply(
                lambda x: self.complexity_reverse.get(x, f"O(n^{x})") if pd.notna(x) else "")
        else:
            df['time_complexity_str'] = df['time_complexity'].apply(
                lambda x: self._standardize_complexity_notation(x) if pd.notna(x) else "")
        
        if df['space_complexity'].dtype != 'object':
            df['space_complexity_str'] = df['space_complexity'].apply(
                lambda x: self.complexity_reverse.get(x, f"O(n^{x})") if pd.notna(x) else "")
        else:
            df['space_complexity_str'] = df['space_complexity'].apply(
                lambda x: self._standardize_complexity_notation(x) if pd.notna(x) else "")
        
        # Convert to numeric form for models
        df['time_complexity_value'] = df['time_complexity_str'].apply(
            lambda x: self._complexity_to_numeric(x))
        df['space_complexity_value'] = df['space_complexity_str'].apply(
            lambda x: self._complexity_to_numeric(x))
        
        # Log distribution
        logger.info("\nComplexity distribution:")
        logger.info("\nTime complexity:")
        for val, count in df['time_complexity_value'].value_counts().sort_index().items():
            logger.info(f"  {self.complexity_reverse.get(val, f'O(n^{val})')}: {count} samples")
        
        logger.info("\nSpace complexity:")
        for val, count in df['space_complexity_value'].value_counts().sort_index().items():
            logger.info(f"  {self.complexity_reverse.get(val, f'O(n^{val})')}: {count} samples")
        
        return df
    
    def _standardize_complexity_notation(self, notation: str) -> str:
        """
        Standardize complexity notation string
        
        Args:
            notation: Complexity notation to standardize
            
        Returns:
            Standardized notation string
        """
        if not isinstance(notation, str) or not notation.strip():
            return "O(1)"  # Default to constant time if empty
            
        # Clean the notation
        notation = notation.lower().strip()
        notation = re.sub(r'\s+', '', notation)
        
        # Standardize common variations
        notation = notation.replace('o(', 'O(')
        notation = notation.replace('0(', 'O(')
        notation = notation.replace('n^2', 'n²')
        notation = notation.replace('n**2', 'n²')
        notation = notation.replace('n*n', 'n²')
        notation = notation.replace('n^3', 'n³')
        notation = notation.replace('n**3', 'n³')
        
        # Standardize logarithmic notations
        if 'log' in notation:
            notation = notation.replace('nlogn', 'n log n')
            notation = notation.replace('n*log(n)', 'n log n')
            notation = notation.replace('n*log n', 'n log n')
            notation = notation.replace('log(n)', 'log n')
        
        # Add missing big-O
        if not notation.startswith('O('):
            notation = f'O({notation})'
        
        # Ensure notation is closed
        if not notation.endswith(')'):
            notation = notation + ')'
        
        return notation
    
    def _complexity_to_numeric(self, notation: str) -> int:
        """
        Convert complexity notation to numeric value
        
        Args:
            notation: Complexity notation string
            
        Returns:
            Numeric complexity value
        """
        if not notation or not isinstance(notation, str):
            return 1  # Default to O(1)
        
        # Standardize notation first
        std_notation = self._standardize_complexity_notation(notation)
        
        # Look up in mapping
        return self.complexity_mapping.get(std_notation, 5)  # Default to O(n²) if unknown
    
    def split_train_test(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Split data into training, validation, and test sets
        
        Args:
            df: Preprocessed DataFrame
            
        Returns:
            DataFrame with 'split' column indicating train/val/test
        """
        logger.info("Splitting dataset into train/val/test...")
        
        # Create combined stratification label using time and space complexity
        df['strat_label'] = (
            df['time_complexity_value'].astype(str) + '_' + 
            df['space_complexity_value'].astype(str)
        )
        
        try:
            # First split: train vs rest
            train_idx, temp_idx = train_test_split(
                df.index,
                train_size=self.train_ratio,
                stratify=df['strat_label'],
                random_state=self.seed
            )
            
            # Second split: val vs test
            val_size = self.val_ratio / (1 - self.train_ratio)
            val_idx, test_idx = train_test_split(
                temp_idx,
                train_size=val_size,
                stratify=df.loc[temp_idx, 'strat_label'],
                random_state=self.seed
            )
            
            # Add split column
            df['split'] = 'test'
            df.loc[train_idx, 'split'] = 'train'
            df.loc[val_idx, 'split'] = 'val'
            
            # Remove stratification label
            df = df.drop('strat_label', axis=1)
            
            # Log split sizes
            logger.info(f"Train: {len(train_idx)} samples")
            logger.info(f"Val: {len(val_idx)} samples")
            logger.info(f"Test: {len(test_idx)} samples")
            
            return df
            
        except Exception as e:
            # If stratified split fails (e.g., too few samples in some classes)
            logger.warning(f"Stratified split failed: {str(e)}")
            logger.info("Using simple random split instead")
            
            # Simple random split
            df = df.sample(frac=1, random_state=self.seed).reset_index(drop=True)
            
            train_size = int(len(df) * self.train_ratio)
            val_size = int(len(df) * self.val_ratio)
            
            df['split'] = 'test'
            df.loc[:train_size-1, 'split'] = 'train'
            df.loc[train_size:train_size+val_size-1, 'split'] = 'val'
            
            # Clean up
            if 'strat_label' in df.columns:
                df = df.drop('strat_label', axis=1)
            
            # Log split sizes
            train_count = len(df[df['split'] == 'train'])
            val_count = len(df[df['split'] == 'val'])
            test_count = len(df[df['split'] == 'test'])
            
            logger.info(f"Train: {train_count} samples")
            logger.info(f"Val: {val_count} samples")
            logger.info(f"Test: {test_count} samples")
            
            return df
    
    def save_processed_data(self, df: pd.DataFrame, output_path: str = None) -> None:
        """
        Save processed dataset and metadata
        
        Args:
            df: Processed DataFrame
            output_path: Optional custom output path
        """
        if output_path is None:
            output_path = os.path.join(self.processed_dir, 'processed_dataset.csv')
        
        # Save CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Saved processed dataset to {output_path}")
        
        # Save metadata
        metadata = {
            'dataset_size': len(df),
            'columns': df.columns.tolist(),
            'complexity_distribution': {
                'time': df['time_complexity_value'].value_counts().to_dict(),
                'space': df['space_complexity_value'].value_counts().to_dict()
            },
            'splits': {
                'train': len(df[df['split'] == 'train']),
                'val': len(df[df['split'] == 'val']),
                'test': len(df[df['split'] == 'test'])
            },
            'algorithm_types': df.get('domain_tag', df.get('algorithm_name')).value_counts().to_dict()
        }
        
        metadata_path = os.path.join(os.path.dirname(output_path), 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved metadata to {metadata_path}")
    
    def process_pipeline(self) -> pd.DataFrame:
        """
        Run the full data processing pipeline
        
        Returns:
            Processed DataFrame
        """
        try:
            # Load dataset
            df = self.load_dataset()
            
            # Preprocess
            df = self.preprocess_dataset(df)
            
            # Split data
            df = self.split_train_test(df)
            
            # Save processed data
            self.save_processed_data(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error in processing pipeline: {str(e)}")
            raise

def main():
    """Main function to run the data processing pipeline"""
    try:
        # Get paths relative to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        raw_dir = os.path.join(project_root, 'data', 'raw')
        processed_dir = os.path.join(project_root, 'data', 'processed')
        
        # Initialize processor
        processor = DataProcessor(raw_dir=raw_dir, processed_dir=processed_dir)
        
        # Run pipeline
        df = processor.process_pipeline()
        
        print(f"Processing complete. Dataset shape: {df.shape}")
        return 0
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())