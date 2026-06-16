import { Routes } from '@angular/router';
import { DashboardComponent } from './dashboard/dashboard';
import { Patients } from './patients/patients';
import { PatientDetailComponent } from './patient-detail/patient-detail';
import { Alerts } from './alerts/alerts';
import { Settings } from './settings/settings';
import { AddPatientComponent } from './add-patient/add-patient';

export const routes: Routes = [
  { path: '', redirectTo: '/overview', pathMatch: 'full' },
  { path: 'overview', component: DashboardComponent },
  { path: 'patients', component: Patients },
  { path: 'patients/:id', component: PatientDetailComponent },
  { path: 'alerts', component: Alerts },
  { path: 'settings', component: Settings },
  { path: 'add-patient', component: AddPatientComponent },
];
