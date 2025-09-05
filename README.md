# LiveKit Video Calling Backend

A complete Python backend implementation for video calling applications using LiveKit with room management and user management functionality.

## Features

- **User Management**: Registration, login, JWT authentication
- **Room Management**: Create, list, join, leave, and delete rooms
- **LiveKit Integration**: Secure token generation and room management
- **RESTful API**: FastAPI-based with automatic documentation
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Security**: Password hashing, JWT tokens, request validation

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database
- LiveKit server (cloud or self-hosted)

### Installation

1. **Clone or download the project files**

2. **Run the setup script:**

   **Windows:**

   ```bash
   setup.bat
   ```

   **Linux/Mac:**

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure environment variables:**

   Update the `.env` file with your configuration:

   ```env
   # Database Configuration
   DATABASE_URL=postgresql://username:password@localhost:5432/livekit_db

   # JWT Configuration
   SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

   # LiveKit Configuration
   LIVEKIT_API_KEY=your-livekit-api-key
   LIVEKIT_API_SECRET=your-livekit-api-secret
   LIVEKIT_URL=wss://your-livekit-server-url
   ```

4. **Set up PostgreSQL database:**

   Create a database named `livekit_db` (or update the DATABASE_URL accordingly)

5. **Run the server:**

   ```bash
   python main.py
   ```

6. **Access the API documentation:**

   Open your browser to: http://localhost:8000/docs

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user information

### Room Management

- `POST /rooms` - Create a new room
- `GET /rooms` - List all active rooms
- `GET /rooms/{room_id}` - Get room details with participants
- `POST /rooms/{room_id}/join` - Join a room and get LiveKit token
- `POST /rooms/{room_id}/leave` - Leave a room
- `DELETE /rooms/{room_id}` - Delete a room (creator only)

### Health Check

- `GET /health` - Service health check

## Architecture Overview

### 1. User Management

- User registration with email/username and password
- JWT-based authentication
- Secure password hashing with bcrypt
- User session management

### 2. Room Management

- Create rooms with custom names and descriptions
- Set maximum participant limits
- Track room membership and participant counts
- Room creator permissions for deletion

### 3. LiveKit Integration

- Secure token generation for room access
- Room creation and deletion on LiveKit server
- Participant management and permissions
- Real-time participant tracking

### 4. Database Schema

**Users Table:**

- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `hashed_password`
- `is_active`
- `created_at`

**Rooms Table:**

- `id` (Primary Key)
- `name` (Unique room identifier)
- `display_name` (Human-readable name)
- `description`
- `creator_id` (Foreign Key to Users)
- `max_participants`
- `is_active`
- `created_at`

**Room Memberships Table:**

- `id` (Primary Key)
- `user_id` (Foreign Key to Users)
- `room_id` (Foreign Key to Rooms)
- `joined_at`
- `left_at`
- `is_active`

## Security Features

1. **Password Security**: Bcrypt hashing with salt
2. **JWT Tokens**: Secure authentication with expiration
3. **CORS Protection**: Configurable cross-origin requests
4. **Input Validation**: Pydantic models for request validation
5. **Authorization**: Protected endpoints with user authentication
6. **LiveKit Security**: Server-side token generation only

## Configuration

### Environment Variables

| Variable             | Description                    | Required |
| -------------------- | ------------------------------ | -------- |
| `DATABASE_URL`       | PostgreSQL connection string   | Yes      |
| `SECRET_KEY`         | JWT signing secret             | Yes      |
| `LIVEKIT_API_KEY`    | LiveKit API key                | Yes      |
| `LIVEKIT_API_SECRET` | LiveKit API secret             | Yes      |
| `LIVEKIT_URL`        | LiveKit server WebSocket URL   | Yes      |
| `HOST`               | Server host (default: 0.0.0.0) | No       |
| `PORT`               | Server port (default: 8000)    | No       |
| `DEBUG`              | Debug mode (default: True)     | No       |

### LiveKit Setup

1. **LiveKit Cloud**: Sign up at [LiveKit Cloud](https://cloud.livekit.io/)
2. **Self-hosted**: Follow the [LiveKit deployment guide](https://docs.livekit.io/home/self-hosting/deployment/)

## Usage Examples

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword"
  }'
```

### 3. Create a Room

```bash
curl -X POST "http://localhost:8000/rooms" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "meeting-room-1",
    "display_name": "Team Meeting Room",
    "description": "Daily standup meeting room",
    "max_participants": 10
  }'
```

### 4. Join a Room

```bash
curl -X POST "http://localhost:8000/rooms/1/join" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Frontend Integration

Use the token received from the `/rooms/{room_id}/join` endpoint to connect to LiveKit from your frontend:

```javascript
import { Room, connect } from "livekit-client";

// Token received from your backend
const token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...";
const wsURL = "wss://your-livekit-server-url";

const room = new Room();
await room.connect(wsURL, token);
```

## Deployment

### Production Considerations

1. **Environment**: Set `DEBUG=False` in production
2. **Database**: Use a managed PostgreSQL service
3. **SSL/TLS**: Use HTTPS for all endpoints
4. **CORS**: Configure specific allowed origins
5. **Monitoring**: Add logging and monitoring
6. **Scaling**: Consider using a load balancer for multiple instances

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**: Check your `DATABASE_URL` and ensure PostgreSQL is running
2. **LiveKit Connection Failed**: Verify your LiveKit credentials and server URL
3. **JWT Token Invalid**: Ensure your `SECRET_KEY` is set and consistent
4. **Import Errors**: Make sure all dependencies are installed in your virtual environment

### Logs

Check the console output for detailed error messages and debugging information.

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For LiveKit-specific documentation and support:

- [LiveKit Documentation](https://docs.livekit.io/)
- [LiveKit GitHub](https://github.com/livekit)
- [LiveKit Community Slack](https://livekit.io/join-slack)
