import { useQuery } from "@tanstack/react-query";
import proposalApi from "../services/proposalApi";

export function useProposalVersions(leadId) {
  return useQuery({
    queryKey: ["proposal-versions", leadId],
    queryFn: () => proposalApi.getProposalVersions(leadId),
    enabled: !!leadId,
    staleTime: 60 * 1000,
  });
}
export default useProposalVersions;
