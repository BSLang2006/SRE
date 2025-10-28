import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

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

@Component({
  selector: 'app-homepage',
  standalone: true,
  templateUrl: './homepage.html',
  styleUrls: ['./homepage.css'],
  imports: [CommonModule, RouterLink],
})

export class Homepage implements OnInit, OnDestroy {
  private http = inject(HttpClient);
  private base = 'http://54.196.221.164:8000';     // FastAPI base
  private pollMs = 150000;                     // simple polling interval
  private timer: any;

  // exposed to template
  loading = false;
  error = '';
  devicesTotal = 0;
  locationsCount = 0;
  devicesDown = 0;
  devicesUpPct = 0;
  failures: { ts: string; site: string; type: string; name: string; ip: string }[] = [];  // current failures 

  // raw items if you want to list them later
  items: DeviceRow[] = [];

  radius = 48;
circumference = 2 * Math.PI * this.radius;  // ~301.59

  ngOnInit() {
    this.refresh();
    this.timer = setInterval(() => this.refresh(), this.pollMs);
  }

  ngOnDestroy() {
    if (this.timer) clearInterval(this.timer);
  }

  refresh() {
    this.loading = true;
    this.error = '';
    this.http.get<DevicesResp>(`${this.base}/devices`).subscribe({
      next: (res) => {
        if (!res?.ok) {
          this.error = 'API error';
          this.loading = false;
          return;
        }
        this.items = res.items || [];
        this.devicesTotal = res.total ?? this.items.length;

        // unique locations from current inventory
        const sites = new Set<string>();
        let up = 0, down = 0;
        for (const d of this.items) {
          this.failures = this.items
          .filter(d => d.status === 'down')
          .map(d => ({
          ts: new Date().toISOString(),
          site: d.site ?? '',
          type: d.type ?? '',
          name: d.name ?? '',
          ip: d.ip ?? ''
        }))
          if (d.site) sites.add(d.site);
          if (d.status === 'down') down++;
          else if (d.status === 'up') up++;
        }
        this.locationsCount = sites.size;
        this.devicesDown = down;
        this.devicesUpPct = this.devicesTotal ? Math.round((up / this.devicesTotal) * 100) : 0;
      },
      error: () => {
        this.error = 'Request failed';
      },
      complete: () => {
        this.loading = false;
      },
    });
  }
}
