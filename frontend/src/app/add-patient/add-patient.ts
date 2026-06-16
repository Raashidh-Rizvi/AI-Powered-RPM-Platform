import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-add-patient',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './add-patient.html',
  styleUrl: './add-patient.css'
})
export class AddPatientComponent {
  patientName: string = '';
  isSubmitting = false;

  constructor(private http: HttpClient, private router: Router) {}

  addPatient() {
    if (!this.patientName.trim()) return;
    this.isSubmitting = true;
    
    this.http.post('http://localhost:8000/patients/', { name: this.patientName }).subscribe({
      next: (res) => {
        this.isSubmitting = false;
        this.router.navigate(['/patients']);
      },
      error: (err) => {
        console.error('Error adding patient', err);
        this.isSubmitting = false;
      }
    });
  }
}
