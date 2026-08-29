export { default as DashboardPage } from "./pages/DashboardPage";

export { default as SummaryCards } from "./components/SummaryCards";
export { default as LeadPipeline } from "./components/LeadPipeline";
export { default as BookingPipeline } from "./components/BookingPipeline";
export { default as FinanceSummary } from "./components/FinanceSummary";
export { default as RevenueTrend } from "./components/RevenueTrend";
export { default as UpcomingTrips } from "./components/UpcomingTrips";
export { default as OperationsOverview } from "./components/OperationsOverview";
export { default as MyWorkPanel } from "./components/MyWorkPanel";
export { default as QuickActions } from "./components/QuickActions";

export {
  useSummaryCards,
  useLeadPipeline,
  useBookingPipeline,
  useFinanceSummary,
  useUpcomingTrips,
  useOperationsOverview,
  useRevenueTrend,
} from "./hooks/useDashboard";
export { default as dashboardApi } from "./services/dashboardApi";
export { default as WidgetCard } from "./widgets/WidgetCard";
export { default as WidgetSkeleton } from "./widgets/WidgetSkeleton";
