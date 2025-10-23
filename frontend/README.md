# FPL Optimizer - Frontend

> Angular 20 application with Tailwind CSS for Fantasy Premier League team optimization

---

## Overview

Modern, responsive frontend built with Angular 20 (standalone components), TypeScript, and Tailwind CSS. Provides an intuitive interface for:

- Player browsing and filtering
- Team optimization based on budget and formation
- Real-time player statistics
- Premier League branding and styling

---

## Prerequisites

- **Node.js 18+** ([Download](https://nodejs.org/))
- **npm** (comes with Node.js)
- **Angular CLI** (install globally):
  ```bash
  npm install -g @angular/cli
  ```

---

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Edit environment files in `src/app/environments/`:

**`environment.ts` (Development):**
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  useMockServices: false
};
```

### 3. Start Development Server

```bash
ng serve
```

Navigate to `http://localhost:4200/`. The application will automatically reload when you modify source files.

---

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── app.ts                    # Main application component
│   │   ├── app.html                  # Main template
│   │   ├── app.config.ts             # Angular configuration
│   │   ├── app.routes.ts             # Routing configuration
│   │   ├── config/                   # Configuration service
│   │   │   ├── config.service.ts
│   │   │   └── app.config.ts
│   │   ├── environments/             # Environment configurations
│   │   │   ├── environment.ts        # Development
│   │   │   ├── environment.staging.ts # Staging
│   │   │   └── environment.prod.ts   # Production
│   │   ├── services/                 # Angular services
│   │   │   ├── service-interfaces/   # Service abstractions
│   │   │   ├── implementations/      # Real implementations
│   │   │   ├── mock-implementations/ # Mock services for testing
│   │   │   └── service-factory.ts    # Factory pattern
│   │   ├── object-interfaces/        # TypeScript interfaces
│   │   ├── types/                    # Type definitions
│   │   │   └── fpl.types.ts          # FPL-specific types
│   │   ├── player-card/              # Player card component
│   │   └── team-display/             # Team display component
│   ├── index.html                    # HTML entry point
│   └── styles.css                    # Global styles (Tailwind)
├── public/                           # Static assets
│   ├── favicon.ico                   # Premier League logo
│   └── icons/
├── angular.json                      # Angular workspace config
├── package.json                      # Node.js dependencies
├── tailwind.config.js                # Tailwind CSS config
├── tsconfig.json                     # TypeScript configuration
└── README.md                         # This file
```

---

## Development

### Start Development Server

```bash
ng serve
```

With custom port:
```bash
ng serve --port 4200
```

With host binding:
```bash
ng serve --host 0.0.0.0 --port 4200
```

### Code Scaffolding

Angular CLI includes powerful code scaffolding tools:

**Generate Component:**
```bash
ng generate component component-name
```

**Generate Service:**
```bash
ng generate service services/service-name
```

**Generate Module:**
```bash
ng generate module module-name
```

For a complete list of available schematics:
```bash
ng generate --help
```

### Live Reload

The application automatically reloads whenever you modify source files. No configuration needed!

---

## Building

### Development Build

```bash
ng build
```

### Production Build

```bash
ng build --configuration production
```

Build artifacts will be stored in the `dist/` directory. The production build optimizes for:
- Minification
- Tree-shaking
- Ahead-of-time (AOT) compilation
- Bundle optimization

### Staging Build

```bash
ng build --configuration staging
```

---

## Testing

### Unit Tests

Run unit tests with [Karma](https://karma-runner.github.io):

```bash
ng test
```

Run once (no watch mode):
```bash
ng test --watch=false
```

With coverage:
```bash
ng test --code-coverage
```

Coverage report will be in `coverage/` directory.

### End-to-End Tests

```bash
ng e2e
```

> **Note:** Angular CLI does not include an e2e testing framework by default. Popular options include Cypress, Playwright, or Protractor.

---

## Configuration

### Environment Files

**Development (`environment.ts`):**
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  useMockServices: false,
  enableAnalytics: false,
  logLevel: 'debug'
};
```

**Production (`environment.prod.ts`):**
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://api.your-domain.com/api/v1',
  useMockServices: false,
  enableAnalytics: true,
  logLevel: 'error'
};
```

### Using Mock Services

For development without backend:

```typescript
// environment.ts
export const environment = {
  useMockServices: true,  // Enable mock services
  ...
};
```

Mock implementations are in `src/app/services/mock-implementations/`.

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Angular | 20.1.0 |
| Language | TypeScript | 5.8.2 |
| Styling | Tailwind CSS | 3.4.0 |
| HTTP | Angular HttpClient | Built-in |
| Reactive | RxJS | 7.8.0 |
| Testing | Jasmine + Karma | Latest |
| Build | Angular CLI | 20.1.5 |

---

## Key Features

### Angular 20 Features

- ✅ **Standalone Components** - No NgModules required
- ✅ **Modern Control Flow** - `@if`, `@for`, `@switch` syntax
- ✅ **Signals** - Reactive state management
- ✅ **Improved Performance** - Faster change detection

### Tailwind CSS

- ✅ **Utility-first** - Rapid UI development
- ✅ **Responsive** - Mobile-first design
- ✅ **Customizable** - Easy theming via config
- ✅ **PurgeCSS** - Optimized bundle size

### TypeScript

- ✅ **Type Safety** - Catch errors at compile time
- ✅ **IntelliSense** - Better IDE support
- ✅ **Interfaces** - Clear contracts between components

---

## Styling with Tailwind CSS

### Global Styles

Edit `src/styles.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom global styles */
@layer base {
  h1 {
    @apply text-4xl font-bold;
  }
}
```

### Component Styles

Use Tailwind utility classes in templates:

```html
<div class="flex items-center justify-between p-4 bg-white rounded-lg shadow-md">
  <h2 class="text-xl font-semibold text-gray-800">Player Name</h2>
  <span class="text-green-600 font-bold">£8.5M</span>
</div>
```

### Customization

Edit `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        'fpl-primary': '#37003c',    // Premier League purple
        'fpl-secondary': '#00ff87',  // FPL green
      },
    },
  },
};
```

---

## Service Architecture

### Service Factory Pattern

Services are instantiated via factory pattern to support real vs. mock implementations:

```typescript
// service-factory.ts
export class ServiceFactory {
  static createPlayerService(): IPlayerService {
    return environment.useMockServices
      ? new MockPlayerService()
      : new PlayerService(httpClient);
  }
}
```

### Service Interfaces

All services implement interfaces for loose coupling:

```typescript
export interface IPlayerService {
  getPlayers(filters: PlayerFilters): Observable<Player[]>;
  getPlayer(id: number): Observable<Player>;
}
```

---

## Routing

Routes are defined in `src/app/app.routes.ts`:

```typescript
export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'players', component: PlayersComponent },
  { path: 'optimizer', component: OptimizerComponent },
  { path: '**', redirectTo: '' }
];
```

---

## Deployment

### Build for Production

```bash
ng build --configuration production
```

### Serve Static Files

The `dist/` directory contains static files. Serve with:

**Using http-server:**
```bash
npm install -g http-server
http-server dist/frontend -p 8080
```

**Using nginx:**
```nginx
server {
  listen 80;
  server_name your-domain.com;
  root /path/to/dist/frontend;

  location / {
    try_files $uri $uri/ /index.html;
  }
}
```

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build -- --configuration production

FROM nginx:alpine
COPY --from=build /app/dist/frontend /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Build and Run:**
```bash
docker build -t fpl-optimizer-frontend .
docker run -p 80:80 fpl-optimizer-frontend
```

---

## Code Quality

### Linting

```bash
ng lint
```

### Formatting

Use Prettier (if configured):
```bash
npm run format
```

### Type Checking

```bash
npx tsc --noEmit
```

---

## Browser Support

Supports all modern browsers:

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

---

## Troubleshooting

### Common Issues

**Issue: `ng: command not found`**
```bash
# Solution: Install Angular CLI globally
npm install -g @angular/cli
```

**Issue: Port already in use**
```bash
# Solution: Use different port
ng serve --port 4201
```

**Issue: Module not found**
```bash
# Solution: Reinstall dependencies
rm -rf node_modules
npm install
```

**Issue: Tailwind styles not loading**
```bash
# Solution: Ensure Tailwind is properly configured
# Check that styles.css has @tailwind directives
```

---

## Additional Resources

- [Angular Documentation](https://angular.dev/)
- [Angular CLI Reference](https://angular.dev/tools/cli)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [RxJS Documentation](https://rxjs.dev/)

---

## Contributing

See main [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

**Frontend-specific guidelines:**
- Follow Angular style guide
- Use Prettier for code formatting
- Write unit tests for all components and services
- Use TypeScript strict mode
- Follow semantic HTML practices

---

## License

MIT License - See [LICENSE](../LICENSE)
