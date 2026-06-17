import { cn } from "@/shared/utils/cn";

interface DataTableColumn<T> {
  header: string;
  accessor: keyof T | ((row: T) => React.ReactNode);
  sortable?: boolean;
  className?: string;
  headerClassName?: string;
}

interface DataTableProps<T> {
  columns: DataTableColumn<T>[];
  data: T[];
  isLoading?: boolean;
  emptyMessage?: string;
  onRowClick?: (row: T) => void;
  className?: string;
}

export function DataTable<T extends { id?: number | string }>({
  columns,
  data,
  isLoading = false,
  emptyMessage = "No data",
  onRowClick,
  className,
}: DataTableProps<T>) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-400">
        Loading...
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-500">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className={cn("overflow-x-auto", className)}>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-700">
            {columns.map((col, i) => (
              <th
                key={i}
                className={cn(
                  "text-left px-4 py-3 text-slate-400 font-medium text-xs uppercase tracking-wide",
                  col.sortable && "cursor-pointer hover:text-slate-200 select-none",
                  col.headerClassName,
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIdx) => (
            <tr
              key={row.id ?? rowIdx}
              onClick={() => onRowClick?.(row)}
              className={cn(
                "border-b border-slate-800 transition-colors",
                onRowClick && "cursor-pointer hover:bg-slate-800/50",
              )}
            >
              {columns.map((col, colIdx) => (
                <td
                  key={colIdx}
                  className={cn("px-4 py-3 text-slate-300", col.className)}
                >
                  {typeof col.accessor === "function"
                    ? col.accessor(row)
                    : String(row[col.accessor] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
