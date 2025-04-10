# Efficode-ACRR: AI Code Review and Refactoring Tool

A comprehensive tool for automated code review and refactoring using AI and rule-based techniques.

## Project Structure

```
.
├── backend/           # Python backend server
│   ├── src/          # Core backend logic
│   │   └── rule_based.py  # Rule-based optimization engine
│   ├── app.py        # Main backend application
│   └── interactive_optimizer.py  # Interactive command-line optimizer
├── frontend/         # React frontend application
│   ├── src/          # React source code
│   └── public/       # Static assets
└── requirements.txt  # Python dependencies
```

## Setup and Installation

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
python backend/app.py
```

4. Use the interactive optimizer:
```bash
python backend/interactive_optimizer.py
```

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The frontend will be available at http://localhost:3000

## Features

### Rule-Based Optimizer

The core of Efficode-ACRR is the rule-based optimizer that can detect and optimize various code patterns:

- **Algorithm Detection**: Identifies and optimizes common algorithms (sorting, searching)
- **Loop Optimization**: Improves inefficient loops and transforms them into more efficient code
- **Constant Folding**: Pre-computes constant expressions
- **Dead Code Elimination**: Removes unreachable and unused code
- **String Optimization**: Enhances string concatenation operations
- **Repeated Computation Elimination**: Avoids redundant calculations

### Interactive Optimizer

The interactive command-line tool allows you to:

1. Choose optimization types:
   - Rule-based optimizations
   - Code transformations
   - Both

2. Select algorithm domains:
   - Sorting
   - Searching
   - Graph algorithms
   - Dynamic programming
   - String manipulation

3. Input your code and receive optimized versions with:
   - Complexity analysis
   - Detailed optimization explanations
   - Performance improvements

## Development

### Backend Development

- The backend is built with Flask and provides RESTful APIs
- Core optimization logic is in `backend/src/rule_based.py`
- Interactive CLI is in `backend/interactive_optimizer.py`
- Main application entry point is `backend/app.py`

### Frontend Development

- Built with React and TypeScript
- Uses Monaco Editor for code editing
- Real-time communication with backend APIs

## Testing

### Backend Tests

Run backend tests with:
```bash
pytest backend/
```

### Frontend Tests

Run frontend tests with:
```bash
cd frontend
npm test
```

## Deployment

1. Build the frontend:
```bash
cd frontend
npm run build
```

2. Start the production server:
```bash
python backend/app.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
