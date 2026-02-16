# Scalable Real-Time Communication Platform

## Overview

This project is a distributed real-time communication system built with:

- Backend: FastAPI (ASGI, async)
- Database: PostgreSQL
- Cache & Pub/Sub: Redis
- Real-Time: WebSocket
- Voice/Video: WebRTC (signaling only)
- Reverse Proxy: Nginx
- TURN Server: Coturn
- Frontend: React (Vite + TypeScript)
- Containerization: Docker + Docker Compose

The system is designed to be horizontally scalable and production-ready.

---

# High-Level Architecture

Client (React)
      |
HTTPS / WSS
      |
Nginx (Reverse Proxy)
      |
Multiple FastAPI Instances
      |
Redis (Presence + Pub/Sub)
      |
PostgreSQL (Persistent Storage)
      |
Coturn (Media Relay)

---

# Design Principles

1. Stateless backend (no in-memory session storage)
2. Async-first architecture (ASGI)
3. Horizontal scalability
4. Clear separation of concerns
5. Production-ready Docker setup
6. Clean modular folder structure

---

# Backend Architecture

## Core Modules

app/
│
├── main.py
├── core/
│   ├── config.py
│   ├── security.py
├── db/
│   ├── session.py
│   ├── base.py
├── models/
│   ├── user.py
│   ├── conversation.py
│   ├── message.py
│   ├── call_log.py
├── schemas/
├── services/
│   ├── websocket_manager.py
│   ├── redis_service.py
│   ├── signaling_service.py
├── api/
│   ├── auth.py
│   ├── chat.py
│   ├── call.py
├── websocket/
│   ├── chat_ws.py
│   ├── call_ws.py

---

# Authentication

- JWT Access + Refresh tokens
- Password hashing using bcrypt
- Token validation inside WebSocket handshake
- Stateless authentication

---

# Real-Time Messaging Design

1. Client connects via WebSocket
2. Token verified during handshake
3. User marked online in Redis
4. Message stored in PostgreSQL
5. Redis Pub/Sub distributes event
6. Correct FastAPI instance emits to recipient

---

# WebRTC Signaling

Backend responsibilities:
- Forward offer
- Forward answer
- Forward ICE candidates
- Handle call accept/reject
- Log call metadata

Media does NOT pass through backend.

---

# Redis Responsibilities

- User presence tracking
- Distributed message broadcasting
- Scaling WebSocket connections

Example channels:
- chat:conversation:{id}
- call:signal:{user_id}
- presence:update

---

# Database Schema

Users:
- id (UUID)
- email
- password_hash
- is_active
- created_at

Conversations:
- id
- type (private/group)
- created_at

ConversationParticipants:
- id
- conversation_id
- user_id

Messages:
- id
- conversation_id
- sender_id
- content
- message_type
- status
- created_at

CallLogs:
- id
- caller_id
- receiver_id
- call_type
- duration
- status

---

# Frontend Architecture

React + Vite + TypeScript

src/
├── api/
├── components/
├── hooks/
├── store/
├── pages/

State Management:
- Zustand

Hooks:
- useWebSocket
- useWebRTC

---

# Docker Services

- backend
- frontend
- postgres
- redis
- nginx
- coturn

All services communicate via Docker internal network.

---

# Scaling Strategy

- Multiple FastAPI instances
- Redis Pub/Sub shared state
- Stateless backend
- Nginx load balancing
- Production-ready architecture

---

# Future Enhancements

- End-to-end encryption
- Kafka message queue
- Media server (SFU)
- Kubernetes deployment
- Observability (Prometheus + Grafana)
