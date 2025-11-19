import { AppConfig } from "../app/config/app.config";

export const environment: AppConfig = {
  production: false,
  api: {
    baseUrl: 'http://localhost:8000/api/v1',  // Updated to point to FastAPI backend
    timeout: 30000,
    retryAttempts: 3
  },
  features: {
    enableAdvancedOptimization: true,
    enablePlayerComparison: false,
    enableMockData: false  // Changed to false to use real backend
  },
  logging: {
    level: 'debug' as const,
    enableConsoleLogging: true
  }
};