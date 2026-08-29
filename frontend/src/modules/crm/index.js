export { default as LeadsPage } from "./pages/LeadsPage";
export { default as LeadDetailPage } from "./pages/LeadDetailPage";
export { default as CustomersPage } from "./pages/CustomersPage";

export { default as crmApi } from "./services/crmApi";
export { useLeads, useCreateLead, useCustomers } from "./hooks/useLeads";
export { useLeadDetail, useUpdateLead, useConvertLead, useDeleteLead } from "./hooks/useLeadDetail";
export { useActivities, useCreateActivity } from "./hooks/useActivities";
export { useFollowups, useCreateFollowup, useCompleteFollowup } from "./hooks/useFollowups";
