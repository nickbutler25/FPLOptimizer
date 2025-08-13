import { Observable } from 'rxjs';
import { HealthCheckResponse } from '../../object-interfaces/health-check-response.interface';


export interface HealthServiceInterface {
  // Basic health monitoring
  healthCheck(): Observable<HealthCheckResponse>;
}