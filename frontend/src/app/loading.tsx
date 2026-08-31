import React from "react";
import Loader from "@/components/ui/loader";

export default function Loading() {
  return (
    <main className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-background text-foreground px-4 selection:bg-primary/20 selection:text-primary">
      <Loader />
    </main>
  );
}
