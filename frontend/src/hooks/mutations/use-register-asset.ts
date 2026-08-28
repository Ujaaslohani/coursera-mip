import { useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/api/axios";
import {
  type AssetRegisterRequest,
  type AssetRegisterResponse,
  type ProcessingJobResponse,
  type RegisterAndProcessPayload,
  type RegisterAndProcessResult,
} from "@/types/asset.types";

export type { RegisterAndProcessPayload, RegisterAndProcessResult };

// MUTATION HOOK — REGISTERS ASSET AND INITIATES PROCESSING JOB
export const useRegisterAsset = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: RegisterAndProcessPayload): Promise<RegisterAndProcessResult> => {
      // 1. REGISTER THE ASSET IN BACKEND
      const registerPayload: AssetRegisterRequest = {
        storage_url: payload.storageUrl,
        modality: payload.modality,
        owner: payload.owner || "Anonymous",
        topic: payload.title,
        concept_tags: payload.conceptTags || [],
        permission_scope: payload.permissionScope || [],
        metadata: {
          title: payload.title,
          ...(payload.metadata || {}),
        },
      };

      const { data: assetData } = await api.post<AssetRegisterResponse>(
        "/api/assets",
        registerPayload
      );

      // 2. START THE PROCESSING/INGESTION JOB FOR THE ASSET
      const { data: jobData } = await api.post<ProcessingJobResponse>(
        "/api/processing-jobs",
        {
          asset_id: assetData.asset_id,
        }
      );

      return {
        asset: assetData,
        job: jobData,
      };
    },
    onSuccess: () => {
      // INVALIDATE REGISTERED ASSETS LIST TO REFRESH TABLE
      queryClient.invalidateQueries({ queryKey: ["registered-assets"] });
    },
  });
};
