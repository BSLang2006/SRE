import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { RouterOutlet } from '@angular/router';
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

type LocationRow = {
  site: string;
  total: number;
  down: number;
  lastName?: string;
  lastIp?: string;
  lastTs?: string;
};

@Component({
  selector: 'app-locations',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink],
  templateUrl: './locations.html',
  styleUrls: ['./locations.css'],
})
export class Locations implements OnInit {
  private http = inject(HttpClient);
  private base = 'http://54.196.221.164:8000';

  loading = false;
  error = '';
  locationRows: LocationRow[] = [];

  ngOnInit() {
    this.load();
  }

  private load() {
    this.loading = true;
    this.error = '';
    this.http.get<DevicesResp>(`${this.base}/devices`).subscribe({
      next: (res) => {
        if (!res?.ok) { this.error = 'API error'; return; }
        this.locationRows = this.buildLocationRows(res.items || []);
      },
      error: () => this.error = 'Request failed',
      complete: () => this.loading = false,
    });
  }

  private buildLocationRows(items: DeviceRow[]): LocationRow[] {
    const bySite = new Map<string, DeviceRow[]>();
    for (const d of items) {
      const site = d.site ?? 'Unknown';
      if (!bySite.has(site)) bySite.set(site, []);
      bySite.get(site)!.push(d);
    }

    const rows: LocationRow[] = [];
    for (const [site, list] of bySite.entries()) {
      const total = list.length;
      const downs = list.filter(d => d.status === 'down');
      const down = downs.length;

      // Pick the device with the most recent first_down_at (if available)
      let lastName: string | undefined;
      let lastIp: string | undefined;
      let lastTs: string | undefined;

      if (down > 0) {
        const mostRecent = downs.reduce((a, b) => {
          const ta = a.first_down_at ? Date.parse(a.first_down_at) : 0;
          const tb = b.first_down_at ? Date.parse(b.first_down_at) : 0;
          return tb > ta ? b : a;
        });
        lastName = mostRecent.name ?? undefined;
        lastIp = mostRecent.ip ?? undefined;
        lastTs = mostRecent.first_down_at ?? undefined;
      }

      rows.push({ site, total, down, lastName, lastIp, lastTs });
    }

    // Sort: sites with downs first, then alphabetically
    rows.sort((a, b) => (b.down - a.down) || a.site.localeCompare(b.site));
    return rows;
  }
}
