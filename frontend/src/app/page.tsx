import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";

const TEAMS = [
  { role: "RAG Pipeline", members: "Kshitij, Pranav, Aditya" },
  { role: "Database Pipeline", members: "Pranay, Mukul" },
  { role: "Backend", members: "Ujaas, Ajay" },
  { role: "Frontend", members: "Tushar" },
  { role: "Testing & Deployment", members: "Kavya, Tushar" },
];

export default function HomePage() {
  return (
    <main className="h-screen w-full flex flex-col justify-between p-8 sm:p-12 md:p-16 lg:p-20 bg-background text-foreground">
      {/* MINIMAL TOP BAR */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
          Project Presentation
        </span>
        <ThemeToggle />
      </div>

      {/* MAIN TITLE & TEAM RESPONSIBILITIES */}
      <div className="my-auto max-w-3xl w-full space-y-10">
        <h1 className="text-3xl sm:text-5xl md:text-6xl font-bold font-heading tracking-tight text-foreground leading-[1.1]">
          Coursera: Multimodal Intelligence Platform
        </h1>

        <div className="space-y-4">
          {TEAMS.map((item) => (
            <div
              key={item.role}
              className="flex flex-col sm:flex-row sm:items-center justify-between py-3 border-b border-border/60 text-sm sm:text-base gap-1"
            >
              <span className="text-muted-foreground font-medium">
                {item.role}
              </span>
              <span className="text-foreground font-semibold sm:text-right">
                {item.members}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* MINIMAL BOTTOM LINK */}
      <div className="flex items-center justify-between text-xs text-muted-foreground pt-6">
        <span>2026</span>
        <Link
          href="/login"
          className="hover:text-foreground transition-colors underline underline-offset-4 font-medium"
        >
          Enter Platform →
        </Link>
      </div>
    </main>
  );
}
