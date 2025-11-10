def data_formatter(data_to_format: list | tuple, keys) -> dict | list[dict]:


    """
        Receives the data to sort and a list of keys ,
        that is, the names for the keys of the dictionary
        to return in the order in which the unsorted data
        comes

    """



    equal_len = len(data_to_format[0]) == len(keys)




    if isinstance(data_to_format, (list, tuple)) and equal_len:

        if (len(data_to_format) == 1):

            formatted_data = {'☐': '☐'}

            for index, key in enumerate(keys):

                formatted_data[key] = data_to_format[0][index]

            return formatted_data

        else:

            formatted_data_list = []

            for row in data_to_format:

                row_dict = {'☐': '☐'}

                for index, key in enumerate(keys):

                    row_dict[key] = row[index]

                formatted_data_list.append(row_dict)

                print(row_dict)
            return formatted_data_list


    else:

        print("Error en formatter")

        return {}



def tuple_to_readable(data: list):

    final_data = []

    for item in data:

        final_data.append(item[0])

    return final_data









