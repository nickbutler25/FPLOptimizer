import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { retry, timeout } from 'rxjs/operators';
import { ConfigService } from '../../config/config.service';
import { OptimizationRequest } from '../../object-interfaces/optimization-request.interface';
import { OptimizationResult } from '../../object-interfaces/optimization-result.interface';
import { Formation } from '../../types/fpl.types';
import { OptimizerServiceInterface } from '../service-interfaces/optimizer-service.interface';

@Injectable({
  providedIn: 'root'
})
export class OptimizerService implements OptimizerServiceInterface {

  constructor(
    private http: HttpClient,
    private config: ConfigService
  ) {}

  optimize(budget: number, formation: Formation): Observable<OptimizationResult> {
    const requestData = { budget, formation };
    
    return this.http.post<OptimizationResult>(
      this.config.getApiUrl('optimize'), 
      requestData
    ).pipe(
      timeout(this.config.apiTimeout),
      retry(this.config.apiRetryAttempts)
    );
  }

  optimizeAdvanced(request: OptimizationRequest): Observable<OptimizationResult> {
    return this.http.post<OptimizationResult>(
      this.config.getApiUrl('optimize-advanced'), 
      request
    ).pipe(
      timeout(this.config.apiTimeout),
      retry(this.config.apiRetryAttempts)
    );
  }
}