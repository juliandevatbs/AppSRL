from openpyxl.utils import get_column_letter

def subcontracted_reader(ws_to_read) -> list:
    
    
    #Receive the worksheet with the subcontracted data to read
    
    registers_to_create = []
    
    columns_to_read =  [get_column_letter(i) for i in range(1, 38)]
    
    for row in range(1, 1000):
    
        register = []
        
        
        for col in columns_to_read:
        
            cell = f"{col}{row}"
            cell_to_read = ws_to_read[cell].value

            
            register.append(cell_to_read)
        
        registers_to_create.append(register)    
     
    
    return registers_to_create