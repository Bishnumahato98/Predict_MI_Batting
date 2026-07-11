export interface PlayerStats {
  batter: string;
  matches: number;
  total_runs: number;
  avg_runs: number;
  avg_sr: number;
  fifties: number;
}

export interface Prediction {
  name: string;
  role?: string;
  batting_pos: number;
  prediction: "LOW" | "MEDIUM" | "HIGH";
  prob_low: number;
  prob_medium: number;
  prob_high: number;
  avg_runs_last5: number;
  avg_sr_last5: number;
  composite_score?: number;
  has_history: boolean;
}

export interface SquadPlayer {
  name: string;
  role: "BAT" | "WK" | "ALLR" | "BOWL";
  batting_pos: number;
}

export const DEFAULT_SQUAD: SquadPlayer[] = [
  { name: "RG Sharma", role: "BAT", batting_pos: 1 },
  { name: "Ishan Kishan", role: "WK", batting_pos: 2 },
  { name: "SA Yadav", role: "BAT", batting_pos: 3 },
  { name: "TH David", role: "BAT", batting_pos: 4 },
  { name: "HH Pandya", role: "ALLR", batting_pos: 5 },
  { name: "KH Pandya", role: "ALLR", batting_pos: 6 },
  { name: "TL Seifert", role: "WK", batting_pos: 7 },
  { name: "RD Gaikwad", role: "BAT", batting_pos: 3 },
  { name: "N Wadhera", role: "BAT", batting_pos: 4 },
  { name: "Naman Dhir", role: "ALLR", batting_pos: 6 },
  { name: "JJ Bumrah", role: "BOWL", batting_pos: 10 },
  { name: "Mohammad Nabi", role: "ALLR", batting_pos: 7 },
  { name: "Romario Shepherd", role: "ALLR", batting_pos: 8 },
  { name: "Nuwan Thushara", role: "BOWL", batting_pos: 11 },
  { name: "Akash Madhwal", role: "BOWL", batting_pos: 11 },
];

export const VENUES = [
  "Wankhede Stadium, Mumbai",
  "MA Chidambaram Stadium, Chepauk",
  "Eden Gardens, Kolkata",
  "M Chinnaswamy Stadium",
  "Arun Jaitley Stadium",
  "Rajiv Gandhi International Stadium",
  "Sawai Mansingh Stadium",
  "Punjab Cricket Association Stadium, Mohali",
  "Narendra Modi Stadium, Ahmedabad",
];

export const OPPONENTS = [
  "Chennai Super Kings",
  "Royal Challengers Bengaluru",
  "Kolkata Knight Riders",
  "Delhi Capitals",
  "Sunrisers Hyderabad",
  "Rajasthan Royals",
  "Punjab Kings",
  "Gujarat Titans",
  "Lucknow Super Giants",
];
