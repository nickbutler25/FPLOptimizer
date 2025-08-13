import { Injectable } from "@angular/core";
import { delay, Observable, of } from "rxjs";
import { DependencyStatus, HealthCheckResponse, SystemMetrics } from "../../object-interfaces/health-check-response.interface";
import { HealthStatus } from "../../types/fpl.types";
import { HealthServiceInterface } from "../service-interfaces/health-service.interface";


@Injectable({
  providedIn: 'root'
})

export class MockHealthService implements HealthServiceInterface {    

healthCheck(): Observable<HealthCheckResponse> {
    const dependencies: DependencyStatus[] = [
      {
        name: 'FPL API',
        status: 'healthy',
        response_time: 120,
        last_check: new Date().toISOString(),
        version: 'v2.0',
        endpoint: 'https://fantasy.premierleague.com/api/'
      },
      {
        name: 'Cache Service',
        status: 'healthy',
        response_time: 5,
        last_check: new Date().toISOString()
      }
    ];
    
    const systemMetrics: SystemMetrics = {
      cpu_usage: 15.2,
      memory_usage: 68.5,
      disk_usage: 45.1,
      active_connections: 24,
      cache_hit_ratio: 0.87
    };
    
    return of({
      status: 'healthy' as HealthStatus,
      message: 'All systems operational',
      timestamp: new Date().toISOString(),
      uptime: 86400, // 24 hours
      version: '1.0.0',
      environment: 'development' as 'development' | 'staging' | 'production' ,
      dependencies,
      system_metrics: systemMetrics
    }).pipe(delay(200));
  }
}