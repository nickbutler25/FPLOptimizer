// Dynamic service creation
import { Injectable, Injector, inject } from '@angular/core';
import { ConfigService } from '../config/config.service';

// Service Interfaces
import {
  HealthServiceInterface,
  OptimizerServiceInterface,
  PlayersServiceInterface,
  StatisticsServiceInterface
} from './index';

// Mock Implementations
import {
  MockHealthService,
  MockOptimizerService,
  MockPlayersService
} from './mock-implementations';

// Real Implementations
 import {
  HealthService,
  OptimizerService,
  PlayersService,
  StatisticsService
} from './implementations';


@Injectable({
  providedIn: 'root'
})
export class ServiceFactory {
  private injector = inject(Injector);
  private config = inject(ConfigService);

  // Optimizer Service
  createOptimizerService(): OptimizerServiceInterface {
    if (this.config.shouldUseMockData) {
      return this.injector.get(MockOptimizerService);
    } else {
      return this.injector.get(OptimizerService);
    }
  }

  // Players Service
  createPlayersService(): PlayersServiceInterface {
    if (this.config.shouldUseMockData) {
      return this.injector.get(MockPlayersService);
    } else {
      return this.injector.get(PlayersService);
    }
  }

  // Health Service
  createHealthService(): HealthServiceInterface {
    if (this.config.shouldUseMockData) {
      return this.injector.get(MockHealthService);
    } else {
      return this.injector.get(HealthService);
    }
  }

  // Statistics Service
  createStatisticsService(): StatisticsServiceInterface {
    return this.injector.get(StatisticsService);
  }
}