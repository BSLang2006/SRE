import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-device-details',
  standalone: true,
  imports: [CommonModule, RouterLink, HttpClientModule],
  templateUrl: './device-details.html',
  styleUrls: ['./device-details.css'],
})
export class DeviceDetails {
  site: string | null = '';
  mac: string | null = '';
  api = 'http://54.196.221.164:8000';

  device: any = null;   // holds the matched device
  loading = true;
  error = '';

  constructor(private route: ActivatedRoute, private http: HttpClient) {
    this.site = this.route.snapshot.paramMap.get('site');
    this.mac  = this.route.snapshot.paramMap.get('mac');
    this.load();
  }

  private load() {
    if (!this.site || !this.mac) { this.loading = false; return; }
    this.http.get<any>(`${this.api}/devices?site=${encodeURIComponent(this.site)}&limit=1000`)
      .subscribe({
        next: res => {
          this.device = res?.items?.find((d: any) => d.mac === this.mac) ?? null;
        },
        error: () => { this.error = 'Failed to load device'; },
        complete: () => { this.loading = false; },
      });
  }
}
