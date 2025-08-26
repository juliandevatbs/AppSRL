from datetime import datetime, timedelta

from Utils.get_excel import get_excel


def excel_chain_data_reader(wb_to_read, file_path: str):

    #This function receives the read data parameters, reads as needed and returns a list with the data

    try:
        ws_to_read = wb_to_read["Chain of Custody 1"]

    except Exception as e:

        print(f"Error getting the chain of custody, please verify: {e}")

    start_row = 15

    is_data = True

    columns_to_read = ["B", "AY", "C", "F", "G", "E", "D", "H"]
    columns_matrix_data = ["I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL", "AM", "AN", "AO", "AP", "AQ", "AR", "AS", "AT", "AU", "AV", "AW", "AX"]

    chain_data = []



    while is_data:

        row = []
        matrix_bool = []
        specific_data = []

        for column in columns_to_read:


            cell_spec = f"{column}{start_row}"
            cell_value = ws_to_read[cell_spec].value
            

            if cell_value != 'Shipment Method:':

                if column == 'D' :

                    cell_value = cell_value.strftime("%d-%m-%y")

                elif column == 'E':

                    if isinstance(cell_value, datetime):

                        cell_value  = cell_value.total_seconds()
                        hours = int(cell_value // 3600)
                        minutes = int(cell_value % 3600 // 60)
                        seconds = int(cell_value % 60)

                        cell_value = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

                    elif isinstance(cell_value, timedelta):
                        # If it's a timedelta, convert to HH:MM:SS
                        total_seconds = cell_value.total_seconds()
                        hours = int(total_seconds // 3600)
                        minutes = int((total_seconds % 3600) // 60)
                        seconds = int(total_seconds % 60)
                        cell_value = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                specific_data.append(cell_value)


            else:

                is_data = False
                break
        specific_data.insert(1, ws_to_read["BA3"].value)
        specific_data.insert(7, ws_to_read["B10"].value)
        
        row.append(specific_data)


        for column in columns_matrix_data:

            cell_spec = f"{column}{start_row}"
            cell_value = ws_to_read[cell_spec].value



            if cell_value == 1 or cell_value == '1':

                matrix_bool.append(ws_to_read[f"{column}12"].value)
                #print(f"{cell_spec} -> {cell_value} -> {ws_to_read[f"{column}12"].value}")


        start_row += 1


        row.append(matrix_bool)
        chain_data.append(row)

    #print(chain_data)

    return chain_data





    


























