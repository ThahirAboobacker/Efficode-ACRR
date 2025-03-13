from setuptools import setup, find_packages

setup(
    name="efficode-acrr",
    version="0.1.0",
    description="Python code optimizer using rule-based and ML approaches",
    author="EFFICODE-ACRR Team",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "flask>=2.3.0",
        "flask-cors>=4.0.0",
        "python-dotenv>=1.0.0",
        "matplotlib>=3.7.0",
        "astor>=0.8.0",
    ],
    python_requires=">=3.8",
) 