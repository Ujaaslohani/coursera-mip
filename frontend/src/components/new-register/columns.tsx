"use client";

import { createColumnHelper } from "@tanstack/react-table";
import { type DataTableFeatures } from "@/constants/processing-table-features";
import { Processing } from "@/types";

// DEFINE THE SHAPE OF THE PROCESSING TABLE
const columnHelper = createColumnHelper<DataTableFeatures, Processing>()

export const columns = columnHelper.columns([
    columnHelper.accessor("mode", {
        header: 'Modality',
    }),
    columnHelper.accessor('topic', {
        header: 'Topic'
    }),
    columnHelper.accessor('stage', {
        header: 'Stage'
    }),
    columnHelper.accessor('assetId',{
        header: 'Asset Id'
    })
])


