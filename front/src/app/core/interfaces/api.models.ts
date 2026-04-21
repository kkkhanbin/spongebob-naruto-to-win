export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}

export interface Wallet {
  balance: string;
  bonus_balance: string;
  currency: string;
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  is_verified: boolean;
  is_banned: boolean;
  balance: string;
  bonus_balance: string;
  created_at: string;
}

export interface TransactionItem {
  id: number;
  kind: 'top_up' | 'bet' | 'payout';
  amount: string;
  signed_amount: string;
  balance_after: string;
  description: string;
  game_type: string;
  created_at: string;
}

export interface BlackjackHand {
  cards: string[];
  bet_amount: string;
  status: string;
  result: string;
  payout: string;
  doubled: boolean;
  is_split: boolean;
}

export interface BlackjackSession {
  id: number;
  game_type: string;
  status: 'player_turn' | 'dealer_turn' | 'finished';
  outcome: 'pending' | 'win' | 'loss' | 'push' | 'mixed' | 'blackjack';
  bet_amount: string;
  total_wagered: string;
  payout_amount: string;
  net_result: string;
  player_hands: BlackjackHand[];
  dealer_cards: string[];
  dealer_total: number;
  current_hand_index: number;
  result_message: string;
  client_seed: string;
  server_seed_hash: string;
  show_server_seed: string | null;
  created_at: string;
  updated_at: string;
  finished_at: string | null;
  available_actions: Array<'hit' | 'stand' | 'double' | 'split'>;
}

export interface ApiErrorResponse {
  detail?: string;
  [key: string]: unknown;
}
