"use client";

import React, { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { Spinner } from "@/components/ui/spinner";

import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { FormInputField } from "@/components/ui/form-input-field";
import { Button } from "@/components/ui/button";
import { StatusBanner } from "@/components/ui/status-banner";
import { PageHeader } from "@/components/ui/page-header";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { DataTable } from "@/components/new-register/data-table";
import { columns } from "@/components/new-register/columns";
import { useRegisteredAssets } from "@/hooks/query/use-registered-assets";
import { useRegisterAsset } from "@/hooks/mutations/use-register-asset";
import { type AssetFormData } from "@/types/asset.types";
import {
  ASSET_MODALITY_OPTIONS,
  DEFAULT_ASSET_FORM_VALUES,
} from "@/constants/asset.constants";

export default function NewRegister() {
  const [submitMessage, setSubmitMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<AssetFormData>({
    defaultValues: DEFAULT_ASSET_FORM_VALUES,
    mode: "onTouched",
  });

  const { data: registeredData = [], isLoading: isTableLoading } =
    useRegisteredAssets();
  const registerMutation = useRegisterAsset();

  async function onSubmit(formData: AssetFormData) {
    setSubmitMessage(null);
    console.log("[NewRegister] Submitting asset form:", formData);
    try {
      const parsedConceptTags = formData.conceptTags
        ? formData.conceptTags
            .split(",")
            .map((tag) => tag.trim())
            .filter(Boolean)
        : [];

      const result = await registerMutation.mutateAsync({
        title: formData.title,
        modality: formData.modality,
        owner: formData.owner || "Anonymous",
        storageUrl: formData.storageUrl,
        conceptTags: parsedConceptTags,
        permissionScope: ["public"],
      });

      console.log("[NewRegister] Asset registration result:", result);

      if (result.asset.duplicate) {
        setSubmitMessage({
          type: "success",
          text: `Asset already existed (${result.asset.asset_id}). Resumed processing job ${result.job.job_id} (Stage: ${result.job.stage}).`,
        });
      } else {
        setSubmitMessage({
          type: "success",
          text: `Asset registered successfully! Ingestion job ${result.job.job_id} is now in stage "${result.job.stage}".`,
        });
      }

      reset();
    } catch (err: unknown) {
      console.error("[NewRegister] Registration failed:", err);
      const errorMsg =
        err instanceof Error ? err.message : "Failed to register asset.";
      setSubmitMessage({
        type: "error",
        text: errorMsg,
      });
    }
  }

  const isProcessing = isSubmitting || registerMutation.isPending;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Register New Asset"
        description="Register new asset and make it searchable"
      />

      {/* ASSET INTAKE SECTION */}
      <div className="bg-card border border-border rounded-xl p-6 shadow-xs space-y-5">
        {submitMessage && (
          <StatusBanner
            type={submitMessage.type}
            message={submitMessage.text}
          />
        )}

        {/* ASSETS REGISTRATION FORM */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <FormInputField
            id="title"
            label="Title"
            placeholder="e.g Week 3 - Data Modelling walkthrough"
            error={errors.title}
            registration={register("title", {
              required: "Asset title is required",
              minLength: {
                value: 3,
                message: "Title must be at least 3 characters",
              },
            })}
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <Field data-invalid={!!errors.modality}>
              <FieldLabel>Modality</FieldLabel>
              <Controller
                name="modality"
                control={control}
                rules={{ required: "Modality selection is required" }}
                render={({ field }) => (
                  <Select
                    value={field.value}
                    onValueChange={(val) => field.onChange(val)}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectGroup>
                        {ASSET_MODALITY_OPTIONS.map((item) => (
                          <SelectItem key={item.value} value={item.value}>
                            <span className="flex items-center gap-2">
                              {item.icon && (
                                <item.icon className="h-4 w-4 text-muted-foreground shrink-0" />
                              )}
                              <span>{item.label}</span>
                            </span>
                          </SelectItem>
                        ))}
                      </SelectGroup>
                    </SelectContent>
                  </Select>
                )}
              />
              {errors.modality?.message && (
                <FieldError>{errors.modality.message}</FieldError>
              )}
            </Field>

            <FormInputField
              id="owner"
              label="Owner"
              placeholder="e.g. John Doe"
              error={errors.owner}
              registration={register("owner")}
            />
          </div>

          <FormInputField
            id="storageUrl"
            label="Storage URL"
            type="url"
            placeholder="e.g. https://ab123345677.execute-api.us-west-2.amazonaws.com/uploads/lec01.vtt"
            error={errors.storageUrl}
            registration={register("storageUrl", {
              required: "Storage URL is required",
              pattern: {
                value: /^https?:\/\/.+/i,
                message:
                  "Please enter a valid URL (starting with http:// or https://)",
              },
            })}
          />

          <FormInputField
            id="conceptTags"
            label="Concept Tags"
            placeholder="e.g. neural-networks, optimization, transformers (comma separated)"
            error={errors.conceptTags}
            registration={register("conceptTags")}
          />

          <div className="flex justify-end pt-2">
            <Button type="submit" disabled={isProcessing}>
              {isProcessing ? (
                <>
                  <Spinner className="h-4 w-4 mr-2" />
                  Registering & Starting Ingestion...
                </>
              ) : (
                "Register"
              )}
            </Button>
          </div>
        </form>
      </div>

      {/* REGISTERED ASSETS AND PROCESSING TABLE SECTION */}
      <div className="bg-card border border-border rounded-xl p-6 shadow-xs space-y-4">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">
            Registered Assets
          </h2>
          <p className="text-sm text-muted-foreground">
            List of currently registered assets and their processing status
          </p>
        </div>
        {isTableLoading ? (
          <div className="flex items-center justify-center h-32 text-sm text-muted-foreground gap-2">
            <Spinner className="h-4 w-4 text-muted-foreground" />
            Loading registered assets...
          </div>
        ) : (
          <DataTable columns={columns} data={registeredData} />
        )}
      </div>
    </div>
  );
}
