"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { Eye, EyeOff, Lock, Mail, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { Checkbox } from "@/components/ui/checkbox";
import { ThemeToggle } from "@/components/theme-toggle";
import { type LoginFormValues } from "@/types/login.types";

export default function LoginPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    defaultValues: {
      email: "",
      password: "",
      rememberMe: false,
    },
    mode: "onTouched",
  });

  const onSubmit = async (_data: LoginFormValues) => {
    setErrorMessage("");
    setIsLoading(true);
    try {
      // Navigate to dashboard
      router.push("/dashboard");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to sign in.";
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleContinueWithoutLogin = () => {
    router.push("/dashboard");
  };

  const isProcessing = isSubmitting || isLoading;

  return (
    <div className="relative min-h-screen w-full flex flex-col justify-between bg-background text-foreground selection:bg-primary/20 selection:text-primary">
      {/* THEME TOGGLE IN CORNER */}
      <div className="absolute top-4 right-4 z-10">
        <ThemeToggle />
      </div>

      {/* MAIN LOGIN CARD SECTION */}
      <main className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-[420px]">
          {/* CARD CONTAINER */}
          <div className="rounded-2xl border border-border bg-card p-7 md:p-8 shadow-sm transition-all">
            {/* CARD HEADER */}
            <div className="text-center mb-6 space-y-1.5">
              <h1 className="text-2xl font-bold font-heading tracking-tight text-foreground">
                System Access
              </h1>
              <p className="text-sm text-muted-foreground">
                Sign in with your organization account to continue
              </p>
            </div>

            {/* ERROR MESSAGE */}
            {errorMessage && (
              <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-center gap-2">
                <span>{errorMessage}</span>
              </div>
            )}

            {/* FORM */}
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {/* EMAIL FIELD */}
              <Field data-invalid={!!errors.email} className="space-y-1.5">
                <FieldLabel
                  htmlFor="email"
                  className="text-xs font-semibold tracking-wider text-muted-foreground"
                >
                  Email Address
                </FieldLabel>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground pointer-events-none" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="name@coursera.org"
                    autoComplete="email"
                    aria-invalid={!!errors.email}
                    className="h-10 pl-9.5 text-sm bg-background border-input focus-visible:border-primary focus-visible:ring-primary/20"
                    {...register("email", {
                      required: "Email address is required",
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: "Please enter a valid email address",
                      },
                    })}
                  />
                </div>
                {errors.email?.message && (
                  <FieldError>{errors.email.message}</FieldError>
                )}
              </Field>

              {/* PASSWORD FIELD */}
              <Field data-invalid={!!errors.password} className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <FieldLabel
                    htmlFor="password"
                    className="text-xs font-semibold tracking-wider text-muted-foreground"
                  >
                    Password
                  </FieldLabel>
                  <a
                    href="#forgot-password"
                    onClick={(e) => {
                      e.preventDefault();
                      alert(
                        "Please contact your MIP platform administrator to reset credentials.",
                      );
                    }}
                    className="text-xs font-medium text-primary hover:text-primary-hover transition-colors"
                  >
                    Forgot password?
                  </a>
                </div>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground pointer-events-none" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••••••"
                    autoComplete="current-password"
                    aria-invalid={!!errors.password}
                    className="h-10 pl-9.5 pr-10 text-sm bg-background border-input focus-visible:border-primary focus-visible:ring-primary/20"
                    {...register("password", {
                      required: "Password is required",
                      minLength: {
                        value: 6,
                        message: "Password must be at least 6 characters",
                      },
                    })}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors p-0.5 rounded focus:outline-hidden cursor-pointer"
                    aria-label={
                      showPassword ? "Hide password" : "Show password"
                    }
                  >
                    {showPassword ? (
                      <EyeOff className="size-4" />
                    ) : (
                      <Eye className="size-4" />
                    )}
                  </button>
                </div>
                {errors.password?.message && (
                  <FieldError>{errors.password.message}</FieldError>
                )}
              </Field>

              {/* REMEMBER ME CHECKBOX */}
              <div className="flex items-center justify-between pt-1">
                <Checkbox
                  id="remember-me"
                  label="Remember my session"
                  {...register("rememberMe")}
                />
              </div>

              {/* SIGN IN BUTTON */}
              <Button
                type="submit"
                disabled={isProcessing}
                className="w-full h-10 font-semibold text-sm bg-primary hover:bg-primary-hover text-primary-foreground cursor-pointer mt-2"
              >
                {isProcessing ? (
                  <span className="flex items-center gap-2">
                    <span className="size-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                    Signing in...
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    Sign in to platform
                    <ArrowRight className="size-4" />
                  </span>
                )}
              </Button>

              {/* DIVIDER */}
              <div className="relative my-4">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-card px-2 text-muted-foreground">Or</span>
                </div>
              </div>

              {/* CONTINUE WITHOUT LOGIN BUTTON */}
              <Button
                type="button"
                variant="outline"
                onClick={handleContinueWithoutLogin}
                className="w-full h-10 font-medium text-sm border-border hover:bg-muted text-foreground cursor-pointer"
              >
                Continue without login
              </Button>
            </form>
          </div>
        </div>
      </main>

      {/* FOOTER */}
      <footer className="w-full py-4 text-center text-xs text-muted-foreground border-t border-border/50">
        <p>
          © {new Date().getFullYear()} Coursera Inc. Multimodal Intelligence
          Platform
        </p>
      </footer>
    </div>
  );
}
