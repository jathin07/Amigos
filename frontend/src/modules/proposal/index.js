export { default as ProposalListPage } from "./pages/ProposalListPage";
export { default as ProposalDetailPage } from "./pages/ProposalDetailPage";
export { default as ProposalBuilderPage } from "./pages/ProposalBuilderPage";

export { default as proposalApi } from "./services/proposalApi";
export { 
  useProposals, 
  useProposalDetail, 
  useCreateProposal, 
  useUpdateProposal, 
  useDeleteProposal, 
  useFinalizeProposal 
} from "./hooks/useProposal";
export { default as useProposalVersions } from "./hooks/useProposalVersions";
export { default as ProposalStatusBadge } from "./components/ProposalStatusBadge";
export { default as FinalizeProposalModal } from "./modals/FinalizeProposalModal";
