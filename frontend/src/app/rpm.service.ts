import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class RpmService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  getPatients(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/patients/`);
  }

  getPatient(id: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/patients/${id}`);
  }

  getAlerts(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/alerts/`);
  }

  getVitals(patientId: string, range?: string): Observable<any[]> {
    const url = range ? `${this.apiUrl}/vitals/${patientId}?range=${range}` : `${this.apiUrl}/vitals/${patientId}`;
    return this.http.get<any[]>(url);
  }

  getAIFeatures(patientId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/ai/features/${patientId}`);
  }

  getAIRisk(patientId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/ai/risk/${patientId}`);
  }

  getAITrends(patientId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/ai/trends/${patientId}`);
  }

  getAIAnomalies(patientId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/ai/anomalies/${patientId}`);
  }
}
