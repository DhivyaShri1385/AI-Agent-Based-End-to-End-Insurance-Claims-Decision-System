export type InsuranceType = "HEALTH" | "ACCIDENT" | "THEFT";
export type PolicyStatus = "ACTIVE" | "EXPIRED" | "CANCELLED" | "SUSPENDED";

// Monetary values arrive as decimal strings (e.g. "500000.00") to avoid float rounding.
export interface PolicySummary {
  id: string;
  policy_number: string;
  holder_id: string;
  insurance_type: InsuranceType;
  status: PolicyStatus;
  start_date: string;
  end_date: string;
  coverage_limit: string;
  deductible: string;
  copay_percent: string;
  waiting_period_days: number;
}

export interface PolicyListResponse {
  items: PolicySummary[];
  total: number;
  page: number;
  page_size: number;
}
