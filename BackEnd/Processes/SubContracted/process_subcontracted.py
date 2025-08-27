from openpyxl import load_workbook

from BackEnd.Processes.Read import subcontracted_reader


def process_subcontracted(url_file: str) -> list:
    
    
    #Load the wb
    try:
        wb = load_workbook(filename=url_file)
        
        # Get the first sheet
        ws_to_read = wb.worksheets[0]
        
        
        registers_to_create = subcontracted_reader(ws_to_read)
        
        if len(registers_to_create) > 0 :
            
            return registers_to_create

        else:
            
            raise ValueError("No data in the excel ")
        
    
    except Exception as ex:

        raise Exception(f"File could not be open: {ex}") from ex
    
    finally:
        
        try:
            wb.close()
        except:
            pass    
    
