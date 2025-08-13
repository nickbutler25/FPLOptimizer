import { Injectable } from "@angular/core";
import { delay, Observable, of } from "rxjs";
import { ApiResponse } from "../../object-interfaces/api-response.interface";
import { ApiStatus, Formation, FORMATIONS } from "../../types/fpl.types";
import { FormationServiceInterface } from "../service-interfaces/formation-service.interface";


@Injectable({
  providedIn: 'root'
})

export class MockFormationService implements FormationServiceInterface {    

    getSupportedFormations(): Observable<ApiResponse<Formation[]>> {
        return of({
            status: 'success' as ApiStatus,
            data: [...FORMATIONS],
            timestamp: new Date().toISOString()
            }).pipe(delay(100));
        }


    validateFormation(formation: Formation): Observable<ApiResponse<{ valid: boolean }>> {
        return of({
            status: 'success' as ApiStatus, 
            data: { valid: true },      
            timestamp: new Date().toISOString()
            }).pipe(delay(100));
        }
}