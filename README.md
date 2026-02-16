# Scalable Real-Time Communication Platform (ChatApp)

A robust, full-stack real-time chat application built with modern technologies, designed for scalability and performance. This project features real-time messaging, WebRTC signaling for audio/video calls, and a secure authentication system.

## 🚀 Features

- **Real-Time Messaging**: Instant message delivery using WebSockets.
- **Voice & Video Calls**: WebRTC signaling for peer-to-peer audio and video communication.
- **Secure Authentication**: JWT-based authentication with access and refresh tokens.
- **Scalable Architecture**: Built with a stateless backend, Redis Pub/Sub, and Nginx load balancing.
- **Modern Frontend**: Responsive UI built with React, TypeScript, and Tailwind CSS.
- **Containerized**: Fully Dockerized for easy deployment and consistent development environments.

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python) - High performance, easy to learn, fast to code, ready for production.
- **Database**: PostgreSQL - Advanced, open-source relational database.
- **ORM**: SQLAlchemy (Async) - The Python SQL toolkit and Object Relational Mapper.
- **Cache & Pub/Sub**: Redis - In-memory data structure store, used as a database, cache, and message broker.
- **WebSockets**: Native WebSocket support for real-time bi-directional communication.

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Routing**: React Router DOM

### Infrastructure
- **Reverse Proxy**: Nginx
- **Containerization**: Docker & Docker Compose
- **TURN Server**: Coturn (for WebRTC media relay)

## 📋 Prerequisites

Before getting started, ensure you have the following installed:

- **Docker** and **Docker Compose** (Recommended for easiest setup)
- **Node.js** (v18+ for local frontend development)
- **Python** (v3.11+ for local backend development)

## ⚡ Getting Started

### Option 1: Docker (Recommended)

Run the entire stack with a single command:

```bash
# Clone the repository
git clone <repository-url>
cd ChatApp

# Start the application
docker-compose up --build
```

The services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Copy `.env.example` to `.env` and update values if necessary.
   ```bash
   cp .env.example .env
   ```
   *Note: For local development without Docker, ensure you have a local PostgreSQL and Redis instance running and update `.env` to point to `localhost` instead of container names.*

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173` (default Vite port).

## 📂 Project Structure

```
ChatApp/
├── backend/                # FastAPI application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Config and security
│   │   ├── db/             # Database session and base
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemata
│   │   ├── services/       # Business logic (Redis, WebRTC)
│   │   └── websocket/      # WebSocket handlers
│   ├── alembic/            # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # React application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── hooks/          # Custom hooks (useWebSocket, useWebRTC)
│   │   ├── pages/          # Application pages
│   │   └── store/          # Zustand state management
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml      # Docker services configuration
└── ARCHITECTURE.md         # Detailed architectural documentation
```

## 📖 API Documentation

Once the backend is running, you can access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add some amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
