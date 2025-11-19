/**
 * Player with expected points for upcoming gameweeks
 */
export interface PlayerWithFixtures {
  id: number;
  web_name: string;
  first_name: string;
  second_name: string;
  team: number;
  team_name?: string;
  element_type: number; // 1=GK, 2=DEF, 3=MID, 4=FWD
  position?: string;
  now_cost: number; // In £0.1m units
  total_points: number;
  form: string;
  selected_by_percent: string;
  minutes: number;
  status: string;
  news: string;
  chance_of_playing_next_round?: number;

  // Expected points for next 5 gameweeks
  expected_points_gw1: number;
  expected_points_gw2: number;
  expected_points_gw3: number;
  expected_points_gw4: number;
  expected_points_gw5: number;
  expected_points_total: number;
}