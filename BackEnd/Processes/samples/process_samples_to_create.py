from datetime import datetime


def process_samples_to_create(data_to_process: list[dict]) -> list[dict]:
    """
    Procesa y valida los datos de las muestras antes de insertar
    
    Args:
        data_to_process: Lista de diccionarios con datos crudos
        
    Returns:
        list[dict]: Lista de diccionarios procesados y listos para insertar
    """
    processed_samples = []
    
    for sample in data_to_process:
        try:
            # Procesar fecha y hora
            date_collected = process_date_time(sample.get('DateCollected'))
            
            # Crear diccionario procesado
            processed_sample = {
                'ItemID': sample.get('ItemID'),
                'LabSampleID': sample.get('LabSampleID'),
                'ClientSampleID': sample.get('ClientSampleID', ''),
                'CollectMethod': sample.get('CollectMethod', ''),
                'CollectionAgency': sample.get('CollectionAgency', ''),
                'MatrixID': sample.get('MatrixID', ''),
                'Sampler': sample.get('Sampler', ''),
                'DateCollected': date_collected,
                'ResultComments': sample.get('ResultComments'),
                'ShippingBatchID': sample.get('ShippingBatchID'),
                'CoolerNumber': sample.get('CoolerNumber'),
                'Temperature': sample.get('Temperature'),
                'AdaptMatrixID': sample.get('AdaptMatrixID'),
                'TotalContainers': sample.get('TotalContainers'),
                'LabID': sample.get('LabID', '1-001'),
                'LabReportingBatchID': sample.get('LabReportingBatchID')
            }
            
            processed_samples.append(processed_sample)
            
        except Exception as e:
            print(f"Error processing sample {sample.get('LabSampleID')}: {e}")
            continue
    
    return processed_samples


def process_date_time(date_value) -> datetime:
    """
    Procesa diferentes formatos de fecha y los convierte a datetime
    
    Args:
        date_value: Fecha en string o datetime
        
    Returns:
        datetime: Objeto datetime procesado
    """
    if isinstance(date_value, datetime):
        return date_value
    
    if not isinstance(date_value, str):
        return datetime.now()
    
    # Formatos soportados
    formats = [
        "%m/%d/%y %H:%M",      # 09/24/25 13:31
        "%Y-%m-%d %H:%M:%S",   # 2025-09-24 13:31:00
        "%m/%d/%Y %H:%M",      # 09/24/2025 13:31
        "%Y-%m-%d",            # 2025-09-24
        "%m/%d/%y",            # 09/24/25
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_value, fmt)
        except ValueError:
            continue
    
    # Si ningún formato funciona, retornar fecha actual
    print(f"Warning: Could not parse date '{date_value}', using current date")
    return datetime.now()