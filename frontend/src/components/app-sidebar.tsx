"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import Image from "next/image";
import logoExpanded from "@/assets/LOGO-UP.png";
import logoCollapsed from "@/assets/COLLAPSED-UP.png";
import { ChevronsUpDown } from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { navMain } from "@/constants/nav-items";

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const pathname = usePathname();

  return (
    <Sidebar
      collapsible="icon"
      className="border-r border-sidebar-border"
      {...props}
    >
      <SidebarHeader className="h-14 flex items-center justify-center px-4 border-b border-sidebar-border">
        <Link
          href="/dashboard"
          className="flex items-center justify-center w-full py-1"
        >
          {/* EXPANDED LOGO */}
          <div className="flex items-center justify-center w-full group-data-[collapsible=icon]:hidden">
            <Image
              src={logoExpanded}
              alt="Coursera MIP"
              height={24}
              className="h-6 w-auto object-contain mx-auto"
              priority
            />
          </div>

          {/* COLLAPSED ICON LOGO */}
          <div className="hidden group-data-[collapsible=icon]:flex items-center justify-center w-full">
            <Image
              src={logoCollapsed}
              alt="MIP"
              height={16}
              className="h-4 w-auto object-contain mx-auto"
              priority
            />
          </div>
        </Link>
      </SidebarHeader>

      {/* MAIN NAVIGATION */}
      <SidebarContent className="px-2 py-3">
        <SidebarGroup>
          <SidebarGroupLabel className="text-[11px] font-semibold text-muted-foreground/70 uppercase tracking-wider px-2 mb-1 group-data-[collapsible=icon]:hidden">
            Menu
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navMain.map((item) => {
                const isActive = pathname === item.url;
                return (
                  <SidebarMenuItem
                    key={item.title}
                    className="flex justify-center"
                  >
                    <SidebarMenuButton
                      render={<Link href={item.url} />}
                      isActive={isActive}
                      tooltip={item.title}
                      className={`h-9 rounded-md transition-colors font-medium text-sm group-data-[collapsible=icon]:justify-center ${
                        isActive
                          ? "bg-primary/10 text-primary font-semibold hover:bg-primary/15 dark:bg-sidebar-accent dark:text-sidebar-accent-foreground"
                          : "text-foreground font-medium hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                      }`}
                    >
                      <item.icon
                        className={`h-4 w-4 shrink-0 ${isActive ? "text-primary dark:text-sidebar-accent-foreground" : "text-foreground/80 group-hover/menu-button:text-sidebar-accent-foreground"}`}
                      />
                      <span className="flex-1 truncate group-data-[collapsible=icon]:hidden">
                        {item.title}
                      </span>
                      {item.badge && (
                        <span className="rounded-full bg-primary/15 px-2 py-0.5 text-[10px] font-bold text-primary group-data-[collapsible=icon]:hidden">
                          {item.badge}
                        </span>
                      )}
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      {/* PROFILE FOOTER */}
      <SidebarFooter className="border-t border-sidebar-border p-2">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              size="lg"
              className="w-full hover:bg-sidebar-accent hover:text-sidebar-accent-foreground rounded-lg transition-colors p-1.5 cursor-pointer"
            >
              <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground font-semibold text-xs shadow-xs">
                N
              </div>
              <div className="flex flex-col text-left text-xs leading-tight group-data-[collapsible=icon]:hidden truncate min-w-0 flex-1">
                <span className="font-semibold text-foreground truncate">
                  Navya
                </span>
                <span className="text-[11px] text-muted-foreground truncate">
                  navya@coursera.org
                </span>
              </div>
              <ChevronsUpDown className="ml-auto size-4 shrink-0 text-muted-foreground group-data-[collapsible=icon]:hidden" />
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
