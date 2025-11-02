import { Component, computed, signal, inject, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { makeSorter, SortDir } from '../../shared/sort';

type DeviceRow = {
  mac: string;
  site: string | null;
  type: string | null;
  name: string | null;
  ip: string | null;
  status: 'up' | 'down' | 'unknown';
  first_down_at?: string | null;
  last_seen?: string | null;
  last_change_at?: string | null;
  metrics?: Record<string, unknown>;
  last_failure_reason?: string | null;
  latency_ms?: number | null;
};

// ✅ This was missing → now it's back.
type DevicesResp = { ok: boolean; items: DeviceRow[]; total: number };

type SortKey = 'status' | 'last_change_at' | 'type' | 'name' | 'ip';

@Component({
  selector: 'app-site-devices',
  standalone: true,
  imports: [CommonModule, RouterLink, HttpClientModule], // ✅ Now HttpClient works here
  templateUrl: './devices.html',
  styleUrls: ['./devices.css'],
})
export class Devices implements OnInit, OnDestroy {
  private api = 'http://54.196.221.164:8000';
  private http = inject(HttpClient);
  private route = inject(ActivatedRoute);
  private sub: any;

  site = signal<string>('');
  loading = signal<boolean>(false);
  error = signal<string>('');
  rows = signal<DeviceRow[]>([]);

  sortBy = signal<SortKey>('status');
  sortDir = signal<SortDir>('desc');

  private accessors: Record<SortKey, (r: DeviceRow) => unknown> = {
    status: r => r.status,
    last_change_at: r => (r.last_change_at ? Date.parse(r.last_change_at) : 0),
    type: r => r.type ?? '',
    name: r => r.name ?? r.mac,
    ip: r => r.ip ?? '',
  };

  setSort(col: SortKey) {
    if (this.sortBy() === col) {
      this.sortDir.set(this.sortDir() === 'asc' ? 'desc' : 'asc');
    } else {
      this.sortBy.set(col);
      this.sortDir.set(col === 'status' ? 'desc' : 'asc');
    }
  }

  sorted = computed(() =>
    this.rows().slice().sort(
      makeSorter(
        { by: this.sortBy(), dir: this.sortDir() },
        this.accessors
      )
    )
  );

  trackMac = (_: number, r: DeviceRow) => r.mac;

  ngOnInit() {
    const initial = this.route.snapshot.paramMap.get('site') ?? '';
    this.site.set(initial);
    this.fetch(initial);

    this.sub = this.route.paramMap.subscribe(pm => {
      const s = pm.get('site') ?? '';
      this.site.set(s);
      this.fetch(s);
    });
  }

  private fetch(site: string) {
    this.loading.set(true);
    this.error.set('');
    this.http
      .get<DevicesResp>(`${this.api}/devices?site=${encodeURIComponent(site)}&limit=1000`)
      .subscribe({
        next: (res) => {
          if (!res?.ok) {
            this.error.set('API error');
            return;
          }
          this.rows.set(res.items ?? []);
        },
        error: () => this.error.set('Request failed'),
        complete: () => this.loading.set(false),
      });
  }

  ngOnDestroy() {
    this.sub?.unsubscribe();
  }
}
