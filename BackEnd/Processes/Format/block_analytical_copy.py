

from BackEnd.Utils.copy_excel_range import copy_excel_range
from BackEnd.Utils.pagination import check_pagination_needed, pagination


def block_analitic_copy(source_wb, destiny_wb, source_sheet, last_row, times_to_print_block, times_each_block, WB_TO_FORMAT, WB_TO_READ):
    """
    Copies header blocks and analytic blocks with improved pagination logic
    """
    block_analitic_range = "A1:AQ4"  # Header block range (4 rows)
    analitic_block_range = "A5:AQ6"  # Analytic block range (2 rows)
         
    try:
        src_sheet = source_wb[source_sheet] if isinstance(source_sheet, str) else source_sheet
        dest_sheet = destiny_wb['Reporte']
                 
        current_row = last_row - 2
                 
        # Process each main block
        for i in range(times_to_print_block):
            internal_blocks = times_each_block[i] if i < len(times_each_block) else 0
            
            # Calcular total de filas necesarias para este bloque completo
            total_rows_needed = 4 + (internal_blocks * 1)  # header (4) + analytics (2 cada uno)
            
            # Verificar si todo el bloque cabe en la página actual
            if check_pagination_needed(current_row, total_rows_needed):
                current_row = pagination(destiny_wb, WB_TO_FORMAT, WB_TO_READ, current_row, total_rows_needed)
            
            # Copy the header block
            header_cell_dest = f"A{current_row}"
            #print(f"Writing header block {i+1} to {header_cell_dest} (needs {total_rows_needed} total rows)")
                         
            copy_excel_range(src_sheet, dest_sheet, block_analitic_range, header_cell_dest)
            current_row += 4
                         
            # Get the analytic block source sheet
            analytic_src_sheet = source_wb["block_analitic"]
                         
            # Copy each analytic block
            for j in range(internal_blocks):
                analytic_cell_dest = f"A{current_row}"
                #print(f"Writing analytic block {j+1} for main block {i+1} to {analytic_cell_dest}")
                                 
                copy_excel_range(analytic_src_sheet, dest_sheet, analitic_block_range, analytic_cell_dest)
                current_row += 1
                 
        return current_row
             
    except Exception as e:
        print(f"Error en block_analitic_copy: {str(e)}")
        return False