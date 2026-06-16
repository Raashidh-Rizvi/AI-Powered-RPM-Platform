import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { RpmService } from '../rpm.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class DashboardComponent implements OnInit {
  patients: any[] = [];
  alerts: any[] = [];

  constructor(private rpmService: RpmService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.rpmService.getPatients().subscribe({
      next: (data) => {
        this.patients = data;
        this.cdr.detectChanges();
      },
      error: (err) => console.error("Error fetching patients:", err)
    });
    this.rpmService.getAlerts().subscribe({
      next: (data) => {
        this.alerts = data;
        this.cdr.detectChanges();
      },
      error: (err) => console.error("Error fetching alerts:", err)
    });
  }

  get highRiskCount() {
    return this.alerts.filter(a => a.severity === 'CRITICAL' || a.severity === 'HIGH').length;
  }
}
