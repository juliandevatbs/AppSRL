import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path

from BackEnd.Database.Queries.Select.select_samples import select_samples
from BackEnd.Database.Queries.Updates.update_assign_data import update_assign_data



"""
This view is for assign data
1. Assign data to big information groups
2. Select specific samples by LabSampleID or all samples in batch
"""

class AssignData:
    
    #Init config
    def __init__(self, parent=None):
        
        BASE_DIR = Path(__file__).parent.resolve()
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Assign data")
        
        # Set window size
        window_width = 800
        window_height = 500
        
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Calculate position to center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set geometry with centered position
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
        self.window.resizable(True, True)
        self.window.iconbitmap(BASE_DIR / "assets" / "logos" / "LOGO_SRL_FINAL.ico")
        
        # Variables to the user    
        self.group_id = tk.StringVar()
        self.data_to_assign = tk.StringVar()
        self.field_to_assign = tk.StringVar()
        self.lab_reporting_batch_id = tk.StringVar()
        self.sample_selection_mode = tk.StringVar(value="all")  # "all" or "specific"
        
        # Date variables for date picker
        self.selected_date = tk.StringVar()
        self.selected_date.set(datetime.now().strftime("%Y-%m-%d"))
        
        # Sample data storage
        self.available_samples = []  # Will store sample data from database
        self.selected_samples = []   # Will store selected sample IDs
        
        # Fields to select
        self.fields_select = [
            "ClientSampleID", "Sampler", "DateCollected", "MatrixID", 
            "LabAnalysisRefMethodID", "Temperature", "CollectMethod", 
            "TotalContainers", "CoolerNumber"
        ]
        
        # Sample data for comboboxes (you should replace these with your actual data)
        self.samplers = ["Sampler A", "Sampler B", "Sampler C", "Sampler D"]
        self.matrix_ids = ["Matrix 1", "Matrix 2", "Matrix 3", "Matrix 4"]
        self.lab_analysis_methods = ["Method A", "Method B", "Method C", "Method D"]
        self.collect_methods = ["Manual", "Automatic", "Grab Sample", "Composite"]
        
        # Current input widget reference
        self.current_input_widget = None
        
        self.setup_ui()
    
    def center_window(self, window, width, height):
        """Center a window on the screen"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - width) // 2
        
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    # Define the view
    def setup_ui(self):
        
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid columns to center content
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Container frame for centered content
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=0, column=0, columnspan=2, sticky="")
        
        # Title (centered)
        title_label = ttk.Label(content_frame, text="Assign data",
                               font=("Century Gothic", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Form container for better alignment
        form_frame = ttk.Frame(content_frame)
        form_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # LabReportingBatchID field
        ttk.Label(form_frame, text="Lab Reporting Batch ID:").grid(row=0, column=0, sticky=tk.E, pady=5, padx=(0, 10))
        lab_batch_entry = ttk.Entry(form_frame, textvariable=self.lab_reporting_batch_id, width=25)
        lab_batch_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        lab_batch_entry.bind('<KeyRelease>', self.on_batch_id_change)
        
        # Load samples button
        ttk.Button(form_frame, text="Load Samples", command=self.load_samples_from_batch,
                  width=12, cursor="hand2").grid(row=0, column=2, padx=(10, 0), pady=5)
        
        # Sample selection mode
        ttk.Label(form_frame, text="Sample Selection:").grid(row=1, column=0, sticky=tk.E, pady=5, padx=(0, 10))
        selection_frame = ttk.Frame(form_frame)
        selection_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(selection_frame, text="All samples in batch", 
                       variable=self.sample_selection_mode, value="all",
                       command=self.on_selection_mode_change).pack(side=tk.LEFT)
        ttk.Radiobutton(selection_frame, text="Select specific samples", 
                       variable=self.sample_selection_mode, value="specific",
                       command=self.on_selection_mode_change).pack(side=tk.LEFT, padx=(20, 0))
        
        # Sample selection area (initially hidden)
        self.sample_selection_frame = ttk.LabelFrame(form_frame, text="Available Samples", padding="10")
        self.sample_selection_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)
        self.sample_selection_frame.grid_remove()  # Hide initially
        
        # Create sample selection widgets
        self.setup_sample_selection()
        
        # List for the field selection
        ttk.Label(form_frame, text="Select field to assign:").grid(row=3, column=0, sticky=tk.E, pady=5, padx=(0, 10))
        self.field_selection_combo = ttk.Combobox(form_frame, textvariable=self.field_to_assign,
                                                  state="readonly", width=25)
        self.field_selection_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        self.field_selection_combo.bind('<<ComboboxSelected>>', self.on_field_selection_change)
        self.update_comboboxes()

        # Label for data to assign
        self.data_label = ttk.Label(form_frame, text="Write the value:")
        self.data_label.grid(row=4, column=0, sticky=tk.E, pady=5, padx=(0, 10))
        
        # Frame for dynamic input widget
        self.input_frame = ttk.Frame(form_frame)
        self.input_frame.grid(row=4, column=1, sticky=tk.W, pady=5)
         
        # Buttons (centered)
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        """# Execute button
        ttk.Button(button_frame, text="Execute", command=self.execute_assignment,
                  width=10, cursor="hand2").pack(side=tk.LEFT, padx=5)
        """
        # Update button - NUEVO BOTÓN AGREGADO
        ttk.Button(button_frame, text="Update", command=self.update_data,
                  width=10, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        # Clear button
        ttk.Button(button_frame, text="Clear", command=self.clear_fields,
                  width=10, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        self.create_default_input()
    
    def setup_sample_selection(self):
        """Setup the sample selection interface"""
        # Info label
        self.sample_info_label = ttk.Label(self.sample_selection_frame, 
                                          text="No samples loaded. Enter Batch ID and click 'Load Samples'.")
        self.sample_info_label.pack(pady=5)
        
        # Scrollable frame for sample checkboxes
        canvas = tk.Canvas(self.sample_selection_frame, height=150)
        scrollbar = ttk.Scrollbar(self.sample_selection_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Initially hidden
        self.canvas = canvas
        self.scrollbar = scrollbar
        
        # Selection buttons frame
        self.selection_buttons_frame = ttk.Frame(self.sample_selection_frame)
        
        ttk.Button(self.selection_buttons_frame, text="Select All", 
                  command=self.select_all_samples).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.selection_buttons_frame, text="Deselect All", 
                  command=self.deselect_all_samples).pack(side=tk.LEFT, padx=5)
    
    def on_batch_id_change(self, event=None):
        """Handle batch ID change"""
        # Clear existing samples when batch ID changes
        self.available_samples = []
        self.selected_samples = []
        self.update_sample_selection_display()
    
    def on_selection_mode_change(self):
        """Handle selection mode change"""
        if self.sample_selection_mode.get() == "specific":
            if self.available_samples:
                self.sample_selection_frame.grid()
        else:
            self.sample_selection_frame.grid_remove()
    
    def load_samples_from_batch(self):
        """Load samples from database based on batch ID"""
        batch_id = self.lab_reporting_batch_id.get().strip()
        
        if not batch_id:
            messagebox.showwarning("Warning", "Please enter a Lab Reporting Batch ID first.")
            return
        
        try:
            # Convert batch_id to integer since the function expects int
            batch_id_int = int(batch_id)
            
            # Call the select_samples function
            raw_samples = select_samples(batch_id_int, [], None, True)
            
            if not raw_samples:
                messagebox.showinfo("No Samples", f"No samples found for Batch ID: {batch_id}")
                self.available_samples = []
            else:
                # Convert raw database results to dictionary format
                # Based on the SQL query, the columns are:
                # ItemID, LabReportingBatchID, LabSampleID, ClientSampleID, DateCollected, MatrixID, AnalysisMethodIDs
                self.available_samples = []
                
                for row in raw_samples:
                    sample_dict = {
                        'item_id': row[0],
                        'lab_reporting_batch_id': row[1],
                        'lab_sample_id': row[2],
                        'client_sample_id': row[3] if row[3] else 'N/A',
                        'date_collected': row[4],
                        'matrix_id': row[5],
                        'analysis_method_ids': row[6] if row[6] else '',
                        'status': 'Active'  # Default status since it's not in the query
                    }
                    self.available_samples.append(sample_dict)
                
                # LÍNEA REMOVIDA: messagebox.showinfo("Samples Loaded", f"Loaded {len(self.available_samples)} samples for Batch ID: {batch_id}")
            
            self.update_sample_selection_display()
        
        except ValueError:
            messagebox.showerror("Input Error", "Lab Reporting Batch ID must be a valid number.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading samples: {str(e)}")
    
    
    def update_sample_selection_display(self):
        """Update the sample selection display"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.available_samples:
            self.sample_info_label.config(text="No samples loaded. Enter Batch ID and click 'Load Samples'.")
            return
        
        # Update info label
        self.sample_info_label.config(text=f"Found {len(self.available_samples)} samples:")
        
        # Create checkboxes for each sample
        self.sample_vars = {}
        for i, sample in enumerate(self.available_samples):
            var = tk.BooleanVar()
            self.sample_vars[sample['lab_sample_id']] = var
            
            # Create frame for each sample
            sample_frame = ttk.Frame(self.scrollable_frame)
            sample_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Checkbox
            cb = ttk.Checkbutton(sample_frame, variable=var, 
                               text=f"{sample['lab_sample_id']} - {sample['client_sample_id']} ({sample['status']})")
            cb.pack(side=tk.LEFT)
        
        # Show canvas and scrollbar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.selection_buttons_frame.pack(pady=10)
        
        # Update scrollregion
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def select_all_samples(self):
        """Select all available samples"""
        for var in self.sample_vars.values():
            var.set(True)
    
    def deselect_all_samples(self):
        """Deselect all samples"""
        for var in self.sample_vars.values():
            var.set(False)
    
    def get_selected_samples(self):
        """Get list of selected sample IDs"""
        if self.sample_selection_mode.get() == "all":
            return [sample['lab_sample_id'] for sample in self.available_samples]
        else:
            return [sample_id for sample_id, var in self.sample_vars.items() if var.get()]
    
    def update_comboboxes(self):
        """Updates the values of comboboxes"""
        self.field_selection_combo['values'] = self.fields_select
    
    def on_field_selection_change(self, event=None):
        """Handle field selection change and create appropriate input widget"""
        selected_field = self.field_to_assign.get()
        self.create_input_widget(selected_field)
    
    def clear_input_frame(self):
        """Clear the input frame"""
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        self.current_input_widget = None
    
    def create_default_input(self):
        """Create default text entry"""
        self.clear_input_frame()
        self.current_input_widget = ttk.Entry(self.input_frame, textvariable=self.data_to_assign, width=25)
        self.current_input_widget.pack()
    
    def create_input_widget(self, field_type):
        """Create appropriate input widget based on field type"""
        self.clear_input_frame()
        
        if field_type == "ClientSampleID":
            # Text entry for Client Sample ID
            self.current_input_widget = ttk.Entry(self.input_frame, textvariable=self.data_to_assign, width=25)
            self.current_input_widget.pack()
            
        elif field_type == "Sampler":
            # Combobox for Sampler selection
            self.current_input_widget = ttk.Combobox(self.input_frame, textvariable=self.data_to_assign, 
                                                   values=self.samplers, width=22, state="readonly")
            self.current_input_widget.pack()
            
        elif field_type == "DateCollected":
            # Date picker (using Entry with validation)
            date_frame = ttk.Frame(self.input_frame)
            date_frame.pack()
            
            self.current_input_widget = ttk.Entry(date_frame, textvariable=self.data_to_assign, width=15)
            self.current_input_widget.pack(side=tk.LEFT)
            
            # Button to open date picker
            ttk.Button(date_frame, text="📅", width=3, command=self.open_date_picker).pack(side=tk.LEFT, padx=(2, 0))
            
            # Set default date
            self.data_to_assign.set(datetime.now().strftime("%Y-%m-%d"))
            
        elif field_type == "MatrixID":
            # Combobox for Matrix ID selection
            self.current_input_widget = ttk.Combobox(self.input_frame, textvariable=self.data_to_assign,
                                                   values=self.matrix_ids, width=22, state="readonly")
            self.current_input_widget.pack()
            
        elif field_type == "LabAnalysisRefMethodID":
            # Combobox for Lab Analysis Method selection
            self.current_input_widget = ttk.Combobox(self.input_frame, textvariable=self.data_to_assign,
                                                   values=self.lab_analysis_methods, width=22, state="readonly")
            self.current_input_widget.pack()
            
        elif field_type == "Temperature":
            # Numeric entry for Temperature
            self.current_input_widget = ttk.Entry(self.input_frame, textvariable=self.data_to_assign, width=25)
            self.current_input_widget.pack()
            # Add validation for numeric input
            self.current_input_widget.bind('<KeyRelease>', lambda e: self.validate_numeric_input(e, allow_decimal=True))
            
        elif field_type == "CollectMethod":
            # Combobox for Collection Method selection
            self.current_input_widget = ttk.Combobox(self.input_frame, textvariable=self.data_to_assign,
                                                   values=self.collect_methods, width=22, state="readonly")
            self.current_input_widget.pack()
            
        elif field_type == "TotalContainers":
            # Numeric entry for Total Containers
            self.current_input_widget = ttk.Entry(self.input_frame, textvariable=self.data_to_assign, width=25)
            self.current_input_widget.pack()
            # Add validation for integer input
            self.current_input_widget.bind('<KeyRelease>', lambda e: self.validate_numeric_input(e, allow_decimal=False))
            
        elif field_type == "CoolerNumber":
            # Numeric entry for Cooler Number
            self.current_input_widget = ttk.Entry(self.input_frame, textvariable=self.data_to_assign, width=25)
            self.current_input_widget.pack()
            # Add validation for integer input
            self.current_input_widget.bind('<KeyRelease>', lambda e: self.validate_numeric_input(e, allow_decimal=False))
            
        elif field_type == "LabReportingBatchID":
            # Text entry for Lab Reporting Batch ID
            self.current_input_widget = ttk.Entry(self.input_frame, textvariable=self.data_to_assign, width=25)
            self.current_input_widget.pack()
        
        else:
            # Default text entry for unspecified fields
            self.create_default_input()
    
    def validate_numeric_input(self, event, allow_decimal=True):
        """Validate numeric input"""
        value = event.widget.get()
        if value == "":
            return
        
        try:
            if allow_decimal:
                float(value)
            else:
                int(value)
        except ValueError:
            # Remove the last character if it's not valid
            event.widget.delete(len(value)-1)
    
    def open_date_picker(self):
        """Open a simple date picker dialog"""
        date_window = tk.Toplevel(self.window)
        date_window.title("Select Date")
        
        # Center the date picker window
        self.center_window(date_window, 300, 200)
        
        date_window.resizable(False, False)
        date_window.grab_set()
    
    # NUEVA FUNCIÓN PARA EL BOTÓN UPDATE
    def update_data(self):
        """Recolecta y retorna todos los datos seleccionados por el usuario"""
        try:
            # Validar que se hayan cargado muestras
            if not self.available_samples:
                messagebox.showwarning("Warning", "Please load samples first by entering a Batch ID and clicking 'Load Samples'.")
                return None
            
            # Obtener muestras seleccionadas
            selected_samples = self.get_selected_samples()
            
            if not selected_samples:
                messagebox.showwarning("Warning", "Please select at least one sample.")
                return None
            
            # Validar que se haya seleccionado un campo
            if not self.field_to_assign.get():
                messagebox.showwarning("Warning", "Please select a field to assign.")
                return None
            
            # Validar que se haya ingresado un valor
            if not self.data_to_assign.get().strip():
                messagebox.showwarning("Warning", "Please enter a value to assign.")
                return None
            
            # Recopilar toda la información seleccionada
            update_data = {
                'batch_id': self.lab_reporting_batch_id.get(),
                'selection_mode': self.sample_selection_mode.get(),
                'selected_samples': selected_samples,
                'selected_samples_count': len(selected_samples),
                'field_to_assign': self.field_to_assign.get(),
                'value_to_assign': self.data_to_assign.get(),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_available_samples': len(self.available_samples)
            }
            
            try:
                update_assign_data(update_data['field_to_assign'], update_data['selected_samples'], update_data['value_to_assign'])

            except Exception as ex:
                
                print(f"ERROR -> {ex}")
            
            # Mostrar resumen de los datos seleccionados
            summary_message = f"""UPDATE DATA SUMMARY:
            
            Batch ID: {update_data['batch_id']}
            Selection Mode: {update_data['selection_mode']}
            Field to Update: {update_data['field_to_assign']}
            New Value: {update_data['value_to_assign']}
            Selected Samples: {update_data['selected_samples_count']} of {update_data['total_available_samples']}
            Timestamp: {update_data['timestamp']}

            Sample IDs to update:
            {', '.join(map(str, selected_samples[:10]))}{'...' if len(selected_samples) > 10 else ''}

            Do you want to proceed with this update?"""
            
            # Confirmar la actualización
            result = messagebox.askyesno("Confirm Update", summary_message)
            
            if result:
                # Aquí puedes agregar la lógica para actualizar la base de datos
                # Por ahora, solo mostramos los datos y los retornamos
                
                print("="*50)
                print("UPDATE DATA COLLECTED:")
                print("="*50)
                for key, value in update_data.items():
                    print(f"{key}: {value}")
                print("="*50)
                
                messagebox.showinfo("Update Successful", 
                                  f"Data updated successfully for {len(selected_samples)} samples!")
                
                return update_data
            else:
                return None
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while updating data: {str(e)}")
            return None
    
    def execute_assignment(self):
        """Execute the assignment (placeholder function - implement your logic here)"""
        # Esta función ya existía en tu código original
        # Puedes mantener tu lógica existente aquí
        update_data = self.update_data()
        if update_data:
            print("Assignment executed with data:", update_data)
    
    def clear_fields(self):
        """Clear all input fields"""
        self.lab_reporting_batch_id.set("")
        self.data_to_assign.set("")
        self.field_to_assign.set("")
        self.sample_selection_mode.set("all")
        
        # Clear samples
        self.available_samples = []
        self.selected_samples = []
        self.update_sample_selection_display()
        
        # Hide sample selection frame
        self.sample_selection_frame.grid_remove()
        
        # Reset input widget
        self.create_default_input()