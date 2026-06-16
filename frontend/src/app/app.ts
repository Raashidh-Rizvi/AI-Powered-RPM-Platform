import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RpmService } from './rpm.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  title = 'frontend';
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
}
