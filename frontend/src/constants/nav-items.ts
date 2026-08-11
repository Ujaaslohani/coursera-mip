import type { NavItem } from "@/types";
import {
  LayoutDashboard,
  MessageSquarePlus,
  ServerPlus,
  Settings,
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
    title: "Operations",
    url: "/operations",
    icon: Settings,
  },
];