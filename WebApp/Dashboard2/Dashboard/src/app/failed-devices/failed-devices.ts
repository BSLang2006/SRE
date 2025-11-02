import { Component, OnInit, inject } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Router, RouterLink, RouterModule } from '@angular/router';

type DeviceRow = {
  mac: string;
  site: string | null;
  type: string | null;
  name: string | null;
  ip: string | null;
  status: 'up' | 'down' | 'unknown';
  first_down_at?: string | null;
  last_seen?: string | null;
  metrics?: Record<string, unknown>;
};
type DevicesResp = { ok: boolean; items: DeviceRow[]; total: number };

type DownRow = {
  mac: string;
  site: string;
  name?: string;
  ip?: string;
  type?: string;
  firstDownAt?: string;
  lastSeen?: string;
  minutesDown?: number;
};

@Component({
  selector: 'app-failed-devices',
  standalone: true,
  imports: [CommonModule, DatePipe, RouterModule],
  templateUrl: './failed-devices.html',
  styleUrls: ['./failed-devices.css'],
})
export class FailedDevices implements OnInit {
  private http = inject(HttpClient);
  private router = inject(Router);
  private base = 'http://54.196.221.164:8000';

  loading = false;
  error = '';
  rows: DownRow[] = [];

  ngOnInit() { this.load(); }
  refresh() { this.load(); }

  goToSite(site: string) {
    this.router.navigate(['/locations', site]);
  }

  goToDevice(site: string, mac: string) {
    this.router.navigate(['/locations', site, mac]);
  }

  private load() {
    this.loading = true;
    this.error = '';
    this.http.get<DevicesResp>(`${this.base}/devices`).subscribe({
      next: (res) => {
        if (!res?.ok) { this.error = 'API error'; return; }
        const now = Date.now();
        const downs = (res.items || []).filter(d => d.status === 'down');
        this.rows = downs.map<DownRow>(d => {
          const t = d.first_down_at ? Date.parse(d.first_down_at) : undefined;
          return {
            mac: d.mac,
            site: d.site ?? 'Unknown',
            name: d.name ?? undefined,
            ip: d.ip ?? undefined,
            type: d.type ?? undefined,
            firstDownAt: d.first_down_at ?? undefined,
            lastSeen: d.last_seen ?? undefined,
            minutesDown: t ? Math.max(0, Math.round((now - t) / 60000)) : undefined,
          };
        }).sort((a, b) => {
          const ta = a.firstDownAt ? Date.parse(a.firstDownAt) : 0;
          const tb = b.firstDownAt ? Date.parse(b.firstDownAt) : 0;
          return (tb - ta) || a.site.localeCompare(b.site);
        });
      },
      error: () => this.error = 'Request failed',
      complete: () => this.loading = false,
    });
  }
}
