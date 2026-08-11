import { createFilteredRowModel, columnFilteringFeature, globalFilteringFeature, columnVisibilityFeature, rowPaginationFeature, rowSelectionFeature, rowSortingFeature, createPaginatedRowModel, createSortedRowModel, filterFn_includesString, sortFn_alphanumeric, sortFn_text, tableFeatures } from "@tanstack/react-table";


export const features = tableFeatures({
    columnFilteringFeature,
    globalFilteringFeature,
    columnVisibilityFeature,
    rowPaginationFeature,
    rowSelectionFeature,
    rowSortingFeature,
    filteredRowModel: createFilteredRowModel(),
    paginatedRowModel: createPaginatedRowModel(),
    sortedRowModel: createSortedRowModel(),
    filterFns: {includeString: filterFn_includesString},
    sortFns: {alphanumeric: sortFn_alphanumeric, text: sortFn_text},
})

export type DataTableFeatures = typeof features;