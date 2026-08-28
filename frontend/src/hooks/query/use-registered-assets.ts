import { useQuery } from "@tanstack/react-query";
import api from "@/api/axios";
import { Processing } from "@/types";
import { RegisteredAsset } from "@/types/asset.types";

// QUERY HOOK — FETCHES REGISTERED ASSETS AND MAPS THEM FOR THE DATA TABLE
export const useRegisteredAssets = () => {
  return useQuery({
    queryKey: ["registered-assets"],
    queryFn: async () => {
      const { data } = await api.get<RegisteredAsset[]>("/api/assets/registered");
      return data;
    },
    select: (assets): Processing[] => {
      return assets.map((asset) => ({
        mode: asset.modality,
        topic: asset.topic || (asset.metadata?.title as string) || "Untitled Asset",
        owner: asset.owner || "Anonymous",
        stage: asset.status,
        assetId: asset.asset_id,
      }));
    },
    staleTime: 10_000,
  });
};
