import service from './index'

/**
 * Fetch aggregated token usage for the dashboard.
 * Returns totals, breakdown by operation, and per-project/simulation lists.
 */
export const getDashboardStats = () => {
  return service.get('/api/analytics/dashboard')
}