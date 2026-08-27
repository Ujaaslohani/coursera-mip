import type { ComponentType } from "react";

// ASSET MODALITY OPTION INTERFACE
export interface ModalityOption {
  label: string;
  value: string;
  icon?: ComponentType<{ className?: string }>;
}

// ASSET REGISTRATION AND PROCESSING JOB API INTERFACES
export interface AssetRegisterRequest {
  modality: string;
  owner?: string | null;
  topic?: string | null;
  concept_tags?: string[];
  storage_url: string;
  permission_scope?: string[];
  metadata?: Record<string, any>;
}

export interface AssetRegisterResponse {
  asset_id: string;
  job_id: string;
  status: string;
  duplicate?: boolean;
}

export interface RegisteredAsset {
  asset_id: string;
  modality: string;
  owner?: string | null;
  topic?: string | null;
  concept_tags?: string[];
  storage_url: string;
  permission_scope?: string[];
  status: string;
  created_at: string;
  metadata?: Record<string, any>;
}

export interface ProcessingJobCreateRequest {
  asset_id: string;
}

export interface ProcessingJobResponse {
  job_id: string;
  asset_id: string;
  stage: string;
  error?: string | null;
  warnings?: string[];
  created_at: string;
  updated_at: string;
}

// ASSET FORM DATA INTERFACE
export interface AssetFormData {
  title: string;
  modality: string;
  owner: string;
  storageUrl: string;
  conceptTags: string;
}

// REGISTRATION AND PROCESSING MUTATION PAYLOAD & RESULT
export interface RegisterAndProcessPayload {
  title: string;
  modality: string;
  owner?: string;
  storageUrl: string;
  conceptTags?: string[];
  permissionScope?: string[];
  metadata?: Record<string, unknown>;
}

export interface RegisterAndProcessResult {
  asset: AssetRegisterResponse;
  job: ProcessingJobResponse;
}
