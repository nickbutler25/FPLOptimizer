import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';

import { provideHttpClient } from '@angular/common/http';
import { routes } from './app.routes';
import { ConfigService } from './config/config.service';
import { MockHealthService, MockOptimizerService, MockPlayersService, StatisticsService } from './services';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(),
    MockOptimizerService,
    MockPlayersService,
    MockHealthService,
    StatisticsService,
    ConfigService
  ]
};
