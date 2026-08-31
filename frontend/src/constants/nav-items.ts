import type { NavItem } from "@/types";
import {
  LayoutDashboard,
  Lightbulb,
  ServerPlus,
  Sparkles,
} from "lucide-react";

// Navigation items for the sidebar
export const navMain: NavItem[] = [
  {
    title: "Dashboard",
    url: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Register",
    url: "/new-register",
    icon: ServerPlus,
  },
  {
    title: "Ask",
    url: "/chat",
    icon: Sparkles,
  },
  {
    title: "Recommendations",
    url: "/recommendations",
    icon: Lightbulb,
  },
];