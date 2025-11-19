import { AppConfig } from "../config/app.config";


export const environment: AppConfig = {
  production: false, // Not production, but optimized
  api: {
    baseUrl: 'https://staging-api.fploptimizer.com/api',
    timeout: 20000,
    retryAttempts: 2
  },
  features: {
    enableAdvancedOptimization: true,
    enablePlayerComparison: true,
    enableMockData: false // Use real API in staging
  },
  logging: {
    level: 'info' as const,
    enableConsoleLogging: true
  }
};