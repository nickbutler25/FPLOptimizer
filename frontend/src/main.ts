
// src/main.ts
import { provideHttpClient } from '@angular/common/http';
import { provideZoneChangeDetection } from '@angular/core';
import { bootstrapApplication } from '@angular/platform-browser';
import { provideRouter } from '@angular/router';

import { App } from './app/app';
import { appConfig } from './app/app.config';

// Import services for DI
import { ConfigService } from './app/config/config.service';
import { ServiceFactory } from './app/services/service-factory';

// Import mock services (they need to be available for injection)
import {
  MockHealthService,
  MockOptimizerService,
  MockPlayersService
} from './app/services/mock-implementations';

import { StatisticsService } from './app/services/implementations/statistics.service';

bootstrapApplication(App, {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter([]), // Empty routes for now
    provideHttpClient(),
    
    // Core services
    ConfigService,
    ServiceFactory,
    
    // Mock services (needed for factory)
    MockOptimizerService,
    MockPlayersService,
    MockHealthService,
    StatisticsService,
    
    // Add any other providers here
    ...appConfig.providers
  ]
}).catch((err) => console.error(err));