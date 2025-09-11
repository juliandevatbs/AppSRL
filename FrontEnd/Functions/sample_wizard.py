from pathlib import Path
import sys

from BackEnd.Database.Queries.Insert.insert_samples import insert_samples
from BackEnd.Database.Queries.Wizard.select_data_to_c_sample import get_all_sample_data


def get_project_root():
    return Path(__file__).parent.parent.absolute()

PROJECT_ROOT = get_project_root()
sys.path.insert(0, str(PROJECT_ROOT))  
PROJECT_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_DIR))

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime



class SampleWizard:
    
    
    def __init__(self, parent = None):



        BASE_DIR = Path(__file__).parent.resolve()
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Sample Creation Wizard")
        self.window.geometry("720x550")  
        self.window.resizable(False, False)
        #self.root.iconbitmap(BASE_DIR / "Assets" / "logos" / "LOGO_SRL_FINAL.ico")
        
        # Variables para los campos
        self.client_sample_id_var = tk.StringVar()
        self.collect_method_var = tk.StringVar()
        self.collection_agency_var = tk.StringVar()
        self.matrix_var = tk.StringVar()
        self.sampler_var = tk.StringVar()
        self.sample_date_var = tk.StringVar()
        self.sample_time_var = tk.StringVar()
        self.sample_quantity_var = tk.StringVar()  
        self.comments_var = tk.StringVar()
        self.adapt_matrix_var = tk.StringVar()
        self.total_containers = tk.StringVar()
        self.lab_id_var = tk.StringVar()
        self.shipping_id_var = tk.StringVar()
        
        
        # Datos para los comboboxes
        self.collect_methods = []
        self.collection_agencies = []
        self.matrices = []
        self.samplers = []
        self.last_batch_id = None
        self.adapts_matrix = []
        self.lab_ids = []
        self.shipping_batchs = []
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="Create New Sample", 
                               font=("Century Gothic", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Batch ID (solo lectura)
        ttk.Label(main_frame, text="Batch ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.batch_label = ttk.Label(main_frame, text="Loading...", 
                                    font=("Century Gothic", 10, "bold"))
        self.batch_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
            
        # Client Sample ID
        ttk.Label(main_frame, text="Client Sample ID:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.client_sample_id_entry = ttk.Entry(main_frame, textvariable=self.client_sample_id_var, width=40)
        self.client_sample_id_entry.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Collect Method
        ttk.Label(main_frame, text="Collect Method:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.collect_method_combo = ttk.Combobox(main_frame, textvariable=self.collect_method_var,
                                                state="readonly", width=37)
        self.collect_method_combo.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Collection Agency
        ttk.Label(main_frame, text="Collection Agency:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.collection_agency_combo = ttk.Combobox(main_frame, textvariable=self.collection_agency_var,
                                                   state="readonly", width=37)
        self.collection_agency_combo.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Matrix
        ttk.Label(main_frame, text="Matrix:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.matrix_combo = ttk.Combobox(main_frame, textvariable=self.matrix_var,
                                        state="readonly", width=37)
        self.matrix_combo.grid(row=5, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Sampler
        ttk.Label(main_frame, text="Sampler:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.sampler_combo = ttk.Combobox(main_frame, textvariable=self.sampler_var,
                                         state="readonly", width=37)
        self.sampler_combo.grid(row=6, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Sample Quantity
        ttk.Label(main_frame, text="Number of Samples:").grid(row=7, column=0, sticky=tk.W, pady=5)
        quantity_frame = ttk.Frame(main_frame)
        quantity_frame.grid(row=7, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        self.sample_quantity_entry = ttk.Entry(quantity_frame, textvariable=self.sample_quantity_var, width=10)
        self.sample_quantity_entry.grid(row=0, column=0)
        
        ttk.Label(quantity_frame, text="samples").grid(row=0, column=1, padx=(5, 0))
        
        # Botones de cantidad rápida
        quick_frame = ttk.Frame(quantity_frame)
        quick_frame.grid(row=0, column=2, padx=(10, 0))
        
        ttk.Button(quick_frame, text="1", command=lambda: self.sample_quantity_var.set("1"), 
                  width=3).grid(row=0, column=0, padx=2)
        ttk.Button(quick_frame, text="5", command=lambda: self.sample_quantity_var.set("5"), 
                  width=3).grid(row=0, column=1, padx=2)
        ttk.Button(quick_frame, text="10", command=lambda: self.sample_quantity_var.set("10"), 
                  width=3).grid(row=0, column=2, padx=2)
        
        # Sample Date
        ttk.Label(main_frame, text="Date Collected:").grid(row=8, column=0, sticky=tk.W, pady=5)
        date_frame = ttk.Frame(main_frame)
        date_frame.grid(row=8, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        self.sample_date_entry = ttk.Entry(date_frame, textvariable=self.sample_date_var, width=12)
        self.sample_date_entry.grid(row=0, column=0)
        ttk.Label(date_frame, text="(YYYY-MM-DD)").grid(row=0, column=1, padx=(5, 0))
        
        # Botón para fecha actual
        ttk.Button(date_frame, text="Today", command=self.set_current_date,
                  width=8, cursor="hand2").grid(row=0, column=2, padx=(5, 0))
                
        # Sample Time
        ttk.Label(main_frame, text="Sample Time:").grid(row=9, column=0, sticky=tk.W, pady=5)
        time_frame = ttk.Frame(main_frame)
        time_frame.grid(row=9, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        self.sample_time_entry = ttk.Entry(time_frame, textvariable=self.sample_time_var, width=12)
        self.sample_time_entry.grid(row=0, column=0)
        ttk.Label(time_frame, text="(HH:MM:SS)").grid(row=0, column=1, padx=(5, 0))
        
        # Botón para hora actual
        ttk.Button(time_frame, text="Now", command=self.set_current_time,
                  width=8, cursor="hand2").grid(row=0, column=2, padx=(5, 0))
        
        # Comments
        ttk.Label(main_frame, text="Comments:").grid(row=10, column=0, sticky=(tk.W, tk.N), pady=5)
        self.comments_entry = tk.Text(main_frame, width=30, height=4)
        self.comments_entry.grid(row=10, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # COLUMNA DERECHA - Campos adicionales
        
        # Shipping Bath ID
        ttk.Label(main_frame, text="Shipping Bath ID:").grid(row=3, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.shipping_id_entry = ttk.Combobox(main_frame, width=15)
        self.shipping_id_entry.grid(row=3, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Cooler Number
        ttk.Label(main_frame, text="Cooler Number:").grid(row=4, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.cooler_number_entry = ttk.Entry(main_frame, width=15)
        self.cooler_number_entry.grid(row=4, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Temperature
        ttk.Label(main_frame, text="Temperature:").grid(row=5, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.temperature_entry = ttk.Entry(main_frame, width=15)
        self.temperature_entry.grid(row=5, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Adapt Matrix ID
        ttk.Label(main_frame, text="Adapt Matrix:").grid(row=6, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.adapt_matrix_combo = ttk.Combobox(main_frame, textvariable=self.adapt_matrix_var,
                                              state="readonly", width=12)
        self.adapt_matrix_combo.grid(row=6, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        #Total containers
        ttk.Label(main_frame, text="Total containers:").grid(row=7, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.total_containers = ttk.Entry(main_frame, width=5)
        self.total_containers.grid(row=7, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Lab ID
        ttk.Label(main_frame, text="Lab ID:").grid(row=8, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.lab_id_combo = ttk.Combobox(main_frame, textvariable=self.lab_id_var, state="readonly", width=12)
        self.lab_id_combo.grid(row=8, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=11, column=0, columnspan=4, pady=20)
        
        ttk.Button(button_frame, text="Create Sample", command=self.create_sample,
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
            self.batch_label.config(text="Loading data...")
            self.window.update()
            
            all_data = get_all_sample_data()
            
            # Cargar datos
            self.last_batch_id = all_data['last_batch_id']
            self.collect_methods = all_data['collect_methods']
            self.collection_agencies = all_data['collection_agencies']
            self.matrices = all_data['matrices']
            self.samplers = all_data['samplers']
            self.adapts_matrix = all_data['adapts_matrix']
            self.lab_ids = all_data['lab_ids']
            self.shipping_batchs = all_data['shipping_batchs']
            
            # Actualizar UI
            self.update_comboboxes()
            
            # Mostrar batch ID
            batch_text = f"{self.last_batch_id}" if self.last_batch_id else "1"
            self.batch_label.config(text=batch_text)
            
            # Establecer fecha y hora actuales por defecto
            self.set_current_date()
            self.set_current_time()
            
            # Establecer cantidad por defecto
            self.sample_quantity_var.set("1")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading data: {str(e)}")
            self.batch_label.config(text="Error loading")
    
    def update_comboboxes(self):
        """Actualiza los valores de los comboboxes"""
        self.collect_method_combo['values'] = self.collect_methods
        self.collection_agency_combo['values'] = self.collection_agencies
        self.matrix_combo['values'] = self.matrices
        self.sampler_combo['values'] = self.samplers
        self.adapt_matrix_combo['values'] = self.adapts_matrix
        self.lab_id_combo['values'] = self.lab_ids
        #self.shipping_batchs['values'] = self.shipping_batchs
        
    def set_current_date(self):
        """Establece la fecha actual"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.sample_date_var.set(current_date)
        
    def set_current_time(self):
        """Establece la hora actual"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.sample_time_var.set(current_time)
        
    def validate_sample_quantity(self):
        """Valida que la cantidad de muestras sea un número entero válido"""
        quantity_str = self.sample_quantity_var.get().strip()
        if not quantity_str:
            return False, "Please enter the number of samples"
        
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                return False, "Number of samples must be greater than 0"
            if quantity > 100:  # Límite razonable
                return False, "Number of samples cannot exceed 100"
            return True, quantity
        except ValueError:
            return False, "Invalid number format. Please enter a whole number"
    
    def validate_fields(self):
        """Valida que todos los campos requeridos estén completos"""
        """if not self.collect_method_var.get():
            messagebox.showerror("Validation Error", "Please select a collect method")
            return False"""
            
        """if not self.collection_agency_var.get():
            messagebox.showerror("Validation Error", "Please select a collection agency")
            return False"""
            
        """if not self.matrix_var.get():
            messagebox.showerror("Validation Error", "Please select a matrix")
            return False"""
            
        """if not self.sampler_var.get():
            messagebox.showerror("Validation Error", "Please select a sampler")
            return False"""
        
        # Validar cantidad de muestras
        is_valid, result = self.validate_sample_quantity()
        if not is_valid:
            messagebox.showerror("Validation Error", result)
            return False
            
        """if not self.sample_date_var.get():
            messagebox.showerror("Validation Error", "Please enter a sample date")
            return False"""
            
        """if not self.sample_time_var.get():
            messagebox.showerror("Validation Error", "Please enter a sample time")
            return False"""
            
        # Validar formato de fecha
        try:
            datetime.strptime(self.sample_date_var.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid date format. Use YYYY-MM-DD")
            return False
            
        # Validar formato de hora
        try:
            datetime.strptime(self.sample_time_var.get(), "%H:%M:%S")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid time format. Use HH:MM:SS")
            return False
            
        return True
        
    def get_sample_data(self):
        """Retorna los datos del sample como diccionario"""
        
        # Obtener la cantidad de muestras validada
        is_valid, quantity = self.validate_sample_quantity()
        if not is_valid:
            raise ValueError(f"Invalid sample quantity: {quantity}")
        
        # Obtener comentarios del widget Text
        comments = self.comments_entry.get("1.0", tk.END).strip()
        
        # Obtener datos de los campos adicionales
        shipping_bath_id = self.shipping_id_entry.get().strip()
        cooler_number = self.cooler_number_entry.get().strip()
        temperature = self.temperature_entry.get().strip()
        
        # Crear el diccionario con todos los datos
        sample_data = {
            'batch_id': self.last_batch_id + 1 if self.last_batch_id else 1,
            'client_sample_id': self.client_sample_id_var.get().strip(),
            'collect_method': self.collect_method_var.get(),
            'collection_agency': self.collection_agency_var.get(),
            'matrix': self.matrix_var.get(),
            'sampler': self.sampler_var.get(),
            'quantity': quantity,  # Ya validado como int
            'sample_date': self.sample_date_var.get(),
            'sample_time': self.sample_time_var.get(),
            'date_collected_full': f"{self.sample_date_var.get()} {self.sample_time_var.get()}",
            'comments': comments if comments else None,
            'shipping_bath_id': shipping_bath_id if shipping_bath_id else None,
            'cooler_number': cooler_number if cooler_number else None,
            'temperature': temperature if temperature else None,
            'adapt_matrix_id': self.adapt_matrix_var.get() if self.adapt_matrix_var.get() else None,
            'total_containers': self.total_containers.get() if self.total_containers.get() else None
        }
        
        return sample_data
    
    def create_quantity_samples(self, batch_id, times: int, sample):

        samples_to_create = []
        
        for consecutive in range(1, times +1):
            
            lab_sample_id = f"{batch_id}-{consecutive:03d}"
            
            print(lab_sample_id)
            
            sample_list = []
            
            for data_sample in sample.values():
                sample_list.append(data_sample)
            sample_list.insert(0, consecutive)
            
            sample_list.append(lab_sample_id)
            sample_list.append(0)
            samples_to_create.append(sample_list)
                
        columns_to_insert = [
                             "ItemID",
                             "LabSampleID",
                             "ClientSampleID",
                             "CollectMethod",
                             "CollectionAgency",
                             "MatrixID",
                             "Sampler",
                             "DateCollected",
                             "ResultComments",
                             "ShippingBatchID",
                             "CoolerNumber",
                             "Temperature",
                             "AdaptMatrixID",
                             "TotalContainers",
                             "LabID",
                            "LabReportingBatchID"
                            ]
            
        #print(columns_to_insert)
        
        insert_samples(samples_to_create, columns_to_insert)
      
       
        print(samples_to_create)
        return columns_to_insert, samples_to_create
     

    def validate_and_get_sample_data(self):
        """Valida los campos y retorna los datos del sample"""
        
        # Primero validar todos los campos
        if not self.validate_fields():
            return None
        
        try:
            # Obtener los datos validados
            sample_data = self.get_sample_data()
            
            # Validaciones adicionales si es necesario
            if sample_data['quantity'] > 100:
                raise ValueError("Quantity cannot exceed 100 samples")
                
            # Validar que la fecha no sea futura (opcional)
            sample_datetime = datetime.strptime(sample_data['date_collected_full'], "%Y-%m-%d %H:%M:%S")
            if sample_datetime > datetime.now():
                raise ValueError("Sample date cannot be in the future")
    
            return sample_data
            
        except Exception as e:
            messagebox.showerror("Data Error", f"Error processing sample data: {str(e)}")
            return None

    def show_sample_confirmation(self, sample_data):
        """Muestra una confirmación con los datos del sample creado"""
        
        message_parts = [
            "Sample created successfully!",
            "",
            f"Batch ID: {sample_data['batch_id']}",
            f"Client Sample ID: {sample_data['client_sample_id']}",
            f"Collect Method: {sample_data['collect_method']}",
            f"Collection Agency: {sample_data['collection_agency']}",
            f"Matrix: {sample_data['matrix']}",
            f"Sampler: {sample_data['sampler']}",
            f"Quantity: {sample_data['quantity']} samples",
            f"Date Collected: {sample_data['sample_date']}",
            f"Time Collected: {sample_data['sample_time']}"
        ]
        
        # Agregar campos opcionales si tienen datos
        if sample_data['shipping_bath_id']:
            message_parts.append(f"Shipping Bath ID: {sample_data['shipping_bath_id']}")
        
        if sample_data['cooler_number']:
            message_parts.append(f"Cooler Number: {sample_data['cooler_number']}")
        
        if sample_data['temperature']:
            message_parts.append(f"Temperature: {sample_data['temperature']}")
            
        if sample_data['adapt_matrix_id']:
            message_parts.append(f"Adapt Matrix ID: {sample_data['adapt_matrix_id']}")
        
        if sample_data['comments']:
            message_parts.append(f"Comments: {sample_data['comments']}")
        
        message = "\n".join(message_parts)
        messagebox.showinfo("Success", message)

    def clear_form(self):
        """Limpia todos los campos del formulario"""
        self.client_sample_id_var.set("")
        self.collect_method_var.set("")
        self.collection_agency_var.set("")
        self.matrix_var.set("")
        self.sampler_var.set("")
        self.sample_quantity_var.set("1")
        self.adapt_matrix_var.set("")
        
        # Limpiar campos de texto
        self.comments_entry.delete("1.0", tk.END)
        self.shipping_id_entry.delete(0, tk.END)
        self.cooler_number_entry.delete(0, tk.END)
        self.temperature_entry.delete(0, tk.END)
        
        # Resetear fecha y hora a valores actuales
        self.set_current_date()
        self.set_current_time()

    def get_essential_sample_data(self):
        """Retorna solo los datos esenciales del sample"""
        return {
            'batch_id': self.last_batch_id + 1 if self.last_batch_id else 1,
            'client_sample_id': self.client_sample_id_var.get().strip(),
            'collect_method': self.collect_method_var.get(),
            'collection_agency': self.collection_agency_var.get(),
            'matrix': self.matrix_var.get(),
            'sampler': self.sampler_var.get(),
            'quantity': int(self.sample_quantity_var.get()),
            'date_collected': f"{self.sample_date_var.get()} {self.sample_time_var.get()}"
        }
        
    def create_sample(self):
        """Crea el sample"""
        
        # Validar y obtener datos
        sample_data = self.validate_and_get_sample_data()
        if not sample_data:
            return False
            
        try:

            
            self.create_quantity_samples(sample_data['batch_id'], sample_data['quantity'], sample_data)
            
            # Mostrar confirmación con datos
            self.show_sample_confirmation(sample_data)
            
            # Preguntar si quiere crear otro sample
            result = messagebox.askyesno("Create Another?", 
                                       "Sample created successfully!\n\nWould you like to create another sample?")
            
            if result:
                self.clear_form()
                self.client_sample_id_entry.focus()
                
                #Update the last batch id
                self.load_data()
                
                
            else:
                # Cerrar ventana
                self.window.destroy()
                
            return True
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Error creating sample in database: {str(e)}")
            return False
            
    def cancel(self):
        """Cancela y cierra la ventana"""
        if messagebox.askyesno("Cancel", "Are you sure you want to cancel?\n\nAll unsaved data will be lost."):
            self.window.destroy()

def show_samples_wizard(parent=None):
    """Función principal para mostrar el wizard"""
    wizard = SampleWizard(parent)
    wizard.window.grab_set()  # Hacer modal
    wizard.window.focus_set()
    
    # Si no hay parent, ejecutar mainloop
    if parent is None:
        wizard.window.mainloop()
    
    return wizard

def sample_wizard():
    """Función de compatibilidad"""
    show_samples_wizard()

    return True


    