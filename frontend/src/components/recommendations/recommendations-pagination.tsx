"use client";

import React from "react";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationPrevious,
  PaginationNext,
} from "@/components/ui/pagination";

interface RecommendationsPaginationProps {
  page: number;
  pageSize: number;
  totalOnPage: number;
  hasPrevPage: boolean;
  hasNextPage: boolean;
  isLoading?: boolean;
  searchQuery?: string;
  onPageChange: (page: number) => void;
}

export function RecommendationsPagination({
  page,
  pageSize,
  totalOnPage,
  hasPrevPage,
  hasNextPage,
  isLoading = false,
  searchQuery = "",
  onPageChange,
}: RecommendationsPaginationProps) {
  // Only visible when not actively searching and there are items or a previous page
  if (searchQuery.trim() || (totalOnPage === 0 && !hasPrevPage)) {
    return null;
  }

  const firstItem = page * pageSize + 1;
  const lastItem = page * pageSize + totalOnPage;

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-border text-xs text-muted-foreground">
      <span className="font-medium">
        {totalOnPage > 0
          ? `Showing ${firstItem}–${lastItem}`
          : "No results"}
      </span>

      <Pagination className="w-auto mx-0">
        <PaginationContent className="gap-2">
          <PaginationItem>
            <PaginationPrevious
              variant="default"
              onClick={() => hasPrevPage && !isLoading && onPageChange(page - 1)}
              aria-disabled={!hasPrevPage || isLoading}
              className={
                !hasPrevPage || isLoading
                  ? "pointer-events-none opacity-40 bg-primary text-primary-foreground font-medium px-3.5 py-1.5 h-8 rounded-lg shadow-xs"
                  : "cursor-pointer bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground font-medium px-3.5 py-1.5 h-8 rounded-lg shadow-xs transition-all active:scale-95"
              }
            />
          </PaginationItem>

          <PaginationItem>
            <span className="px-3 py-1.5 text-xs font-semibold text-foreground bg-muted/60 rounded-md border border-border/60 min-w-[70px] text-center inline-block">
              Page {page + 1}
            </span>
          </PaginationItem>

          <PaginationItem>
            <PaginationNext
              variant="default"
              onClick={() => hasNextPage && !isLoading && onPageChange(page + 1)}
              aria-disabled={!hasNextPage || isLoading}
              className={
                !hasNextPage || isLoading
                  ? "pointer-events-none opacity-40 bg-primary text-primary-foreground font-medium px-3.5 py-1.5 h-8 rounded-lg shadow-xs"
                  : "cursor-pointer bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground font-medium px-3.5 py-1.5 h-8 rounded-lg shadow-xs transition-all active:scale-95"
              }
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
}
