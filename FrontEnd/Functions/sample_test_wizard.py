from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from BackEnd.Database.Queries.Insert.insert_sample_tests import insert_sample_tests
from BackEnd.Database.Queries.Wizard import select_data_to_c_sample_tests




def get_project_root():
    return Path(__file__).parent.parent.absolute()

PROJECT_ROOT = get_project_root()
sys.path.insert(0, str(PROJECT_ROOT))  
PROJECT_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_DIR))

# Importar tu función de inserción (ajusta la ruta según tu estructura)
# from Db.wizard.insert.insert_sample_tests import insert_sample_tests

class SampleTestsWizard:
    
    def __init__(self, parent=None):
        
        BASE_DIR = Path(__file__).parent.resolve()
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Sample Tests Creation Wizard")
        self.window.geometry("800x600")  
        self.window.resizable(False, False)
        # self.window.iconbitmap(BASE_DIR / "assets" / "logos" / "LOGO_SRL_FINAL.ico")
        
        # Variables para los campos
        self.sample_test_id_var = tk.StringVar()
        self.lab_reporting_batch_id_var = tk.StringVar()
        self.lab_sample_id_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.analyte_name_var = tk.StringVar()
        self.result_var = tk.StringVar()
        self.error_var = tk.StringVar()
        self.result_units_var = tk.StringVar()
        self.lab_qualifiers_var = tk.StringVar()
        self.detection_limit_var = tk.StringVar()
        self.analyte_type_var = tk.StringVar()
        self.dilution_var = tk.StringVar()
        self.percent_moisture_var = tk.StringVar()
        self.percent_recovery_var = tk.StringVar()
        self.relative_percent_difference_var = tk.StringVar()
        self.reporting_limit_var = tk.StringVar()
        self.matrix_id_var = tk.StringVar()
        
        self.lab_reporting_batch_ids = []
        self.lab_sample_ids = []
        self.analyte_names = ["Arsenic", "Lead", "Mercury", "Cadmium", "Chromium", "Copper", "Zinc", "Iron", "Manganese"]
        self.result_units = ["mg/L", "μg/L", "mg/kg", "μg/kg", "ppm", "ppb", "%", "NTU"]
        self.analyte_types = ["Metal", "Organic", "Inorganic", "Biological", "Physical", "Chemical"]
        self.matrix_ids = ["Water", "Soil", "Sediment", "Tissue", "Air", "Food", "Other"]
        
        # Datos internos
        self.last_sample_test_id = None
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="Create New Sample Tests", 
                               font=("Century Gothic", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Sample Test ID (solo lectura)
        ttk.Label(main_frame, text="Sample Test ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sample_test_id_label = ttk.Label(main_frame, text="Loading...", 
                                            font=("Century Gothic", 10, "bold"),
                                            background="lightgray", relief="sunken", width=20)
        self.sample_test_id_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Lab Reporting Batch ID
        ttk.Label(main_frame, text="Lab Reporting Batch ID:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.lab_reporting_batch_combo = ttk.Combobox(main_frame, textvariable=self.lab_reporting_batch_id_var,
                                                     state="readonly", width=37)
        self.lab_reporting_batch_combo.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        self.lab_reporting_batch_combo.bind('<<ComboboxSelected>>', self.on_batch_id_selected)
        
        # Lab Sample ID
        ttk.Label(main_frame, text="Lab Sample ID:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.lab_sample_id_combo = ttk.Combobox(main_frame, textvariable=self.lab_sample_id_var,
                                               state="readonly", width=37)
        self.lab_sample_id_combo.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Quantity
        ttk.Label(main_frame, text="Number of Tests:").grid(row=4, column=0, sticky=tk.W, pady=5)
        quantity_frame = ttk.Frame(main_frame)
        quantity_frame.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        self.quantity_entry = ttk.Entry(quantity_frame, textvariable=self.quantity_var, width=10)
        self.quantity_entry.grid(row=0, column=0)
        
        ttk.Label(quantity_frame, text="tests").grid(row=0, column=1, padx=(5, 0))
        
        # Botones de cantidad rápida
        quick_frame = ttk.Frame(quantity_frame)
        quick_frame.grid(row=0, column=2, padx=(10, 0))
        
        ttk.Button(quick_frame, text="1", command=lambda: self.quantity_var.set("1"), 
                  width=3).grid(row=0, column=0, padx=2)
        ttk.Button(quick_frame, text="5", command=lambda: self.quantity_var.set("5"), 
                  width=3).grid(row=0, column=1, padx=2)
        ttk.Button(quick_frame, text="10", command=lambda: self.quantity_var.set("10"), 
                  width=3).grid(row=0, column=2, padx=2)
        
        # Analyte Name (editable combobox)
        ttk.Label(main_frame, text="Analyte Name:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.analyte_name_combo = ttk.Combobox(main_frame, textvariable=self.analyte_name_var, width=37)
        self.analyte_name_combo.grid(row=5, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Result
        ttk.Label(main_frame, text="Result:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.result_entry = ttk.Entry(main_frame, textvariable=self.result_var, width=40)
        self.result_entry.grid(row=6, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Error
        ttk.Label(main_frame, text="Error:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.error_entry = ttk.Entry(main_frame, textvariable=self.error_var, width=40)
        self.error_entry.grid(row=7, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Result Units (editable combobox)
        ttk.Label(main_frame, text="Result Units:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.result_units_combo = ttk.Combobox(main_frame, textvariable=self.result_units_var, width=37)
        self.result_units_combo.grid(row=8, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Lab Qualifiers
        ttk.Label(main_frame, text="Lab Qualifiers:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.lab_qualifiers_combo = ttk.Combobox(main_frame, textvariable=self.lab_qualifiers_var, width=37)
        self.lab_qualifiers_combo.grid(row=9, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Detection Limit
        ttk.Label(main_frame, text="Detection Limit:").grid(row=10, column=0, sticky=tk.W, pady=5)
        self.detection_limit_entry = ttk.Entry(main_frame, textvariable=self.detection_limit_var, width=40)
        self.detection_limit_entry.grid(row=10, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # COLUMNA DERECHA
        
        # Analyte Type (editable combobox)
        ttk.Label(main_frame, text="Analyte Type:").grid(row=2, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.analyte_type_combo = ttk.Combobox(main_frame, textvariable=self.analyte_type_var, width=20)
        self.analyte_type_combo.grid(row=2, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Matrix ID (editable combobox)
        ttk.Label(main_frame, text="Matrix ID:").grid(row=3, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.matrix_id_combo = ttk.Combobox(main_frame, textvariable=self.matrix_id_var, width=20)
        self.matrix_id_combo.grid(row=3, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Dilution
        ttk.Label(main_frame, text="Dilution:").grid(row=4, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.dilution_entry = ttk.Entry(main_frame, textvariable=self.dilution_var, width=23)
        self.dilution_entry.grid(row=4, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Percent Moisture
        ttk.Label(main_frame, text="Percent Moisture:").grid(row=5, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.percent_moisture_entry = ttk.Entry(main_frame, textvariable=self.percent_moisture_var, width=23)
        self.percent_moisture_entry.grid(row=5, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Percent Recovery
        ttk.Label(main_frame, text="Percent Recovery:").grid(row=6, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.percent_recovery_entry = ttk.Entry(main_frame, textvariable=self.percent_recovery_var, width=23)
        self.percent_recovery_entry.grid(row=6, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Relative Percent Difference
        ttk.Label(main_frame, text="Relative % Difference:").grid(row=7, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.relative_percent_difference_entry = ttk.Entry(main_frame, textvariable=self.relative_percent_difference_var, width=23)
        self.relative_percent_difference_entry.grid(row=7, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Reporting Limit
        ttk.Label(main_frame, text="Reporting Limit:").grid(row=8, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.reporting_limit_entry = ttk.Entry(main_frame, textvariable=self.reporting_limit_var, width=23)
        self.reporting_limit_entry.grid(row=8, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=11, column=0, columnspan=4, pady=20)
        
        ttk.Button(button_frame, text="Create Tests", command=self.create_sample_tests,
                  width=15, cursor="hand2").grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form,
                  width=15, cursor="hand2").grid(row=0, column=1, padx=(10, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel,
                  width=15, cursor="hand2").grid(row=0, column=2, padx=(10, 0))

        # Configurar el grid
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(3, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
    def load_data(self):
        """Carga los datos desde la base de datos"""
        try:
            # Mostrar mensaje de carga
            self.sample_test_id_label.config(text="Loading data...")
            self.window.update()
            
            self.data = select_data_to_c_sample_tests.execute_all_sc_optimized(None)
            
            
            
           
            
            self.last_sample_test_id = self.data['last_sample_tests'] 
            self.lab_reporting_batch_ids = self.data['batchs_id']
            self.analyte_names = self.data['analyte_names']
            self.result_units = self.data['result_units']
            self.lab_qualifiers = self.data['lab_qualifiers']
            self.analyte_types = self.data['analyte_types']
            
            
            # Actualizar UI
            self.update_comboboxes()
            
            # Mostrar Sample Test ID
            next_id = (self.last_sample_test_id + 1) if self.last_sample_test_id else 1
            self.sample_test_id_label.config(text=str(next_id))
            
            
            
            # Establecer cantidad por defecto
            self.quantity_var.set("1")
            
            
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading data: {str(e)}")
            self.sample_test_id_label.config(text="Error loading")
    
    
    def get_lab_sample_ids_for_batch(self, batch_id):
        """Obtiene los Lab Sample IDs para un Batch ID específico usando la función unificada"""
        try:
            # Usar la función unificada para obtener lab samples del batch específico
            batch_data = select_data_to_c_sample_tests.execute_all_sc_optimized(batch_id)
            return batch_data['lab_samples']
        except Exception as e:
            print(f"Error getting lab samples for batch {batch_id}: {e}")
            messagebox.showerror("Error", f"Error loading lab samples: {str(e)}")
            return []
    
    def update_comboboxes(self):
        # Comboboxes principales
        self.lab_reporting_batch_combo['values'] = self.lab_reporting_batch_ids
        
        # Comboboxes editables con opciones predefinidas
        self.analyte_name_combo['values'] = self.analyte_names
        self.result_units_combo['values'] = self.result_units
        self.analyte_type_combo['values'] = self.analyte_types
        self.matrix_id_combo['values'] = self.matrix_ids
        self.lab_qualifiers_combo['values'] = self.lab_qualifiers
        self.analyte_type_combo['values'] = self.analyte_types
        
    def on_batch_id_selected(self, event=None):
        """Maneja la selección de un Lab Reporting Batch ID"""
        selected_batch = self.lab_reporting_batch_id_var.get()
        if selected_batch:
            try:
                # Mostrar loading mientras se cargan los lab samples
                self.lab_sample_id_combo['values'] = ["Loading..."]
                self.lab_sample_id_combo.set("Loading...")
                self.window.update()
                
                # Obtener los Lab Sample IDs para este batch usando la función unificada
                self.lab_sample_ids = self.get_lab_sample_ids_for_batch(selected_batch)
                
                # Actualizar el combobox con los nuevos valores
                self.lab_sample_id_combo['values'] = self.lab_sample_ids
                
                # Limpiar selección y quitar mensaje de loading
                self.lab_sample_id_var.set("")
                
                # Opcional: Seleccionar el primer item si hay datos
                if self.lab_sample_ids:
                    print(f"Loaded {len(self.lab_sample_ids)} lab samples for batch {selected_batch}")
                else:
                    messagebox.showwarning("Warning", f"No lab samples found for batch {selected_batch}")
                    
            except Exception as e:
                # Manejar error y limpiar combobox
                self.lab_sample_id_combo['values'] = []
                self.lab_sample_id_var.set("")
                print(f"Error loading lab samples: {e}")
    
    def validate_quantity(self):
        """Valida que la cantidad sea un número entero válido"""
        quantity_str = self.quantity_var.get().strip()
        if not quantity_str:
            return False, "Please enter the number of tests"
        
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                return False, "Number of tests must be greater than 0"
            if quantity > 50:  # Límite razonable
                return False, "Number of tests cannot exceed 50"
            return True, quantity
        except ValueError:
            return False, "Invalid number format. Please enter a whole number"
    
    def validate_fields(self):
        """Valida que todos los campos requeridos estén completos"""
        if not self.lab_reporting_batch_id_var.get():
            messagebox.showerror("Validation Error", "Please select a Lab Reporting Batch ID")
            return False
            
        if not self.lab_sample_id_var.get():
            messagebox.showerror("Validation Error", "Please select a Lab Sample ID")
            return False
            
        # Validar cantidad
        is_valid, result = self.validate_quantity()
        if not is_valid:
            messagebox.showerror("Validation Error", result)
            return False
            
        if not self.analyte_name_var.get().strip():
            messagebox.showerror("Validation Error", "Please enter an Analyte Name")
            return False
            
        return True
        
    def get_sample_test_data(self):
        """Retorna los datos del sample test como diccionario"""
        
        # Validar cantidad
        is_valid, quantity = self.validate_quantity()
        if not is_valid:
            raise ValueError(f"Invalid quantity: {quantity}")
        
        sample_test_data = {
            'sample_test_id': (self.last_sample_test_id + 1) if self.last_sample_test_id else 1,
            'lab_reporting_batch_id': self.lab_reporting_batch_id_var.get(),
            'lab_sample_id': self.lab_sample_id_var.get(),
            'quantity': quantity,
            'analyte_name': self.analyte_name_var.get().strip(),
            'result': self.result_var.get().strip() if self.result_var.get().strip() else None,
            'error': self.error_var.get().strip() if self.error_var.get().strip() else None,
            'result_units': self.result_units_var.get().strip() if self.result_units_var.get().strip() else None,
            'lab_qualifiers': self.lab_qualifiers_var.get().strip() if self.lab_qualifiers_var.get().strip() else None,
            'detection_limit': self.detection_limit_var.get().strip() if self.detection_limit_var.get().strip() else None,
            'analyte_type': self.analyte_type_var.get().strip() if self.analyte_type_var.get().strip() else None,
            'dilution': self.dilution_var.get().strip() if self.dilution_var.get().strip() else None,
            'percent_moisture': self.percent_moisture_var.get().strip() if self.percent_moisture_var.get().strip() else None,
            'percent_recovery': self.percent_recovery_var.get().strip() if self.percent_recovery_var.get().strip() else None,
            'relative_percent_difference': self.relative_percent_difference_var.get().strip() if self.relative_percent_difference_var.get().strip() else None,
            'reporting_limit': self.reporting_limit_var.get().strip() if self.reporting_limit_var.get().strip() else None,
            'matrix_id': self.matrix_id_var.get().strip() if self.matrix_id_var.get().strip() else None
        }
        
        return sample_test_data
    
    def create_quantity_sample_tests(self, base_test_id, quantity, test_data):
        """Crea múltiples sample tests basados en la cantidad especificada"""
        
        tests_to_create = []
        
        for i in range(quantity):
            current_test_id = base_test_id + i
            
            # Crear lista con los datos del test
            test_list = [
                
                test_data['lab_reporting_batch_id'],
                test_data['lab_sample_id'],
                test_data['analyte_name'],
                test_data['result'],
                test_data['error'],
                test_data['result_units'],
                test_data['lab_qualifiers'],
                test_data['detection_limit'],
                test_data['analyte_type'],
                test_data['dilution'],
                test_data['percent_moisture'],
                test_data['percent_recovery'],
                test_data['relative_percent_difference'],
                test_data['reporting_limit'],
                test_data['matrix_id'],
                'N'
            ]
            
            tests_to_create.append(test_list)
        
        # Definir columnas para la inserción
        columns_to_insert = [
            "LabReportingBatchID", "LabSampleID", "AnalyteName",
            "Result", "Error", "ResultUnits", "LabQualifiers", "DetectionLimit",
            "AnalyteType", "Dilution", "PercentMoisture", "PercentRecovery",
            "RelativePercentDifference", "ReportingLimit", "MatrixID", "QCType"
        ]
        
        
        
        # Aquí debes llamar a tu función de inserción
        insert_sample_tests.insert_sample_tests(tests_to_create, columns_to_insert)
        
        print("Tests to create:", tests_to_create)  # Para debugging
        return columns_to_insert, tests_to_create
    
    def validate_and_get_test_data(self):
        """Valida los campos y retorna los datos del test"""
        
        if not self.validate_fields():
            return None
        
        try:
            test_data = self.get_sample_test_data()
            return test_data
            
        except Exception as e:
            messagebox.showerror("Data Error", f"Error processing test data: {str(e)}")
            return None

    def show_test_confirmation(self, test_data):
        """Muestra una confirmación con los datos de los tests creados"""
        
        message_parts = [
            f"Sample Tests created successfully!",
            "",
            f"Sample Test ID Range: {test_data['sample_test_id']} - {test_data['sample_test_id'] + test_data['quantity'] - 1}",
            f"Lab Reporting Batch ID: {test_data['lab_reporting_batch_id']}",
            f"Lab Sample ID: {test_data['lab_sample_id']}",
            f"Analyte Name: {test_data['analyte_name']}",
            f"Quantity: {test_data['quantity']} tests",
        ]
        
        # Agregar campos opcionales si tienen datos
        optional_fields = [
            ('Result', 'result'),
            ('Result Units', 'result_units'),
            ('Analyte Type', 'analyte_type'),
            ('Matrix ID', 'matrix_id'),
            ('Detection Limit', 'detection_limit')
        ]
        
        for label, key in optional_fields:
            if test_data[key]:
                message_parts.append(f"{label}: {test_data[key]}")
        
        message = "\n".join(message_parts)
        messagebox.showinfo("Success", message)

    def clear_form(self):
        """Limpia todos los campos del formulario"""
        # Mantener Sample Test ID y resetear campos de selección
        self.lab_reporting_batch_id_var.set("")
        self.lab_sample_id_var.set("")
        self.quantity_var.set("1")
        self.analyte_name_var.set("")
        self.result_var.set("")
        self.error_var.set("")
        self.result_units_var.set("")
        self.lab_qualifiers_var.set("")
        self.detection_limit_var.set("")
        self.analyte_type_var.set("")
        self.dilution_var.set("")
        self.percent_moisture_var.set("")
        self.percent_recovery_var.set("")
        self.relative_percent_difference_var.set("")
        self.reporting_limit_var.set("")
        self.matrix_id_var.set("")
        
        # Limpiar combo de sample IDs
        self.lab_sample_id_combo['values'] = []
        
    def create_sample_tests(self):
        """Crea los sample tests"""
        
        # Validar y obtener datos
        test_data = self.validate_and_get_test_data()
        if not test_data:
            return False
            
        try:
            # Crear los tests
            columns, tests = self.create_quantity_sample_tests(
                test_data['sample_test_id'], 
                test_data['quantity'], 
                test_data
            )
            
            # Mostrar confirmación
            self.show_test_confirmation(test_data)
            
            # Preguntar si quiere crear más tests
            result = messagebox.askyesno("Create More?", 
                                       "Sample Tests created successfully!\n\nWould you like to create more tests?")
            
            if result:
                # Limpiar formulario para crear más
                self.clear_form()
                # Recargar datos para actualizar Sample Test ID
                self.load_data()
                # Enfocar en el primer campo editable
                self.lab_reporting_batch_combo.focus()
            else:
                # Cerrar ventana
                self.window.destroy()
                
            return True
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Error creating sample tests: {str(e)}")
            return False
            
    def cancel(self):
        """Cancela y cierra la ventana"""
        if messagebox.askyesno("Cancel", "Are you sure you want to cancel?\n\nAll unsaved data will be lost."):
            self.window.destroy()

def show_sample_tests_wizard(parent=None):
    """Función principal para mostrar el wizard"""
    wizard = SampleTestsWizard(parent)
    wizard.window.grab_set()  # Hacer modal
    wizard.window.focus_set()
    
    # Si no hay parent, ejecutar mainloop
    if parent is None:
        wizard.window.mainloop()
    
    return wizard

def sample_tests_wizard():
    """Función de compatibilidad"""
    show_sample_tests_wizard()
    return True
