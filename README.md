# EFFICODE-ACRR

Code optimization platform using CodeBERT and FLAN-T5 for intelligent code improvements and complexity analysis.

## 🚀 Features

- **Intelligent Code Optimization** using CodeBERT
- **Complexity Analysis** with RandomForest models
- **Detailed Explanations** powered by FLAN-T5
- **Real-time Visual Feedback** on optimization improvements
- **Support for Multiple Programming Patterns**

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Frontend**: React, TypeScript
- **ML Models**: 
  - CodeBERT for code optimization
  - FLAN-T5 for explanation generation
  - RandomForest for complexity analysis

## 📁 Project Structure

```
Efficode-ACRR/
├── backend/
│   ├── models/              # ML model implementations
│   ├── scripts/            # Utility scripts
│   ├── src/               # Core backend logic
│   └── tests/             # Test cases
└── frontend/
    ├── src/
    │   ├── components/    # React components
    │   ├── services/      # API services
    │   └── utils/         # Utility functions
    └── public/            # Static assets
```

## 🚀 Quick Start

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Download models
python scripts/download_models.py

# Start server
python src/app.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## 🔧 Development

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm 6+

### Environment Setup

Create `.env` file in backend directory:

```env
FLASK_ENV=development
FLASK_APP=src/app.py
MODEL_CACHE_DIR=models/cache
PORT=5000
```

### Running Tests

```bash
cd backend
python -m pytest tests/
```

## 📖 API Documentation

### Code Optimization Endpoint

```http
POST /api/optimize
Content-Type: application/json

{
    "code": "def example(): pass",
    "optimization_level": 1
}
```

Response:
```json
{
    "optimized_code": "...",
    "complexity": {
        "time": "O(n)",
        "space": "O(1)"
    },
    "explanation": "..."
}
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Team

- EFFICODE-ACRR Development Team
- ML Research Team
