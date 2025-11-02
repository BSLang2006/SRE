import { Routes } from '@angular/router';
import { Locations } from './locations/locations';
import { Homepage } from './homepage/homepage';
import { FailedDevices } from './failed-devices/failed-devices';
import { Devices } from './locations/devices/devices';
import { DeviceDetails } from './locations/devices/details/device-details/device-details';

export const routes: Routes = [
  { path: "", redirectTo: "homepage", pathMatch: "full" },
  { path: "homepage", component: Homepage },
{
  path: 'locations',
  children: [
    { path: ':site/:mac', component: DeviceDetails }, // detail FIRST
    { path: '', component: Locations },
    { path: ':site', component: Devices },
  ],
},
  { path: "failed-devices", component: FailedDevices },
];
