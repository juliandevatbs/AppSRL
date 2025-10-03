"""
This is the function to create quality controls
"""
# ==================================================================== #
#                     PROJECT ROOT CONFIGURATION
# ====================================================================

from pathlib import Path
import sys

from BackEnd.Database.General.get_connection import DatabaseConnection

def get_project_root():
    return Path(__file__).parent.parent.absolute()

PROJECT_ROOT = get_project_root()
sys.path.append(str(PROJECT_ROOT))
PROJECT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_DIR))

# ==================================================================== #
#                     IMPORTS
# ====================================================================

import tkinter as tk
from tkinter import ttk, messagebox

class CreateQc:
    # Init config
    def __init__(self, parent=None):
        BASE_DIR = Path(__file__).parent.resolve()
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        # States title of window
        self.window.title("Create QC")
        # States magnitude of window
        self.window.geometry("450x400")
        
        self.window.resizable(False, False)

        # Important data to select and create the qc for specific sample
        self.data_to_select = []
        
        # Comment out the icon line if the file doesn't exist
        try:
            self.window.iconbitmap(BASE_DIR / "assets" / "logos" / "LOGO_SRL_FINAL.ico")
        except:
            pass
        
        self.batch_id_var = tk.StringVar()
        self.lab_sample_id_var = tk.StringVar()
        
        # method blank, lcs, lcsd, ms, msd
        self.controls = ["MB", "LCS", "LCSD", "MS", "MSD"]
        
        self.setup_ui()
        
        # Bind event to batch_id entry
        self.batch_id_var.trace('w', self.on_batch_id_change)
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Create Quality Controls",
                               font=("Century Gothic", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Sección 1: Selección de controles
        controls_label = ttk.Label(main_frame, text="Select Quality Controls:",
                                  font=("Century Gothic", 12, "bold"))
        controls_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        # Variables para los checkboxes
        self.control_vars = {}  # Diccionario para almacenar los BooleanVar de cada control
        
        # Crear checkboxes dinámicamente
        for i, control in enumerate(self.controls):
            var = tk.BooleanVar()
            checkbox = ttk.Checkbutton(main_frame, text=control, variable=var)
            checkbox.grid(row=2 + i, column=0, sticky='w', pady=2, padx=20)
            self.control_vars[control] = var
        
        # Sección 2: LabReportingBatchID
        batch_label = ttk.Label(main_frame, text="LabReportingBatchID: ",
                               font=("Century Gothic", 10, "bold"))
        batch_label.grid(row=8, column=0, sticky=tk.W, pady=(20, 5))
        
        self.batch_id_entry = ttk.Entry(main_frame, textvariable=self.batch_id_var, width=30)
        self.batch_id_entry.grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        self.batch_id_var.bind('<<ComboboxSelected>>', self.on_batch_id_change)


        # Sección 3: Lab Sample ID
        lab_sample_label = ttk.Label(main_frame, text="LabSampleID: ",
                                    font=("Century Gothic", 10, "bold"))
        lab_sample_label.grid(row=10, column=0, sticky=tk.W, pady=(10, 5))
        
        self.lab_sample_combobox = ttk.Combobox(main_frame, textvariable=self.lab_sample_id_var,
                                               width=27, state="readonly")
        self.lab_sample_combobox.grid(row=11, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))
        
        # Status label para mostrar información
        self.status_label = ttk.Label(main_frame, text="Enter Batch ID to load Lab Sample IDs",
                                     foreground="gray")
        self.status_label.grid(row=12, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=13, column=0, columnspan=2, pady=(10, 0))
        
        # Botón para mostrar selección (debug)
        check_btn = ttk.Button(button_frame, text="Preview Selection", 
                              command=self.mostrar_seleccion)
        check_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón principal
        create_btn = ttk.Button(button_frame, text="Create Quality Controls", 
                               command=self.create_quality_controls)
        create_btn.pack(side=tk.LEFT)
    
    def on_batch_id_change(self, *args):
        """
        Se ejecuta cuando el Batch ID cambia
        """
        batch_id = self.batch_id_var.get().strip()
        
        if len(batch_id) >= 3:  # Solo buscar si hay al menos 3 caracteres
            self.load_lab_sample_ids(batch_id)
        else:
            # Limpiar combobox si no hay suficientes caracteres
            self.lab_sample_combobox['values'] = ()
            self.lab_sample_id_var.set('')
            self.status_label.config(text="Enter Batch ID to load Lab Sample IDs", foreground="gray")
    
    def load_lab_sample_ids(self, batch_id):
        """
        Carga los Lab Sample IDs desde la base de datos basado en el Batch ID
        """
        try:
            # Llamar a la función de consulta de base de datos
            lab_sample_ids = self.filter_queries(batch_id)
            
            if lab_sample_ids:
                # Extraer solo los IDs de la lista de listas
                lab_sample_ids_flat = [row[0] for row in lab_sample_ids if row]
                
                self.lab_sample_combobox['values'] = lab_sample_ids_flat
                self.status_label.config(text=f"Found {len(lab_sample_ids_flat)} Lab Sample IDs", 
                                       foreground="green")
                # Seleccionar el primero por defecto
                if lab_sample_ids_flat:
                    self.lab_sample_id_var.set(lab_sample_ids_flat[0])
            else:
                self.lab_sample_combobox['values'] = ()
                self.lab_sample_id_var.set('')
                self.status_label.config(text="No Lab Sample IDs found for this Batch ID", 
                                       foreground="orange")
                
        except Exception as e:
            self.lab_sample_combobox['values'] = ()
            self.lab_sample_id_var.set('')
            self.status_label.config(text=f"Error loading data: {str(e)}", foreground="red")
            print(f"Error in load_lab_sample_ids: {e}")
    
    def filter_queries(self, batch_id: str) -> list:
        """
        Consulta la base de datos para obtener los Lab Sample IDs basados en el Batch ID
        
        Args:
            batch_id (str): ID del batch a consultar
            
        Returns:
            list: Lista de listas con los Lab Sample IDs encontrados
        """
        results_list = []
        conn = None
        cursor = None
        
        try:
            instance_db = DatabaseConnection()
            conn = DatabaseConnection.get_conn(instance_db)
            cursor = conn.cursor()
            
            base_query = """
                SELECT DISTINCT LabSampleID FROM Samples WHERE LabReportingBatchID = ?
            """
            
            cursor.execute(base_query, (batch_id,))
            results = cursor.fetchall()
            
            # Convertir resultados a lista
            for row in results:
                results_list.append(list(row))
            
            print(f"Query results for batch {batch_id}: {results_list}")
            
        except Exception as e:
            print(f"Error al seleccionar muestras: {e}")
            raise e  # Re-raise para que se maneje en load_lab_sample_ids
            
        finally:
            # Cerrar cursor y conexión apropiadamente
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
        return results_list
    
    def mostrar_seleccion(self):
        """
        Muestra la selección actual (para debug)
        """
        seleccionados = [ctrl for ctrl, var in self.control_vars.items() if var.get()]
        batch_id = self.batch_id_var.get().strip()
        lab_sample_id = self.lab_sample_id_var.get().strip()
        
        info = f"Quality Controls: {', '.join(seleccionados) if seleccionados else 'None'}\n"
        info += f"Batch ID: {batch_id if batch_id else 'Not specified'}\n"
        info += f"Lab Sample ID: {lab_sample_id if lab_sample_id else 'Not selected'}"
        
        messagebox.showinfo("Current Selection", info)
    
    def create_quality_controls(self):
        """
        Función principal para crear los controles de calidad
        """
        # Validar selecciones
        seleccionados = [ctrl for ctrl, var in self.control_vars.items() if var.get()]
        batch_id = self.batch_id_var.get().strip()
        lab_sample_id = self.lab_sample_id_var.get().strip()
        
        # Validaciones
        if not seleccionados:
            messagebox.showerror("Error", "Please select at least one Quality Control type.")
            return
        
        if not batch_id:
            messagebox.showerror("Error", "Please enter a Batch ID.")
            return
        
        if not lab_sample_id:
            messagebox.showerror("Error", "Please select a Lab Sample ID.")
            return
        
        # Confirmación
        confirm_msg = f"Create the following Quality Controls?\n\n"
        confirm_msg += f"Controls: {', '.join(seleccionados)}\n"
        confirm_msg += f"Batch ID: {batch_id}\n"
        confirm_msg += f"Lab Sample ID: {lab_sample_id}"
        
        if messagebox.askyesno("Confirm Creation", confirm_msg):
            try:
                # AQUÍ IMPLEMENTA LA LÓGICA PARA CREAR LOS QC
                self.execute_qc_creation(seleccionados, batch_id, lab_sample_id)
                
                messagebox.showinfo("Success", 
                                   f"Quality Controls created successfully!\n\n"
                                   f"Created: {', '.join(seleccionados)}\n"
                                   f"For Batch: {batch_id}")
                
                # Opcional: cerrar ventana después de crear
                # self.window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create Quality Controls:\n{str(e)}")
    
    def execute_qc_creation(self, control_types, batch_id, lab_sample_id):
        """
        IMPLEMENTA AQUÍ LA LÓGICA PARA CREAR LOS QC EN LA BASE DE DATOS
        
        Args:
            control_types: Lista de tipos de control seleccionados ['MB', 'LCS', etc.]
            batch_id: ID del batch
            lab_sample_id: ID de la muestra de laboratorio
        """
        # TODO: Implementar la creación real en la base de datos
        print(f"Creating QC:")
        print(f"  Control Types: {control_types}")
        print(f"  Batch ID: {batch_id}")
        print(f"  Lab Sample ID: {lab_sample_id}")
        
        # Aquí deberías:
        # 1. Conectar a la base de datos
        # 2. Insertar los registros de QC
        # 3. Manejar cualquier error
        
        # Simulación de procesamiento
        import time
        time.sleep(1)  # Simula tiempo de procesamiento

def show_create_qc_view(parent=None):
    """
    Function to open the view
    """
    show_create_qc_view = CreateQc(parent)
    if parent:
        show_create_qc_view.window.grab_set()
        show_create_qc_view.window.focus_set()
    
    if parent is None:
        show_create_qc_view.window.mainloop()
    
    return show_create_qc_view

def create_qc():
    show_create_qc_view()
    return True

if __name__ == '__main__':
    show_create_qc_view()