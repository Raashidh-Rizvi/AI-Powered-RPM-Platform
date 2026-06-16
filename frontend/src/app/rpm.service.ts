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

  getAlerts(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/alerts/`);
  }
}
