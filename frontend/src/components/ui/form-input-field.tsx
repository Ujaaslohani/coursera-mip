import * as React from "react";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { type FieldError as RHFFieldError, type UseFormRegisterReturn } from "react-hook-form";

export interface FormInputFieldProps
  extends Omit<React.ComponentProps<typeof Input>, "name"> {
  label: string;
  id: string;
  registration?: UseFormRegisterReturn;
  error?: RHFFieldError | { message?: string };
}

export function FormInputField({
  label,
  id,
  registration,
  error,
  type = "text",
  className,
  ...props
}: FormInputFieldProps) {
  return (
    <Field data-invalid={!!error}>
      <FieldLabel htmlFor={id}>{label}</FieldLabel>
      <Input
        id={id}
        type={type}
        aria-invalid={!!error}
        className={className}
        {...registration}
        {...props}
      />
      {error?.message && <FieldError>{error.message}</FieldError>}
    </Field>
  );
}