import datetime


def process_datetime(date_to_process):
    
    if(isinstance(date_to_process, datetime.datetime)):
        
        
        return date_to_process.strftime("%d/%m/%Y %H:%M")
    
    else :
        
        return date_to_process
    
    