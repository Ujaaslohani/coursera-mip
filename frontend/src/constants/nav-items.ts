import type { NavItem } from "@/types";
import {
  LayoutDashboard,
  Lightbulb,
  ScrollText,
  ServerPlus,
  Settings,
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
  {
    title: "Logs",
    url: "/logs",
    icon: ScrollText,
  },
  {
    title: "Operations",
    url: "/operations",
    icon: Settings,
  },
];