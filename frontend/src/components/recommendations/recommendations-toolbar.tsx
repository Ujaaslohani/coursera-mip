"use client";

import React from "react";
import { SearchInput } from "@/components/ui/search-input";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { Spinner } from "@/components/ui/spinner";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationPrevious,
  PaginationNext,
} from "@/components/ui/pagination";

interface RecommendationsToolbarProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  onRefresh: () => void;
  isLoading: boolean;
  // PAGINATION
  page: number;
  pageSize: number;
  totalOnPage: number;
  hasPrevPage: boolean;
  hasNextPage: boolean;
  onPageChange: (page: number) => void;
}

export function RecommendationsToolbar({
  searchQuery,
  onSearchChange,
  onRefresh,
  isLoading,
  page,
  pageSize,
  totalOnPage,
  hasPrevPage,
  hasNextPage,
  onPageChange,
}: RecommendationsToolbarProps) {
  const firstItem = page * pageSize + 1;
  const lastItem = page * pageSize + totalOnPage;

  return (
    <div className="flex flex-col gap-3">
      {/* SEARCH + REFRESH ROW */}
      <div className="flex items-center gap-2 w-full bg-card">
        <SearchInput
          placeholder="Search recommendations..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          showClear
          onClear={() => onSearchChange("")}
          className="h-9 text-sm"
        />
        <Button
          onClick={onRefresh}
          disabled={isLoading}
          className="h-9 gap-1.5 px-4 shrink-0 cursor-pointer"
        >
          {isLoading ? (
            <Spinner className="h-4 w-4 text-muted-foreground" />
          ) : (
            <RefreshCw className="h-4 w-4" />
          )}
          {isLoading ? "Loading..." : "Refresh"}
        </Button>
      </div>

      {/* PAGINATION ROW — ONLY VISIBLE WHEN NOT ACTIVELY SEARCHING */}
      {!searchQuery.trim() && (totalOnPage > 0 || hasPrevPage) && (
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>
            {totalOnPage > 0
              ? `Showing ${firstItem}–${lastItem}`
              : "No results"}
          </span>

          <Pagination className="w-auto mx-0">
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious
                  onClick={() => hasPrevPage && onPageChange(page - 1)}
                  aria-disabled={!hasPrevPage || isLoading}
                  className={
                    !hasPrevPage || isLoading
                      ? "pointer-events-none opacity-40"
                      : "cursor-pointer"
                  }
                />
              </PaginationItem>

              <PaginationItem>
                <span className="px-3 py-1.5 text-xs font-medium">
                  Page {page + 1}
                </span>
              </PaginationItem>

              <PaginationItem>
                <PaginationNext
                  onClick={() => hasNextPage && onPageChange(page + 1)}
                  aria-disabled={!hasNextPage || isLoading}
                  className={
                    !hasNextPage || isLoading
                      ? "pointer-events-none opacity-40"
                      : "cursor-pointer"
                  }
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      )}
    </div>
  );
}
