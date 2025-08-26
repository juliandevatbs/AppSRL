
from BackEnd.Processes.Format.footer_for_all import footer_for_all
from BackEnd.Processes.Format.header_format_copy import header_format_copy
from BackEnd.Processes.Read.excel_header_reader import excel_header_reader
from BackEnd.Processes.Write.write_header_data import write_header_data


_ROWS_PER_PAGE_CACHE = {}

def get_dynamic_rows_per_page(WB_TO_PRINT, current_row: int = 1) -> int:
    """
    Calcula dinámicamente las filas por página basándose en alturas reales
    """
    worksheet = WB_TO_PRINT.active
    cache_key = id(worksheet)
    
    if cache_key in _ROWS_PER_PAGE_CACHE:
        return _ROWS_PER_PAGE_CACHE[cache_key]
    
    try:
        total_height = 0
        rows_measured = 0
        
        for row_num in range(max(1, current_row), min(current_row + 20, worksheet.max_row + 1)):
            row_dimension = worksheet.row_dimensions.get(row_num)
            if row_dimension and row_dimension.height:
                height = row_dimension.height
            else:
                height = 15
            
            total_height += height
            rows_measured += 1
            
        if rows_measured == 0:
            rows_per_page = 79
        else:
            avg_height = total_height / rows_measured
            rows_per_page = int(720 / avg_height)
            
            if rows_per_page < 50 or rows_per_page > 100:
                rows_per_page = 79
        
        _ROWS_PER_PAGE_CACHE[cache_key] = rows_per_page
        return rows_per_page
        
    except Exception as e:
        print(f"❌ Error calculando filas por página: {e}")
        return 79

def pagination(WB_TO_PRINT, WB_TO_FORMAT, WB_TO_READ, row: int, rows_needed: int = 1):
    """
    FOOTER: 2 líneas ANTES del salto de página
    HEADER: 1 línea DESPUÉS del salto de página
    """
    
    
    # Obtener filas por página dinámicamente
    ROWS_PER_PAGE = get_dynamic_rows_per_page(WB_TO_PRINT, row)
    
    # Si es la primera escritura (row == 2), agregar encabezado inicial
    if row == 2:
        print("Adding initial header at row 2")
        last_row = header_format_copy(WB_TO_FORMAT, WB_TO_PRINT, WB_TO_FORMAT["Header"], row)
        header_data = excel_header_reader(WB_TO_READ)
        write_header_data(WB_TO_PRINT, header_data, 1)
        print(f"Initial header ended at row {last_row}")
        return last_row + 3
    
    # Calcular información de página actual
    current_page, page_start, page_end = get_page_info(row, ROWS_PER_PAGE)
    """print(f"Current page: {current_page}, page range: {page_start}-{page_end}")
    print(f"Available space in current page: {page_end - row + 1} rows")"""
    
    # CALCULAR ESPACIO NECESARIO INCLUYENDO FOOTER
    # Footer necesita espacio + 2 líneas antes del salto
    footer_height = 2 # Necesitamos saber cuántas filas ocupa el footer
    space_needed_with_footer = rows_needed + footer_height + 1
    
    """print(f"Footer height: {footer_height} rows")
    print(f"Total space needed (content + footer + 2): {space_needed_with_footer}")"""
    
    # Verificar si TODO cabe (contenido + footer + 2 líneas)
    if row + space_needed_with_footer - 1 <= page_end:
        print("✅ Block + footer fits in current page, no pagination needed")
        return row
    
    # NO CABE: Necesitamos paginación
    #print("❌ Not enough space, pagination needed")
    
    # FOOTER: 2 líneas ANTES del final de página
    footer_start_row = page_end - footer_height - 2  # -1 para tener 2 líneas antes del salto
    #print(f"🦶 Placing footer at row {footer_start_row} (2 lines before page end {page_end})")
    
    # Copiar footer
    
    last_row_after_footer = footer_for_all(WB_TO_FORMAT, WB_TO_PRINT, WB_TO_FORMAT["footer__all"], footer_start_row  +1)
    #print(f"Footer ended at row {last_row_after_footer}")
    
    # SALTO DE PÁGINA (automático en page_end + 1)
    next_page_start = page_end + 1
    #print(f"📄 Page break at row {page_end}, next page starts at {next_page_start}")
    
    # HEADER: 1 línea DESPUÉS del salto de página
    header_start_row = next_page_start + 1
    #print(f"🗂️ Placing header at row {header_start_row} (1 line after page start)")
    
    # Copiar header
    last_row_after_header = header_format_copy(WB_TO_FORMAT, WB_TO_PRINT, WB_TO_FORMAT["Header"], header_start_row)
    #print(f"Header ended at row {last_row_after_header}")
    
    # Escribir datos del encabezado
    header_data = excel_header_reader(WB_TO_READ)
    write_header_data(WB_TO_PRINT, header_data, 1)
    
    # Retornar la primera fila disponible después del header
    next_row = last_row_after_header + 1
    #print(f"✅ Next available row for content: {next_row}")
    #print(f"=== END PAGINATION DEBUG ===\n")
    
    return next_row

def get_footer_height(WB_TO_FORMAT) -> int:
    """
    Calcula cuántas filas ocupa el footer
    """
    try:
        footer_sheet = WB_TO_FORMAT["Footer"]
        # Contar filas con contenido en el footer
        footer_height = 0
        for row in footer_sheet.iter_rows():
            if any(cell.value is not None for cell in row):
                footer_height += 1
        
        return max(footer_height, 1)  # Mínimo 1 fila
    except:
        return 3  # Valor por defecto si no se puede calcular

def get_page_info(row: int, rows_per_page: int = None) -> tuple[int, int, int]:
    """
    Obtiene información sobre la página actual
    """
    if rows_per_page is None:
        rows_per_page = 79
    
    current_page = ((row - 1) // rows_per_page) + 1
    page_start = ((current_page - 1) * rows_per_page) + 1
    page_end = current_page * rows_per_page
    
    return current_page, page_start, page_end

def check_pagination_needed(current_row: int, rows_needed: int, WB_TO_PRINT=None, WB_TO_FORMAT=None) -> tuple[bool, int, int]:
    """
    Verifica si se necesita paginación considerando el footer
    """
    if WB_TO_PRINT:
        rows_per_page = get_dynamic_rows_per_page(WB_TO_PRINT, current_row)
    else:
        rows_per_page = 79
    
    current_page, page_start, page_end = get_page_info(current_row, rows_per_page)
    
    # Calcular espacio necesario incluyendo footer
    if WB_TO_FORMAT:
        footer_height = get_footer_height(WB_TO_FORMAT)
        space_needed = rows_needed + footer_height + 2  # +2 líneas antes del salto
    else:
        space_needed = rows_needed + 5  # Estimación conservadora
    
    available_rows = page_end - current_row + 1
    needs_pagination = space_needed > available_rows
    
    return needs_pagination, page_end, available_rows

def get_next_page_start(current_row: int, WB_TO_PRINT=None) -> int:
    """
    Obtiene la primera fila de la siguiente página
    """
    if WB_TO_PRINT:
        rows_per_page = get_dynamic_rows_per_page(WB_TO_PRINT, current_row)
    else:
        rows_per_page = 79
        
    current_page, _, page_end = get_page_info(current_row, rows_per_page)
    return page_end + 1

def reset_pagination_cache():
    """
    Limpia el cache de filas por página
    """
    global _ROWS_PER_PAGE_CACHE
    _ROWS_PER_PAGE_CACHE.clear()
    #print("🔄 Cache de paginación limpiado")

def diagnose_pagination(WB_TO_PRINT, WB_TO_FORMAT=None, start_row: int = 1):
    """
    Función de diagnóstico completa
    """
    #print(f"\n🔬 DIAGNÓSTICO DE PAGINACIÓN")
    #print(f"=" * 60)
    
    # Filas por página
    rows_per_page = get_dynamic_rows_per_page(WB_TO_PRINT, start_row)
    #print(f"📄 Filas por página: {rows_per_page}")
    
    # Altura del footer
    if WB_TO_FORMAT:
        footer_height = get_footer_height(WB_TO_FORMAT)
        #print(f"🦶 Altura del footer: {footer_height} filas")
    
    # Información de página actual
    current_page, page_start, page_end = get_page_info(start_row, rows_per_page)
    #print(f"📍 Página actual: {current_page}")
    #print(f"📍 Rango de página: {page_start} - {page_end}")
    
    # Posiciones calculadas
    if WB_TO_FORMAT:
        footer_start = page_end - footer_height - 1
        header_start = page_end + 2
        #print(f"🦶 Footer se colocaría en: {footer_start}")
        #print(f"🗂️ Header se colocaría en: {header_start}")
    
    #print(f"=" * 60)