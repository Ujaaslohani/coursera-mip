"use client";

import { Field, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  FileVideoCamera,
  Image as ImageIcon,
  Captions,
  FileQuestionMark,
  MessagesSquare,
} from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import React from "react";
import { useForm } from "react-hook-form";
import { DataTable } from "./data-table";
import { columns } from "./columns";
import { data } from "@/temp-data/table-data";

export default function NewRegister() {
  const { register, handleSubmit, formState } = useForm();

  const items = [
    { label: "Select a Type", value: null, icon: null },
    { label: "Video", value: "video", icon: FileVideoCamera },
    { label: "Image", value: "image", icon: ImageIcon },
    { label: "Transcript", value: "transcript", icon: Captions },
    { label: "Quiz", value: "quiz", icon: FileQuestionMark },
    { label: "Discussion Thread", value: "discussion", icon: MessagesSquare },
  ];

  // TODO: IMPLEMENT REGISTER API FROM BACKEND
  function onSubmit(data: object) {
    console.log(data);
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Register New Asset"
        description="Register new asset and make it searchable"
      />

      {/* ASSET INTAKE SECTION */}
      <div className="bg-card border border-border rounded-xl p-6 shadow-xs">
        {/* ASSETS REGISTRATION FORM */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <Field>
            <FieldLabel>Title</FieldLabel>
            <Input
              id="title"
              type="text"
              placeholder="e.g Week 3 - Data Modelling walkthrough"
              {...register("title")}
            />
          </Field>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <Field>
              <FieldLabel>Modality</FieldLabel>
              <Select items={items}>
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    {items.map((item) => (
                      <SelectItem
                        key={item.value ?? "default"}
                        value={item.value}
                      >
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
            </Field>

            <Field>
              <FieldLabel>Owner</FieldLabel>
              <Input
                id="owner"
                type="text"
                placeholder="e.g. John Doe"
                {...register("owner")}
              />
            </Field>
          </div>

          <Field>
            <FieldLabel>Storage URL</FieldLabel>
            <Input
              id="storageUrl"
              type="url"
              placeholder="e.g. https://ab123345677.execute-api.us-west-2.amazonaws.com/uploads"
              {...register("storageUrl")}
            />
          </Field>
        </form>
      </div>

      {/* DECIDE TODO : EITHER SHOW MONITOR HERE OR KEEP THE ONE IN THE DASHBOARD  */}
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
        <DataTable columns={columns} data={data} />
      </div>
    </div>
  );
}
