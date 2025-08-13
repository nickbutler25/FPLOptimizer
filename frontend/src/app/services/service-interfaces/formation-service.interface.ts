import { Observable } from "rxjs";
import { ApiResponse } from "../../object-interfaces/api-response.interface";
import { Formation } from "../../types/fpl.types";

export interface FormationServiceInterface {
  // Essential formation methods
  getSupportedFormations(): Observable<ApiResponse<Formation[]>>;
  validateFormation(formation: Formation): Observable<ApiResponse<{ valid: boolean }>>;
}