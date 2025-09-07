# ChatGPT API Microservices Project

This is a microservices project that connects to the ChatGPT API and exposes a new API to clients.

## Project Overview

The project consists of several services, all built with **FastAPI**:

1. **Auth Service**  
   This service handles user-related operations such as creating new users, authentication, and issuing JWT tokens.

2. **ChatGPT Service**  
   This service connects to the ChatGPT API. It receives user prompts and JWT tokens, sends them to a RabbitMQ queue, and uses Celery to process the prompts.  
   The response contains a **task number** that the user can use to track the result of the prompt.

## Docker Setup

A `docker-compose.yml` file is included for running the project with Docker.  

> **Important:** Migrations must be performed manually for security reasons. After all containers are up and running:

1. Enter the `auth` container and run:
```bash
alembic upgrade head
