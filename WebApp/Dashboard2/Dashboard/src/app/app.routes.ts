import { Routes } from '@angular/router';
import { Locations } from './locations/locations';
import { Homepage } from './homepage/homepage';
import { FailedDevices } from './failed-devices/failed-devices';
import { Devices } from './locations/devices/devices';

export const routes: Routes = [
  { path: "", redirectTo: "homepage", pathMatch: "full" },
  { path: "homepage", component: Homepage },
  {
    path: "locations",
    children: [
      { path: "", component: Locations },     // /locations
      { path: ":site", component: Devices },  // /locations/Office
    ],
  },
  { path: "failed-devices", component: FailedDevices },
];
