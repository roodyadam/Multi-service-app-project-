# 🐳 Multi-Service Flask Application by Roody Adam

### Author: [@roodyadam](https://github.com/roodyadam)

This project is a **multi-container Docker application** that demonstrates how a modern web service can be built and orchestrated using **Flask**, **PostgreSQL**, and **Redis** — each running in its own isolated container and communicating through a shared Docker network.

The goal of this project was to gain hands-on experience in containerization, networking, and service orchestration with Docker Compose.

---

## 🚀 Overview

This application showcases a simple **Flask web app** that connects to a **PostgreSQL database** and uses a **Redis cache** to handle fast, in-memory operations.

It’s an end-to-end example of how a backend developer or DevOps engineer can containerize, link, and run multiple services together seamlessly using **Docker Compose**.

---

## 🧱 Project Structure

├── compose.yml # Docker Compose configuration file
├── Dockerfile.web # Build instructions for the Flask web app
├── dependencies.txt # Python dependencies
├── main.py # Flask application source code
└── (auto-created volumes for Postgres and Redis data)


---

## ⚙️ Services Breakdown

### 🖥️ `webapp`
- **Framework:** Flask (Python)
- **Role:** Handles HTTP requests and interacts with both PostgreSQL and Redis.
- **Port:** Exposed on `5003` (maps to container’s internal port `5000`).
- **Environment Variables:**
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
  - `REDIS_HOST`
- **Dockerfile:** Builds from `Dockerfile.web`, installs dependencies from `dependencies.txt`, and runs `main.py`.

### 🗄️ `database`
- **Image:** `postgres:15-alpine`
- **Role:** Provides persistent data storage for the Flask app.
- **Port:** `5432`
- **Volume:** `postgres-storage` ensures data persistence even if the container is removed.
- **Healthcheck:** Uses `pg_isready` to ensure readiness before the app connects.

### ⚡ `cache`
- **Image:** `redis:7-alpine`
- **Role:** Caching layer for fast data access and session management.
- **Port:** `6379`
- **Volume:** `redis-storage` for persistent cache data.
- **Command:** Runs Redis with append-only mode enabled for durability.
- **Healthcheck:** Uses `redis-cli ping` to confirm container health.

---

## 🧩 How the Docker Setup Works

1. **Networking:**  
   All three containers are connected via a custom bridge network (`backend-network`), enabling service-to-service communication using container names as hostnames.

2. **Dependency Ordering:**  
   The `depends_on` directive ensures the database and cache start before the Flask app.

3. **Data Persistence:**  
   Docker volumes (`postgres-storage`, `redis-storage`) are used so data remains intact between restarts.

4. **Health Checks & Restarts:**  
   Each service has a healthcheck and restart policy (`unless-stopped`), making the setup resilient to crashes or restarts.

5. **Port Mapping:**  
   - Host `5003` → Flask container `5000`
   - Host `5432` → Postgres `5432`
   - Host `6379` → Redis `6379`

---

## 🧠 Dependencies

Defined in `dependencies.txt`:

flask==3.0.0

psycopg2-binary==2.9.9

redis==5.0.1


These allow the app to serve web requests, interact with PostgreSQL, and store/retrieve data in Redis.

---

## 🧰 Setup Instructions

### 1️⃣ Clone the Repository
bash
git clone https://github.com/roodyadam/Multi-service-app-project-.git
cd Multi-service-app-project-

2️⃣ Build and Run with Docker Compose
docker compose up --build

This command:
Builds the Flask image from Dockerfile.web
Pulls Redis and PostgreSQL images
Starts all three containers and links them on the shared network

3️⃣ Access the App
Open your browser and go to:
👉 http://localhost:5003

4️⃣ Stopping the App
docker compose down

💪  Challenges & What I Overcame

🧩   1. Multi-container orchestration
Initially, connecting multiple services and ensuring they communicate properly through environment variables and Docker networks was tricky.
I learned how to correctly use depends_on, custom bridge networks, and service hostnames (database, cache) for inter-container communication.

🐘  2. Database integration
Getting Flask to connect reliably to PostgreSQL required handling connection timing issues.
By adding a healthcheck to the database, I ensured Flask only starts once the database is ready.

⚡  3. Redis caching
Setting up Redis persistence with append-only mode helped me understand caching reliability and how Docker volumes preserve data across sessions.

🧠  4. Image optimization
I used alpine-based images (Postgres and Redis) to keep containers lightweight and efficient.

🌟  Key Strengths of This Project
End-to-end environment simulation for backend apps
Production-style containerization using Dockerfile and Compose
Persistent data management with named Docker volumes
Health checks and restart policies for robustness
Modern stack integration: Flask + PostgreSQL + Redis
Reusable infrastructure — can be extended into a microservices architecture

📈  Future Improvements
Add an Nginx reverse proxy for production-style load balancing
Use environment files (.env) for secrets and configuration
Add unit tests and CI/CD pipeline integration
Deploy to a cloud provider (AWS, Render, or Railway)

👨‍💻  About the Author
Roody Adam — Full-Stack Developer & DevOps Enthusiast
GitHub: @roodyadam
“Building this project taught me how containers, networking, and databases come together to form scalable, reliable applications. It’s one of my favorite hands-on DevOps learning experiences.”
To also remove data volumes:
docker compose down -v
