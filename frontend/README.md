# GTM Asset Generator - Frontend

Modern, responsive frontend dashboard for the GTM Asset Generator platform built with Next.js 14 and TypeScript.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom components (shadcn/ui inspired)
- **State Management**:
  - Zustand (client state)
  - TanStack Query (server state)
- **Form Handling**: React Hook Form + Zod
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP Client**: Axios

## Features

### Authentication
- User registration and login
- JWT-based authentication
- Protected routes
- Persistent session

### Dashboard
- Overview with usage statistics
- Quota tracking
- Recent jobs display
- Quick action buttons

### Image Generation
- Multi-provider support (Gemini, OpenAI, Imagen)
- Customizable design tokens
- Style presets
- Real-time job tracking

### Video Generation
- Multi-provider support (Veo, Sora)
- Cinematography controls
- Video configuration options
- Preview and download

### Jobs Management
- List all image and video jobs
- Filter and search
- Job status tracking
- Direct result access

### Analytics
- Usage summary
- Cost breakdown by provider
- Daily statistics charts
- Detailed reporting

### Settings
- User profile management
- API key management
- Secure key storage

## Getting Started

### Prerequisites

- Node.js 20 or higher
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.local.example .env.local
```

3. Configure environment variables in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000)

## Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t gtm-frontend .

# Run container
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000 gtm-frontend
```

Or use with docker-compose from the root directory:

```bash
cd ..
docker-compose up frontend
```

## Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── dashboard/         # Dashboard pages
│   │   ├── images/       # Image generation
│   │   ├── videos/       # Video generation
│   │   ├── jobs/         # Jobs list
│   │   ├── analytics/    # Analytics dashboard
│   │   └── settings/     # Settings page
│   ├── login/            # Login page
│   ├── register/         # Registration page
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Landing page
│   └── globals.css       # Global styles
├── components/            # React components
│   ├── ui/               # UI components
│   └── dashboard/        # Dashboard components
├── lib/                   # Utilities and config
│   ├── api.ts            # API client
│   ├── types.ts          # TypeScript types
│   ├── store.ts          # Zustand store
│   └── utils.ts          # Helper functions
└── public/               # Static assets
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Key Pages

- `/` - Landing page
- `/login` - User login
- `/register` - User registration
- `/dashboard` - Dashboard home
- `/dashboard/images` - Image generation
- `/dashboard/videos` - Video generation
- `/dashboard/jobs` - Jobs list
- `/dashboard/analytics` - Analytics
- `/dashboard/settings` - User settings

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend API URL | http://localhost:8000 |

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License
