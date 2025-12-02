# AI Command Center

This project is a monorepo that contains both a frontend and a backend application.

## Frontend

The frontend is built using Next.js with TypeScript, Tailwind CSS, and ESLint. It is designed to provide a modern user interface for the AI Command Center.

## Backend

The backend is developed using FastAPI, providing a RESTful API for the frontend to interact with. It includes a simple "Hello General Manager" endpoint.

## Getting Started

### Prerequisites

- Node.js (for the frontend)
- Python (for the backend)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai-command-center
   ```

2. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```

3. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Mac/Linux
   pip install -r requirements.txt
   ```

### Running the Applications

- To run the frontend:
  ```bash
  cd frontend
  npm run dev
  ```

- To run the backend:
  ```bash
  cd backend
  .\venv\Scripts\activate  # On Windows
  # source venv/bin/activate  # On Mac/Linux
  uvicorn main:app --reload
  ```

## License

This project is licensed under the MIT License. See the LICENSE file for details.