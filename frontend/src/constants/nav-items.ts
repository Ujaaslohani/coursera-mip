import type { NavItem } from "@/types";
import {
  LayoutDashboard,
  Lightbulb,
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