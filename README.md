# Efficode-ACRR: AI Code Review and Refactoring Tool

A comprehensive tool for automated code review and refactoring using AI techniques.

## Project Structure

```
.
├── backend/           # Python backend server
│   ├── src/          # Core backend logic
│   └── app.py        # Main backend application
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

- AI-powered code analysis and optimization
- Rule-based code refactoring
- Code complexity analysis
- Automated code review suggestions
- Real-time code transformation
- Interactive web interface

## Development

### Backend Development

- The backend is built with Flask and provides RESTful APIs
- Core logic is in the `backend/src` directory
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
