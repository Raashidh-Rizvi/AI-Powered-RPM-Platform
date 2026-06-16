import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { RpmService } from '../rpm.service';

@Component({
  selector: 'app-patient-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './patient-detail.html',
  styleUrl: './patient-detail.css'
})
export class PatientDetailComponent implements OnInit {
  patient: any = null;
  vitalsData: any[] = [];
  aiFeatures: any[] = [];
  aiRisk: any[] = [];
  aiTrends: any[] = [];
  aiAnomalies: any[] = [];

  constructor(
    private route: ActivatedRoute, 
    private rpmService: RpmService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.rpmService.getPatient(id).subscribe({
        next: (data) => {
          this.patient = data;
          this.cdr.detectChanges();
        }
      });
      
      this.rpmService.getVitals(id).subscribe({
        next: (data: any) => {
          this.vitalsData = data;
          this.cdr.detectChanges();
        }
      });
      
      this.rpmService.getAIFeatures(id).subscribe({
        next: (data: any) => {
          this.aiFeatures = data;
          this.cdr.detectChanges();
        }
      });

      this.rpmService.getAIRisk(id).subscribe({
        next: (data: any) => {
          this.aiRisk = data;
          this.cdr.detectChanges();
        }
      });

      this.rpmService.getAITrends(id).subscribe({
        next: (data: any) => {
          this.aiTrends = data;
          this.cdr.detectChanges();
        }
      });

      this.rpmService.getAIAnomalies(id).subscribe({
        next: (data: any) => {
          this.aiAnomalies = data;
          this.cdr.detectChanges();
        }
      });
    }
  }

  getRiskClass(level: string): string {
    if (!level) return '';
    level = level.toLowerCase();
    if (level === 'critical') return 'text-danger';
    if (level === 'high') return 'text-warning';
    if (level === 'medium') return 'text-primary';
    return 'text-success';
  }

  getDisplayValue(dp: any): number {
    if (dp.value !== null && dp.value !== undefined) return dp.value;
    if (dp.structured_value && dp.structured_value.systolic) return dp.structured_value.systolic;
    return 0;
  }

  getMinValue(vitalGroup: any): number {
    const values = vitalGroup.data_points.map((dp: any) => this.getDisplayValue(dp));
    return values.length > 0 ? Math.min(...values) * 0.9 : 0;
  }

  getMaxValue(vitalGroup: any): number {
    const values = vitalGroup.data_points.map((dp: any) => this.getDisplayValue(dp));
    return values.length > 0 ? Math.max(...values) * 1.1 : 100;
  }

  getChartHeight(dp: any, min: number, max: number): string {
    const value = this.getDisplayValue(dp);
    if (value === 0 && dp.value === null) return '0%';
    if (max === min) return '50%';
    const percentage = ((value - min) / (max - min)) * 100;
    return Math.max(5, percentage) + '%';
  }
}
