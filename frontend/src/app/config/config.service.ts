import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { AppConfig, FeatureConfig } from './app.config';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  private readonly config: AppConfig = environment;

  get apiBaseUrl(): string {
    return this.config.api.baseUrl;
  }

  get apiTimeout(): number {
    return this.config.api.timeout;
  }

  get apiRetryAttempts(): number {
    return this.config.api.retryAttempts;
  }

  get isProduction(): boolean {
    return this.config.production;
  }

  get shouldUseMockData(): boolean {
    return this.config.features.enableMockData;
  }

  get isAdvancedOptimizationEnabled(): boolean {
    return this.config.features.enableAdvancedOptimization;
  }

  get loggingLevel(): string {
    return this.config.logging.level;
  }

  get shouldLogToConsole(): boolean {
    return this.config.logging.enableConsoleLogging;
  }

  // Get full API endpoint URL
  getApiUrl(endpoint: string): string {
    return `${this.apiBaseUrl}/${endpoint.replace(/^\//, '')}`;
  }

  // Check if feature is enabled
  isFeatureEnabled(feature: keyof FeatureConfig): boolean {
    return this.config.features[feature];
  }
}