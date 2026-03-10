# CropSense Frontend Documentation

## Overview

React-based web application for CropSense crop recommendation and planning system.

- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **State**: React Context API
- **Routing**: React Router v6

---

## Quick Start

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
# Opens http://localhost:5173

# 4. Build for production
npm run build
```

---

## Project Structure

```
frontend/
├── index.html               # Entry HTML
├── package.json             # Dependencies
├── vite.config.js           # Vite configuration
├── tailwind.config.js       # Tailwind CSS config
├── postcss.config.js        # PostCSS config
│
├── public/                  # Static assets
│
└── src/
    ├── main.jsx             # App entry point
    ├── App.jsx              # Root component with routing
    ├── App.css              # Global styles
    ├── index.css            # Tailwind imports
    │
    ├── assets/
    │   └── images/          # Image assets
    │
    ├── components/
    │   ├── common/          # Shared UI components
    │   ├── cycle/           # Cycle-related components
    │   ├── layout/
    │   │   ├── Header.jsx
    │   │   ├── Sidebar.jsx
    │   │   └── ProtectedRoute.jsx
    │   └── nutrients/       # Nutrient display components
    │
    ├── context/
    │   └── AuthContext.jsx  # Authentication state
    │
    ├── hooks/
    │   ├── useAuth.js       # Auth hook
    │   ├── useCycle.js      # Cycle management hook
    │   └── useNutrients.js  # Nutrient data hook
    │
    ├── pages/
    │   ├── auth/
    │   │   ├── Welcome.jsx  # Landing page
    │   │   ├── Login.jsx    # Login form
    │   │   └── Signup.jsx   # Registration form
    │   ├── cycle/
    │   │   ├── NewCycle.jsx     # Start new cycle
    │   │   ├── ActiveCycle.jsx  # View active cycle
    │   │   └── CycleHistory.jsx # Past cycles
    │   ├── dashboard/
    │   │   └── Dashboard.jsx    # Main dashboard
    │   ├── profile/
    │   │   └── Profile.jsx      # User profile
    │   └── recommendation/
    │       └── QuickRecommendation.jsx
    │
    ├── services/
    │   └── api.js           # API client (axios)
    │
    └── utils/
        └── constants.js     # App constants
```

---

## Routes

| Path | Page | Auth Required |
|------|------|---------------|
| `/welcome` | Landing page | No |
| `/login` | Login form | No |
| `/signup` | Registration | No |
| `/dashboard` | Main dashboard | Yes |
| `/cycle/new` | Start new cycle | Yes |
| `/cycle/active` | Active cycle | Yes |
| `/cycle/history` | Cycle history | Yes |
| `/profile` | User profile | Yes |

---

## Environment Variables (.env)

```env
VITE_API_URL=http://localhost:5000
```

---

## API Integration

The frontend connects to the backend API at `http://localhost:5000`.

### Authentication Flow
1. User registers/logs in
2. JWT token stored in localStorage
3. Token included in all API requests via `Authorization: Bearer <token>`
4. Auto-logout on 401 responses

### API Service (`src/services/api.js`)
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
});

// Auto-attach auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server (port 5173) |
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |

---

## Key Components

### AuthContext
Manages user authentication state globally.

```jsx
const { user, login, logout, isAuthenticated } = useAuth();
```

### ProtectedRoute
Wrapper for routes that require authentication.

```jsx
<ProtectedRoute>
  <Dashboard />
</ProtectedRoute>
```

### Hooks
- `useAuth()` - Authentication state and methods
- `useCycle()` - Cycle CRUD operations
- `useNutrients()` - Nutrient data fetching

---

## Styling

Uses Tailwind CSS for utility-first styling.

```jsx
<button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded">
  Start Cycle
</button>
```

---

## Build & Deploy

```bash
# Build for production
npm run build

# Output in dist/ folder
# Deploy to any static hosting (Vercel, Netlify, etc.)
```

---

## Dependencies

Key packages in `package.json`:
- `react` - UI library
- `react-router-dom` - Routing
- `axios` - HTTP client
- `tailwindcss` - CSS framework
- `vite` - Build tool
- `@vitejs/plugin-react` - React plugin for Vite
