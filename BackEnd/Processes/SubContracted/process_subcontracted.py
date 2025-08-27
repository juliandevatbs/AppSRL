from openpyxl import load_workbook

from BackEnd.Processes.Read import subcontracted_reader


def process_subcontracted(url_file: str) -> bool:
    
    
    #Load the wb
    try:
        wb = load_workbook(filename=url_file)
        
        # Get the first sheet
        ws_to_read = wb.worksheets[0]
        
        
        subcontracted_reader(ws_to_read)
    
    except Exception as ex:
        print("File could not be open")
        return False
    
    
    return True