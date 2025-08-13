import { AppConfig } from "../config/app.config";

export const environment = {
  production: true,
  api: {
    baseUrl: 'https://api.fploptimizer.com/api',
    timeout: 15000,
    retryAttempts: 2
  },
  features: {
    enableAdvancedOptimization: true,
    enablePlayerComparison: true,
    enableMockData: false
  },
  logging: {
    level: 'error',
    enableConsoleLogging: false
  }
};