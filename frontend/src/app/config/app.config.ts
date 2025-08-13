export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
}

export interface FeatureConfig {
  enableAdvancedOptimization: boolean;
  enablePlayerComparison: boolean;
  enableMockData: boolean;
}

export interface LoggingConfig {
  level: 'debug' | 'info' | 'warn' | 'error';
  enableConsoleLogging: boolean;
}

export interface AppConfig {
  production: boolean;
  api: ApiConfig;
  features: FeatureConfig;
  logging: LoggingConfig;
}