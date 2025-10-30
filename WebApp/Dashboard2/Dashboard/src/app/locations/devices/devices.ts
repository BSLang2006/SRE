import { Component, signal, computed, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';

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

type DevicesResp = { ok: boolean; items: DeviceRow[]; total: number };

type SortKey = 'status' | 'last_change_at' | 'type' | 'name' | 'ip';

@Component({
  selector: 'app-site-devices',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './devices.html',
  styleUrls: ['./devices.css'],
})
export class Devices {
  private api = 'http://54.196.221.164:8000';
  constructor(private route: ActivatedRoute, private http: HttpClient) {
    // react to :site changes
    effect(() => {
      const s = this.route.snapshot.paramMap.get('site') ?? '';
      this.site.set(s);
      this.fetch(s);
    });
  }

  // state
  site = signal<string>('');
  loading = signal<boolean>(false);
  error = signal<string>('');
  rows = signal<DeviceRow[]>([]);
  sortBy = signal<SortKey>('status');
  sortDir = signal<'asc' | 'desc'>('desc'); // show downs first by default

  // derived (sorted) rows
  sorted = computed(() => {
    const key = this.sortBy();
    const dir = this.sortDir();
    const mul = dir === 'asc' ? 1 : -1;
    const copy = [...this.rows()];
    copy.sort((a, b) => {
      const av = (a as any)[key] ?? '';
      const bv = (b as any)[key] ?? '';
      // status custom order: down < unknown < up (so down first when desc)
      if (key === 'status') {
        const rank = { down: 2, unknown: 1, up: 0 } as any;
        return (rank[av] - rank[bv]) * mul;
      }
      // date sort for last_change_at
      if (key === 'last_change_at') {
        const at = av ? Date.parse(av) : 0;
        const bt = bv ? Date.parse(bv) : 0;
        return (at - bt) * mul;
      }
      // strings fallback (case-insensitive)
      return String(av).toLowerCase().localeCompare(String(bv).toLowerCase()) * mul;
    });
    return copy;
  });

  setSort(key: SortKey) {
    if (this.sortBy() === key) {
      this.sortDir.set(this.sortDir() === 'asc' ? 'desc' : 'asc');
    } else {
      this.sortBy.set(key);
      this.sortDir.set(key === 'status' ? 'desc' : 'asc');
    }
  }

  trackMac = (_: number, r: DeviceRow) => r.mac;

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
}
