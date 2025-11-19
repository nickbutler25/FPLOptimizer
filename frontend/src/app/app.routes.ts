import { Routes } from '@angular/router';
import { TeamDisplay } from './team-display/team-display';
import { TransferPlanner } from './transfer-planner/transfer-planner';

export const routes: Routes = [
  { path: '', redirectTo: '/team', pathMatch: 'full' },
  { path: 'team', component: TeamDisplay },
  { path: 'transfers', component: TransferPlanner },
];
