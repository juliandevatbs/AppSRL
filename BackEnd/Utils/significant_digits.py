import math
import re

def significant_digits(number_input):
    """
    Formatea un número según estas reglas:
    - Mayor que 100: 3 cifras significativas
    - Entre 10 y 100: 3 cifras significativas
    - Entre 1 y 10: 3 cifras significativas
    - Menor que 1: 2 cifras significativas
    
    Maneja formatos como '3,5645' y '3,565456 U'
    
    Args:
        number_input (str o float): El número a formatear, puede incluir unidad
        
    Returns:
        float: El número formateado como valor flotante, sin unidades, para inserción en SQL
        str: La unidad original si estaba presente (o None si no había unidad)
    """
    # Convertir a string para manipulación
    input_str = str(number_input).strip()
    
    # Inicializar unidad como None
    unit = None
    
    # Verificar si hay un espacio que podría indicar una unidad
    parts = input_str.split(' ', 1)
    if len(parts) > 1:
        input_str = parts[0]
        unit = parts[1]
    
    # Reemplazar comas por puntos para el formato decimal
    input_str = input_str.replace(',', '.')
    
    # Intentar extraer solo la parte numérica usando expresiones regulares 
    # (por si hay caracteres no numéricos mezclados)
    numeric_match = re.match(r'^(-?\d*\.?\d+)', input_str)
    if numeric_match:
        input_str = numeric_match.group(1)
    
    try:
        number = float(input_str)
    except ValueError:
        #print(f"Error: No se puede convertir '{input_str}' a número")
        return None, None  # Devuelve None si no se puede procesar
    
    #print(f"NUMERO PARA CONVERTIR: {number}")
    
    # Evitar error con logaritmo de cero
    if number == 0:
        return 0.0, unit
    
    # Usar el valor absoluto para los cálculos logarítmicos
    abs_number = abs(number)
    
    if abs_number == 0:
        return 0.0
    
    # Definir un umbral mínimo para evitar redondeo a cero
    MINIMUM_VALUE = 1e-10  # Ajusta este valor según tus necesidades
    
    if abs_number > 100:
        precision = -int(math.floor(math.log10(abs_number))) + 2
        formatted_number = round(number, precision if precision >= 0 else 0)
    elif 10 <= abs_number <= 100:
        formatted_number = round(number, 1)
    elif 1 <= abs_number < 10:
        formatted_number = round(number, 2)
    elif abs_number >= MINIMUM_VALUE:  # Números pequeños pero significativos
        decimal_places = -int(math.floor(math.log10(abs_number))) + 1
        formatted_number = round(number, decimal_places)
    else:  # Números extremadamente pequeños
        # Opción 1: Devolver el número original sin redondear
        # return float(number)
        
        # Opción 2: Usar notación científica
        return float(f"{number:.2e}")
    
    return float(formatted_number)

