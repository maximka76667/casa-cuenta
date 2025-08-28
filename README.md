# Casa Cuenta

A modern group expense tracking application that helps you manage shared expenses and calculate balances within groups. Built with React and FastAPI for a seamless expense splitting experience.

## Features

- **Group Management**: Create and manage expense groups with multiple members
- **Expense Tracking**: Add, edit, and delete shared expenses with automatic splitting
- **Balance Calculation**: Real-time balance calculations showing who owes what
- **User Authentication**: Secure signup and signin with Supabase
- **Responsive Design**: Modern UI built with Chakra UI and Tailwind CSS
- **Real-time Updates**: Instant updates across all group members

## Tech Stack

### Frontend
- **React 19** - Modern React with latest features
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **Chakra UI** - Component library for consistent design
- **Tailwind CSS** - Utility-first CSS framework
- **Zustand** - Lightweight state management
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls

### Backend
- **FastAPI** - Modern Python web framework
- **Supabase** - Backend-as-a-Service with PostgreSQL
- **Python-Jose** - JWT token handling
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation and serialization

## Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.8 or higher)
- **Supabase Account** - For database and authentication

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/maximka76667/casa-cuenta.git
cd casa-cuenta
```

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

Configure your `.env` file with the following variables:

```env
SUPABASE_PROJECT_ID=your_supabase_project_id
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

### 3. Frontend Setup

```bash
cd ../web

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Start the Backend Server

```bash
cd ../backend

# Start FastAPI server
uvicorn app:app --reload --port 8000
```

## Development

### Frontend Development

```bash
cd web

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting
npm run lint
```

### Backend Development

```bash
cd backend

# Start with auto-reload
uvicorn app:app --reload --port 8000

# Start without reload
uvicorn app:app --port 8000
```

## API Documentation

The backend provides a RESTful API with the following endpoints:

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Register a new user |
| POST | `/signin` | Sign in existing user |

### Groups

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/groups` | Get all groups |
| GET | `/groups/{group_id}` | Get specific group |
| POST | `/groups` | Create new group |
| PUT | `/groups/{group_id}` | Update group |
| DELETE | `/groups/{group_id}` | Delete group |
| GET | `/groups/{group_id}/persons` | Get group members |
| GET | `/groups/{group_id}/balances` | Get group balances |

### Expenses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/expenses` | Get all expenses |
| GET | `/expenses/{group_id}` | Get expenses for group |
| POST | `/expenses` | Create new expense |
| PUT | `/expenses/{expense_id}` | Update expense |
| DELETE | `/expenses/{expense_id}` | Delete expense |

### Persons

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/persons` | Get all persons |
| POST | `/persons` | Add new person |
| PUT | `/persons/{person_id}` | Update person |
| DELETE | `/persons/{person_id}` | Delete person |

### Members

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/members` | Get all group members |
| POST | `/members` | Add member to group |
| PUT | `/members/{member_id}` | Update member |
| DELETE | `/members/{member_id}` | Remove member |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/{user_id}/groups` | Get user's groups |

## Data Models

### Person
```typescript
{
  name: string
  user_id?: string
  group_id: string
}
```

### Expense
```typescript
{
  name: string
  amount: number
  payer_id: string
  group_id: string
  debtors: string[]  // Array of person IDs
}
```

### Group
```typescript
{
  name: string
}
```

## Usage Examples

### Creating a New Group

```bash
curl -X POST "http://localhost:8000/groups" \
  -H "Content-Type: application/json" \
  -d '{"name": "Weekend Trip"}'
```

### Adding an Expense

```bash
curl -X POST "http://localhost:8000/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dinner",
    "amount": 120.00,
    "payer_id": "person_id_1",
    "group_id": "group_id_1",
    "debtors": ["person_id_1", "person_id_2", "person_id_3"]
  }'
```

### Getting Group Balances

```bash
curl "http://localhost:8000/groups/{group_id}/balances"
```

## Project Structure

```
casa-cuenta/
├── backend/                 # FastAPI backend
│   ├── models/             # Pydantic data models
│   │   ├── auth.py
│   │   ├── expense.py
│   │   ├── group.py
│   │   └── person.py
│   ├── app.py              # Main FastAPI application
│   └── requirements.txt    # Python dependencies
├── web/                    # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── api/            # API client functions
│   │   ├── hooks/          # Custom React hooks
│   │   ├── store/          # Zustand state management
│   │   └── interfaces/     # TypeScript interfaces
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Vite configuration
└── README.md               # This file
```

## Environment Variables

### Backend (.env)
```env
SUPABASE_PROJECT_ID=your_project_id
SUPABASE_SERVICE_KEY=your_service_key
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Guidelines

- Follow TypeScript best practices for frontend development
- Use Pydantic models for all API data validation
- Write meaningful commit messages
- Test your changes before submitting PRs
- Follow the existing code style and conventions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

Built with ❤️ using React, FastAPI, and Supabase
