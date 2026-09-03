import type { NavItem } from "@/types";
import {
  LayoutDashboard,
  Lightbulb,
  Sparkles,
} from "lucide-react";

// NAVIGATION ITEMS FOR THE SIDEBAR
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