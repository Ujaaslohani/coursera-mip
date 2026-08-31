"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  User,
  Mail,
  Building,
  ShieldCheck,
  Sparkles,
  Database,
  CheckCircle2,
  LogOut,
  Save,
  BookOpen,
  Layers,
  Clock,
  Lock,
} from "lucide-react";
import toast from "react-hot-toast";

export default function ProfilePage() {
  const router = useRouter();

  // PROFILE STATE
  const [name, setName] = useState("Navya");
  const [title, setTitle] = useState("Curriculum Specialist & Lead Instructor");
  const [email, setEmail] = useState("navya@coursera.org");
  const [department, setDepartment] = useState(
    "Pedagogical AI & Multimodal Intelligence",
  );
  const [timezone, setTimezone] = useState("UTC-08:00 (Pacific Time)");
  const [bio, setBio] = useState(
    "Focusing on computer science curricula, learner telemetry analysis, multimodal segmentation, and AI-curated pedagogical interventions.",
  );

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success("Profile updated successfully!");
  };

  const handleSignOut = () => {
    toast.success("Signed out successfully");
    router.push("/");
  };

  return (
    <div className="space-y-6 pb-10 w-full">
      {/* PAGE HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <PageHeader
          title="Account & Profile"
          description="Manage your educator profile, institutional information, and platform access scopes."
        />
        <div className="flex items-center gap-2 self-start sm:self-auto shrink-0">
          <Button
            variant="outline"
            size="sm"
            onClick={handleSignOut}
            className="h-9 gap-1.5 text-xs text-destructive hover:bg-destructive/10 hover:border-destructive/30 cursor-pointer"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span>Sign Out</span>
          </Button>
          <Button
            size="sm"
            onClick={handleSave}
            className="h-9 gap-1.5 text-xs bg-primary text-primary-foreground hover:bg-primary-hover cursor-pointer"
          >
            <Save className="h-3.5 w-3.5" />
            <span>Save Changes</span>
          </Button>
        </div>
      </div>

      {/* USER HERO OVERVIEW CARD */}
      <Card className="border-border/80 shadow-xs overflow-hidden bg-card">
        <CardContent className="p-5 sm:p-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="flex size-16 sm:size-18 shrink-0 items-center justify-center rounded-2xl bg-primary text-primary-foreground font-bold text-2xl shadow-md">
                  {name.charAt(0)}
                </div>
                <span className="absolute -bottom-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-emerald-500 ring-2 ring-card">
                  <span className="h-2 w-2 rounded-full bg-white animate-pulse" />
                </span>
              </div>

              <div className="space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="text-xl font-bold font-heading text-foreground">
                    {name}
                  </h1>
                  <Badge
                    variant="default"
                    className="text-[10px] px-2 py-0.5 bg-primary/10 text-primary border-primary/20"
                  >
                    Lead Reviewer
                  </Badge>
                  <Badge
                    variant="success"
                    className="text-[10px] px-2 py-0.5 gap-1"
                  >
                    <ShieldCheck className="h-3 w-3" />
                    SSO Active
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground font-medium">
                  {title}
                </p>
                <div className="flex flex-wrap items-center gap-3 pt-1 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1.5">
                    <Mail className="h-3.5 w-3.5" />
                    {email}
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1.5">
                    <Building className="h-3.5 w-3.5" />
                    {department}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex flex-row md:flex-col items-center md:items-end justify-between border-t md:border-t-0 pt-4 md:pt-0 border-border/50 gap-2 text-xs text-muted-foreground">
              <span className="inline-flex items-center gap-1">
                <Clock className="h-3.5 w-3.5" />
                Member since Jan 2024
              </span>
              <span className="font-mono text-[11px] bg-muted px-2.5 py-0.5 rounded border border-border/60">
                User ID: usr_m1p9942
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* BALANCED 2-COLUMN GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full items-stretch">
        {/* LEFT COLUMN: PERSONAL & ORGANIZATION INFORMATION */}
        <Card className="border-border/80 shadow-xs flex flex-col justify-between">
          <div>
            <CardHeader className="border-b border-border/40 pb-3.5">
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-primary" />
                <CardTitle className="text-sm font-semibold">
                  Personal & Organizational Information
                </CardTitle>
              </div>
              <CardDescription className="text-xs">
                Your public profile details and workspace contact information.
              </CardDescription>
            </CardHeader>
            <CardContent className="p-5 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">
                    Display Name
                  </label>
                  <Input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="h-9 text-xs"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">
                    Professional Title
                  </label>
                  <Input
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="h-9 text-xs"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">
                    Email Address
                  </label>
                  <Input
                    value={email}
                    disabled
                    className="h-9 text-xs bg-muted/50 cursor-not-allowed"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">
                    Department
                  </label>
                  <Input
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className="h-9 text-xs"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">
                  Timezone
                </label>
                <Input
                  value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}
                  className="h-9 text-xs"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">
                  Curriculum Focus & Bio
                </label>
                <textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  rows={4}
                  className="w-full rounded-md border border-input bg-background p-2.5 text-xs text-foreground placeholder:text-muted-foreground focus-visible:outline-hidden focus-visible:ring-1 focus-visible:ring-primary leading-relaxed"
                />
              </div>
            </CardContent>
          </div>
        </Card>

        {/* RIGHT COLUMN: ASSIGNED ROLES & SCOPES */}
        <Card className="border-border/80 shadow-xs flex flex-col justify-between">
          <div>
            <CardHeader className="border-b border-border/40 pb-3.5">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-primary" />
                <CardTitle className="text-sm font-semibold">
                  Assigned Roles & Scopes
                </CardTitle>
              </div>
              <CardDescription className="text-xs">
                Platform capabilities authorized by your organization
                administrator.
              </CardDescription>
            </CardHeader>
            <CardContent className="p-5 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  {
                    name: "Asset Ingestion",
                    level: "Full Access",
                    desc: "Register, segment, and index video, audio, and slides",
                    icon: Layers,
                  },
                  {
                    name: "RAG Synthesis",
                    level: "Full Access",
                    desc: "Generate cross-modal insights with vector retrieval",
                    icon: Sparkles,
                  },
                  {
                    name: "Curriculum Review",
                    level: "Admin / Approve",
                    desc: "Curate, accept, reject, and publish recommendations",
                    icon: CheckCircle2,
                  },
                  {
                    name: "Vector Explorer",
                    level: "Read Only",
                    desc: "Inspect Qdrant embeddings and evidence chunks",
                    icon: Database,
                  },
                ].map((perm, idx) => {
                  const Icon = perm.icon;
                  return (
                    <div
                      key={idx}
                      className="p-3 rounded-lg border border-border/60 bg-muted/20 space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-foreground">
                          <Icon className="h-3.5 w-3.5 text-primary" />
                          <span className="truncate">{perm.name}</span>
                        </div>
                        <Badge
                          variant="secondary"
                          className="text-[10px] px-1.5 py-0 font-mono"
                        >
                          {perm.level}
                        </Badge>
                      </div>
                      <p className="text-[11px] text-muted-foreground leading-snug">
                        {perm.desc}
                      </p>
                    </div>
                  );
                })}
              </div>

              {/* ASSIGNED CURRICULUM COURSES */}
              <div className="pt-2 border-t border-border/40">
                <span className="text-xs font-semibold text-muted-foreground block mb-2">
                  Assigned Active Course Suites
                </span>
                <div className="flex flex-wrap gap-2">
                  {[
                    "Deep Learning & Optimization",
                    "Neural Networks: Backpropagation",
                    "Multimodal AI & Transformers in Production",
                    "CS101: Data Structures Telemetry",
                  ].map((course, i) => (
                    <div
                      key={i}
                      className="inline-flex items-center gap-1.5 rounded-md bg-muted/60 border border-border/50 px-2.5 py-1 text-xs text-foreground/90 font-medium"
                    >
                      <BookOpen className="h-3 w-3 text-primary" />
                      <span>{course}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* SECURITY SUMMARY */}
              <div className="pt-2 border-t border-border/40">
                <span className="text-xs font-semibold text-muted-foreground block mb-2">
                  Enterprise Security & Session
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center gap-2 p-2.5 rounded-md bg-muted/30 border border-border/40">
                    <Lock className="h-3.5 w-3.5 text-muted-foreground" />
                    <div>
                      <span className="text-foreground font-medium block text-[11px]">
                        2FA Enforced
                      </span>
                      <span className="text-muted-foreground text-[10px]">
                        Hardware / Authenticator
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 p-2.5 rounded-md bg-muted/30 border border-border/40">
                    <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
                    <div>
                      <span className="text-foreground font-medium block text-[11px]">
                        SSO Provider
                      </span>
                      <span className="text-muted-foreground text-[10px]">
                        Coursera Okta Identity
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </div>
        </Card>
      </div>
    </div>
  );
}
