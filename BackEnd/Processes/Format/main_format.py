from pathlib import Path
import re
import sys
import os



# Configuración de paths
def get_project_root():
    """Retorna el directorio raíz del proyecto"""
    return Path(__file__).parent.parent.absolute()

# Configurar paths
PROJECT_ROOT = get_project_root()
sys.path.append(str(PROJECT_ROOT))
PROJECT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_DIR))


from BackEnd.Database.Queries.Select.select_parameters import select_parameters
from Format.block_quality_copy import block_quality_copy
from Format.header_quality_format_copy import header_quality_format_copy
from Format.header_summary_format_copy import header_summary_format_copy
from Utils.filter_summary_data import filter_summary_data
from Write.write_quality_control import write_quality_control
from Utils.apply_font_to_worksheet import apply_font_to_worksheet

# Obtén la ruta absoluta al directorio raíz del proyecto
from Utils.group_parameters_by_sample_id import group_parameters_by_sample

from BackEnd.Database.Queries.Select.select_samples import select_samples
from BackEnd.Processes.Format.block_analytical_copy import block_analitic_copy
from BackEnd.Processes.Format.header_analytic_format_copy import header_analitic_format_copy
from BackEnd.Processes.Write.write_analytic_data import write_analitic_data



from openpyxl import load_workbook
from Read.excel_chain_data_reader import excel_chain_data_reader

from Format.lab_format_copy import lab_format_copy
from Write.write_lab_data import write_lab_data
from Format.header_format_copy import header_format_copy
from Write.write_header_data import write_header_data
from Read.excel_header_reader import excel_header_reader

from Utils.set_height_for_all_rows import set_height_for_all_rows
from Format.footer_format_copy import footer_format_copy



def main_format(ln_samples: int, ln_parameters: int) -> bool:
    
    file_path = "C:/Users/Duban Serrano/Downloads/FINAL-REPORT-SRLIMS (1)/FINAL-REPORT-SRLIMS/plantilla-reporte-final.xlsx"
    path_file_source = "C:/Users/Duban Serrano/Downloads/FINAL-REPORT-SRLIMS (1)/FINAL-REPORT-SRLIMS/SOURCE-FORMAT.xlsx"
    path_file_write = "C:/Users/Duban Serrano/Downloads/FINAL-REPORT-SRLIMS (1)/FINAL-REPORT-SRLIMS/Reporte.xlsx"
    
    
    wb_to_print= load_workbook(path_file_write)
    wb_to_read = load_workbook(filename=file_path, data_only=True)
    wb_to_format = load_workbook(path_file_source)
    
    
    # FIRST HEADER BLOCK
    
    last_row = header_format_copy(wb_to_format,wb_to_print,  wb_to_format["Header"], 1)  
    header_data = excel_header_reader(wb_to_read)  
    write_header_data(wb_to_print,header_data, 1)
    client_sample_id = header_data[6]
    
    
    # Lab data block
    lab_format_copy(wb_to_format, wb_to_print, wb_to_format["Header_lab"], last_row, 48) 
    #chain_data = excel_chain_data_reader(wb_to_read, file_path
    chain_data = select_samples(2504020, [], None, False)
    parameters_data = select_parameters(2504020, [])
    last_row=write_lab_data(wb_to_print, chain_data, last_row, client_sample_id)
    
    
    
    last_row_to_header = footer_format_copy(wb_to_format, wb_to_print, wb_to_format["Footer"], last_row)
    last_row = header_format_copy(wb_to_format,wb_to_print,  wb_to_format["Header"], last_row_to_header)
    write_header_data(wb_to_print,header_data, last_row_to_header)
    
    last_row_blocks = header_analitic_format_copy(wb_to_format, wb_to_print, wb_to_format["header_analitic"], last_row)
    
    times_to_print_blocks = len(chain_data)
    
    
    """print("***********************************")
    print(chain_data[:5])
    print(parameters_data[:5])"""
    
    samples, controls = group_parameters_by_sample(parameters_data)
    paremeters_per_block_samples = []
    samples_no_qc = []
    
    
    for sample, item in samples.items():
        
        
        
        samples_no_qc.append(sample)
        paremeters_per_block_samples.append(len(item))
        
        
    
    last_row = block_analitic_copy(wb_to_format, wb_to_print, wb_to_format["block_analitic"], last_row_blocks, len(samples_no_qc), paremeters_per_block_samples)
    
    
    #print("WRITE ANALITIC DATA")
    
    last_row = write_analitic_data(wb_to_format, wb_to_print, last_row_blocks, samples, last_row_blocks)
    last_row_blocks = header_summary_format_copy(wb_to_format, wb_to_print, wb_to_format["header_summary"], last_row )
    
    
    # Summary data 
    samples_summ = filter_summary_data(samples)
    samples_summ_no_qc = []
    parameters_per_summ = []
    
    for sample, item in samples_summ.items():
        
        samples_summ_no_qc.append(sample)
        parameters_per_summ.append(len(item))
        
    last_row = block_analitic_copy(wb_to_format, wb_to_print, wb_to_format["block_analitic"], last_row_blocks, len(samples_no_qc), parameters_per_summ)
    last_row = write_analitic_data(wb_to_format, wb_to_print, last_row_blocks,samples_summ, last_row_blocks)


    # Quality Controls
    last_row = header_quality_format_copy(wb_to_format, wb_to_print, wb_to_format["header_quality"], last_row)
    
    block_quality_copy(wb_to_format, wb_to_print, last_row -1, controls)
    
    
    def transform_data(input_data):
        """
        Transforma la estructura de datos original en el formato deseado.
        Extrae las primeras 6 posiciones de cada lista y sublista.
        
        Args:
            input_data (dict): Diccionario con la estructura original
            
        Returns:
            dict: Diccionario con la estructura transformada
        """
        result = {}
        
        for key, value in input_data.items():
            # Inicializar la lista para esta clave
            result[key] = []
            
            # Añadir las primeras 6 posiciones de la lista principal
            result[key].append(value[:15])
            
            # Buscar sublistas en cualquier posición de la lista principal
            for item in value:
                if isinstance(item, list):
                    # Añadir las primeras 6 posiciones de cada sublista
                    result[key].append(item[:15])
        #print(result)
        #eturn result

  

    controls_org = transform_data(controls)
    
    write_quality_control(controls_org, last_row-2, wb_to_print["Reporte"])
    
    
    #write_quality_control(controls)
    
    set_height_for_all_rows(wb_to_print["Reporte"], 60, 1, 5000)
    apply_font_to_worksheet(wb_to_print["Reporte"], "Calibri", 25)
    wb_to_print.save(path_file_write)
     
    return True

