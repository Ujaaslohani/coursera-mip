import { DataTableFeatures } from "@/constants/processing-table-features";
import { type ColumnDef, type RowData } from "@tanstack/react-table";
import type { ComponentType } from "react";

// INTERFACE FOR THE NAVIGATIONS 
export interface NavItem {
  title: string;
  url: string;
  icon: ComponentType<{ className?: string }>;
  badge?: string;
}


// TYPE AND INTERFACE FOR PROCESSING TABLE
export type Processing = {
    mode: string
    topic: string
    owner: string
    stage: string
    assetId: string
}

export interface DataTableProps<TData extends RowData> {
  columns: ColumnDef<DataTableFeatures, TData>[]
  data: TData[]
}
