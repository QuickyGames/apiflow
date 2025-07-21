# APIFlow - Running Instructions

## Prerequisites

- Docker and Docker Compose installed
- Node.js 18+ (for local frontend development)
- Python 3.10+ (for local backend development)

## Quick Start with Docker

1. Clone the repository and navigate to the project directory:
```bash
cd apiflow
```

2. Copy the environment file:
```bash
cp .env.example .env
```

3. Build and start all services:
```bash
docker-compose up --build
```

This will start:
- PostgreSQL database on port 5432
- API server on http://localhost:8000
- Worker service (background job processor)
- Frontend on http://localhost:3000

4. The admin user will be created automatically with:
   - Username: `admin` (or as set in ADMIN_LOGIN env var)
   - Password: `admin` (or as set in ADMIN_PASSWORD env var)

5. On first run, check the API logs for the admin API token:
```bash
docker-compose logs api | grep "Admin API token"
```

The output will show something like:
```
api_1  | Admin API token: YOUR_TOKEN_HERE
```

## Accessing the Application

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Database**: PostgreSQL on localhost:5432

## Using the Application

### 1. Login with API Token
1. Go to http://localhost:3000
2. You'll be redirected to the login page
3. Enter the admin API token from the logs
4. Click "Sign in"

### 2. Create a Connector
Connectors define API endpoints:
1. Go to Connectors page
2. Click "Create Connector"
3. Example for Replicate:
   ```json
   Name: Replicate
   Base URL: https://api.replicate.com/v1
   Method: POST
   Headers: {
     "Authorization": "Bearer $REPLICATE_API_TOKEN",
     "Content-Type": "application/json"
   }
   ```

### 3. Create a Node
Nodes are reusable components that use connectors:
1. Go to Nodes page
2. Click "Create Node"
3. Select a connector
4. Define input/output schemas

### 4. Create a Workflow
Workflows chain nodes together:
1. Go to Workflows page
2. Click "Create Workflow"
3. Define the workflow JSON structure

### 5. Run a Workflow
1. From the Workflows page, click "Run" on any workflow
2. Provide input data
3. Monitor execution in the Jobs page

## Development Mode

### Backend Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
cd backend
uvicorn api:app --reload --port 8000

# Run worker in another terminal
python worker.py
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Key environment variables in `.env`:

- `PUBLIC_API_URL`: Frontend API URL (default: http://localhost:8000)
- `ADMIN_LOGIN`: Admin username (default: admin)
- `ADMIN_PASSWORD`: Admin password (default: admin)
- `DATABASE_URL`: PostgreSQL connection string
- `REPLICATE_API_TOKEN`: (Optional) For Replicate API integration

## Troubleshooting

### Database Connection Issues
```bash
# Reset the database
docker-compose down -v
docker-compose up --build
```

### Port Conflicts
If ports are already in use, modify `docker-compose.yaml`:
- Change `8000:8000` to `8001:8000` for API
- Change `3000:3000` to `3001:3000` for frontend
- Update `PUBLIC_API_URL` in `.env` accordingly

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f frontend
```

## API Examples

### Get Connectors
```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
  http://localhost:8000/api/v1/connectors
```

### Create a Node
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Node",
    "description": "A test node",
    "connector_id": 1,
    "input": [],
    "output": []
  }' \
  http://localhost:8000/api/v1/nodes
```

### Run a Workflow
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"input": {}}' \
  http://localhost:8000/api/v1/workflow/1/run
```

## Architecture

- **API Server**: FastAPI application handling HTTP requests
- **Worker**: Background service processing workflow jobs
- **Database**: PostgreSQL storing all application data
- **Frontend**: SvelteKit application for the UI

The worker polls for pending jobs and executes workflows asynchronously.
