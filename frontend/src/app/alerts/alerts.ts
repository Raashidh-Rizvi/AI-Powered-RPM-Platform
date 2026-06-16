import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-alerts',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './alerts.html',
  styleUrl: './alerts.css',
})
export class Alerts implements OnInit {
  alerts: any[] = [];
  isLoading: boolean = true;

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.http.get<any[]>('http://localhost:8000/alerts/').subscribe({
      next: (data) => {
        // Sort by newest first
        this.alerts = data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error fetching alerts:', err);
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }
}
