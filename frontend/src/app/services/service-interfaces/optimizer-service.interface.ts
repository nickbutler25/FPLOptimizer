import { Observable } from 'rxjs';
import { OptimizationRequest } from '../../object-interfaces/optimization-request.interface';
import { OptimizationResult } from '../../object-interfaces/optimization-result.interface';
import { Formation } from '../../types/fpl.types';

export interface OptimizerServiceInterface {
  optimize(budget: number, formation: Formation): Observable<OptimizationResult>;
  optimizeAdvanced(request: OptimizationRequest): Observable<OptimizationResult>;
}