import { AppConfig } from "../config/app.config";

export const environment: AppConfig = {
  production: false,
  api: {
    baseUrl: 'http://localhost:5000/api',
    timeout: 30000,
    retryAttempts: 3
  },
  features: {
    enableAdvancedOptimization: true,
    enablePlayerComparison: false,
    enableMockData: true
  },
  logging: {
    level: 'debug' as const,
    enableConsoleLogging: true
  }
};