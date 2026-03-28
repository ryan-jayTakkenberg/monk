export interface JournalEntry {
  id: number
  date: string
  answer_1: string
  answer_2: string
  answer_3: string
  answer_4: string
}

export interface Meal {
  id: number
  name: string
  kcal: number
  protein_g: number
  carbs_g: number
  fat_g: number
  photo: string | null
  logged_at: string
}

export interface MealTotals {
  kcal: number
  protein_g: number
  carbs_g: number
  fat_g: number
}

export interface MealAnalysis {
  name: string
  kcal: number
  protein_g: number
  carbs_g: number
  fat_g: number
}

export interface Suggestion {
  title: string
  description: string
}

export interface SleepData {
  recorded_date: string
  duration_hours: number
  awake_pct: number
  light_pct: number
  deep_pct: number
  recovery_score: number
  hrv: number
}

export interface HealthData {
  connected: boolean
  data: SleepData | null
}

export interface HistoryEntry {
  date: string
  recovery_score: number
  duration_hours: number
  hrv: number
  deep_pct: number
}

export interface MealSettings {
  kcal_goal: number
  protein_goal_g: number
}
