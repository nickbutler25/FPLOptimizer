import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { timeout } from 'rxjs/operators';
import { ConfigService } from '../../config/config.service';
import { HealthCheckResponse } from '../../object-interfaces/health-check-response.interface';
import { HealthServiceInterface } from '../service-interfaces/health-service.interface';

@Injectable({
  providedIn: 'root'
})
export class HealthService implements HealthServiceInterface {

  constructor(
    private http: HttpClient,
    private config: ConfigService
  ) {}

  healthCheck(): Observable<HealthCheckResponse> {
    return this.http.get<HealthCheckResponse>(
      this.config.getApiUrl('health')
    ).pipe(
      timeout(5000) // Health checks should be fast
    );
  }
}