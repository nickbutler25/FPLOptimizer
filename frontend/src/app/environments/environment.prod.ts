import { AppConfig } from "../config/app.config";

export const environment: AppConfig = {
  production: true,
  api: {
    baseUrl: 'https://your-backend.onrender.com/api/v1',  // TODO: Replace with your Render URL after deployment
    timeout: 30000,
    retryAttempts: 3
  },
  features: {
    enableAdvancedOptimization: true,
    enablePlayerComparison: false,
    enableMockData: false
  },
  logging: {
    level: 'error' as const,
    enableConsoleLogging: false
  }
};