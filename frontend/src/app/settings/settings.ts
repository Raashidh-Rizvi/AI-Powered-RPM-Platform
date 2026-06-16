import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './settings.html',
  styleUrl: './settings.css',
})
export class Settings {
  aiSensitivity = 80;
  emailNotifications = true;
  smsNotifications = true;
  autoTriage = false;

  saveSettings() {
    alert("Settings saved successfully! (Mock Action)");
  }
}
