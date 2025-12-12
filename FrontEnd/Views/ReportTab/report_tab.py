from pathlib import Path
import sys
import threading
import tkinter as tk
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor

from BackEnd.Config.fields import INITIAL_DATA_FILTERS, INITIAL_DATA_SAMPLE_TABLE
from BackEnd.Database.Queries.Insert.InsertSample import InsertSample
from BackEnd.Database.Queries.Insert.InsertSampleTest import InsertSampleTest
from BackEnd.Database.Queries.Select.SelectInitialData import SelectInitialData
from BackEnd.Database.Queries.Updates.UpdateSample import UpdateSample
from BackEnd.Database.Queries.Updates.UpdateSampleTest import UpdateSampleTest
from BackEnd.Processes.DataFormatters.data_formatter import data_formatter
from FrontEnd.Views.ReportTab.EditableTreeView import EditableTreeview
from FrontEnd.Views.ReportTab.table_manager import TableManager
from FrontEnd.Views.ReportTab.filter_manager import FilterManager
from FrontEnd.Views.ReportTab.data_loader import DataLoader

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


class ReportTab(ttk.Frame):
    def __init__(self, parent, auto_load=False):
        super().__init__(parent)
        self.root = parent

        self._auto_load = auto_load
        self._load_started = False
        self._load_in_progress = False
        self._load_completed = False

        self.current_batch_id = None
        self.data_loaded = False
        self.executor = ThreadPoolExecutor(max_workers=2)

        self.table_manager = TableManager(self)
        self.filter_manager = FilterManager(self, self.update_status)
        self.data_loader = DataLoader(self, self.update_status)
        self.instance_select_initial_data = SelectInitialData()

        self.filters_initial_data = None
        self.sample_initial_data = None

        self._setup_ui()
        self.filter_manager.set_view_data_callback(self.view_data_wrapper)
        self.filter_manager.set_on_filters_ready_callback(self.on_filters_ready)

        if auto_load:
            self.after(100, self.initialize_data)
        
        self.insert_sample =  InsertSample()
        self.insert_sample_test = InsertSampleTest()
    

    def _setup_ui(self):
        self.status_label = ttk.Label(self, text="Ready - Use 'View Data' to load information")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        filter_container, self.filter_frame = self.filter_manager.create_filter_frame(self)
        #self._create_actions_menu(self.filter_frame)

        results_frame = ttk.Frame(self)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        results_notebook = ttk.Notebook(results_frame)
        results_notebook.pack(fill=tk.BOTH, expand=True)

        self._setup_tables(results_notebook)
        #self._setup_action_buttons()

    def _setup_tables(self, notebook):
        def col(w, a, t, s=False): return {'width': w, 'anchor': a, 'text': t, 'stretch': s}

        table1_columns = {
            'Include': col(50, tk.CENTER, 'Include'),
            'ItemID': col(50, tk.CENTER, 'ItemID'),
            'LabReportingBatchID': col(150, tk.CENTER, 'LabReportingBatchID'),
            'LabSampleID': col(150, tk.CENTER, 'LabSampleID'),
            'ClientSampleID': col(200, tk.CENTER, 'ClientSampleID'),
            'Sampler': col(200, tk.CENTER, 'Sampler'),
            'Datecollected': col(200, tk.CENTER, 'Datecollected'),
            'MatrixID': col(300, tk.CENTER, 'MatrixID'),
            'Temperature': col(50, tk.CENTER, 'Temperature'),
            'ShippingBatchID': col(150, tk.CENTER, 'ShippingBatchID'),
            'CollectMethod': col(50, tk.CENTER, 'CollectMethod'),
            'CollectionAgency': col(200, tk.CENTER, 'CollectionAgency'),
            'AdaptMatrixID': col(100, tk.CENTER, 'AdaptMatrixID'),
            'LabID': col(150, tk.CENTER, 'LabID'),
        }

        table2_columns = {
            'Include': col(50, tk.CENTER, 'Include'),
            'SampleTestsID': col(150, tk.CENTER, 'SampleTestsID'),
            'ClientSampleID': col(200, tk.CENTER, 'ClientSampleID'),
            'LabAnalysisRefMethodID': col(300, tk.CENTER, 'LabAnalysisRefMethodID'),
            'LabSampleID': col(300, tk.CENTER, 'LabSampleID'),
            'AnalyteName': col(250, tk.CENTER, 'AnalyteName'),
            'Result': col(150, tk.CENTER, 'Result'),
            'ResultUnits': col(150, tk.CENTER, 'ResultUnits'),
            'DetectionLimit': col(150, tk.CENTER, 'DetectionLimit'),
            'Dilution': col(150, tk.CENTER, 'Dilution'),
            'ReportingLimit': col(150, tk.CENTER, 'ReportingLimit'),
            'ProjectName': col(150, tk.CENTER, 'ProjectName'),
            'DateCollected': col(200, tk.CENTER, 'DateCollected'),
            'MatrixID': col(150, tk.CENTER, 'MatrixID'),
            'AnalyteType': col(150, tk.CENTER, 'AnalyteType'),
            'LabReportingBatchID': col(200, tk.CENTER, 'LabReportingBatchID'),
            'Notes': col(200, tk.CENTER, 'Notes', s=True),
            'Sampler': col(200, tk.CENTER, 'Sampler'),
            'Analyst': col(200, tk.CENTER, 'Analyst'),
        }

        t1_frame, self.table1 = self.table_manager.create_table(notebook, 'table1', table1_columns)
        notebook.add(t1_frame, text="Sample Data")

        t2_frame, self.table2 = self.table_manager.create_table(notebook, 'table2', table2_columns)
        notebook.add(t2_frame, text="Sample Tests")

        self.table1.bind('<ButtonRelease-1>', lambda e: self._on_table_click(e, 'table1'))
        self.table2.bind('<ButtonRelease-1>', lambda e: self._on_table_click(e, 'table2'))
        
        self._setup_editable_tables()

    def _setup_editable_tables(self):
        """
        Configura las tablas como editables
        Llamar después de crear las tablas en _setup_tables()
        """
        
        # Instanciar las clases de actualización
        self.update_sample = UpdateSample()
        self.update_sample_test = UpdateSampleTest()
        
        # Define qué columnas son editables en Sample Data
        editable_cols_table1 = [
            'ItemID',
            'ClientSampleID',
            'Sampler',
            'Temperature',
            'CollectMethod',
            'CollectionAgency',
            'DateCollected',
            'MatrixID',
            'ShippingBatchID',
            'LabSampleID',
            'LocationCode',
            'AdaptMatrixID',
            'ProgramType'
        ]
        
        # Define qué columnas son editables en Sample Tests
        editable_cols_table2 = [
            'Result',
            'ResultUnits',
            'DetectionLimit',
            'Dilution',
            'ReportingLimit',
            'Notes',
            'Analyst',
            'LabQualifiers',
            'PercentMoisture',
            'PercentRecovery',
            'Sampler',
            'AnalyteType',
            'AnalyteName'
        ]
        
        # Configurar table1 (Sample Data) como editable
        self.editable_table1 = EditableTreeview(
            self.table1,
            on_edit_callback=self._on_table1_edit,
            editable_columns=editable_cols_table1
        )
        
        # Configurar table2 (Sample Tests) como editable
        self.editable_table2 = EditableTreeview(
            self.table2,
            on_edit_callback=self._on_table2_edit,
            editable_columns=editable_cols_table2
        )
    
    def add_new_sample(self):
        """
        Crea un nuevo sample básico para el Work Order actual
        El usuario editará los campos en la tabla
        """
        # Obtener el Work Order actual del FilterManager
        work_order = self.filter_manager.widgets.get('LabReportingBatchID')
        if not work_order:
            self.update_status("Error: No Work Order selected", error=True)
            return
        
        wo_value = work_order.get().strip()
        if not wo_value:
            self.update_status("Error: Please select a Work Order first", error=True)
            return
        
        try:
            wo_int = int(wo_value)
        except ValueError:
            self.update_status("Error: Invalid Work Order", error=True)
            return
        
        self.update_status(f"Creating new sample for WO {wo_int}...")
        
        def worker():
            try:
                new_lab_sample_id = self.insert_sample.create_empty_sample(wo_int)
                
                if new_lab_sample_id:
                    self.after(0, lambda: self._on_sample_created(new_lab_sample_id))
                else:
                    self.after(0, lambda: self.update_status("Error creating sample", error=True))
            except Exception as e:
                print(f"Error in add_new_sample worker: {e}")
                import traceback
                traceback.print_exc()
                self.after(0, lambda: self.update_status(f"Error: {e}", error=True))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()


    def _on_sample_created(self, lab_sample_id):
     
        self.update_status(f" {lab_sample_id} created Reloading data...")
        
        work_order = self.filter_manager.widgets.get('LabReportingBatchID')
        if work_order:
            wo_value = work_order.get().strip()
            try:
                wo_int = int(wo_value)
                self.filter_manager.load_analytes_async(wo_int)
            except ValueError:
                pass
    
        # Luego recargar las tablas
        self.after(500, self.load_table_data)


    def add_new_sample_test(self):
       
        work_order = self.filter_manager.widgets.get('LabReportingBatchID')
        if not work_order:
            self.update_status("Error: No Work Order selected", error=True)
            return
        
        wo_value = work_order.get().strip()
        if not wo_value:
            self.update_status("Error: Please select a Work Order first", error=True)
            return
        
        try:
            wo_int = int(wo_value)
        except ValueError:
            self.update_status("Error: Invalid Work Order", error=True)
            return
        
        selected_lab_sample_id = None
        if 'LabSampleID' in self.filter_manager.widgets:
            lab_sample_widget = self.filter_manager.widgets['LabSampleID']
            lab_sample_value = lab_sample_widget.get().strip()
            
            
            # Si está seleccionado y no es 'All', usarlo
            if lab_sample_value == 'All' or not lab_sample_value:
                
                self.update_status("Error: Please select a specific LabSampleID (not 'All')", error=True)
                return
            
            selected_lab_sample_id = lab_sample_value
        
        samples = self.insert_sample_test.get_samples_for_work_order(wo_int)
        if not samples:
            self.update_status("Error: No samples found. Create a sample first", error=True)
            return

        if not selected_lab_sample_id:
            self.update_status("Error: Please select a specific LabSampleID from the dropdown", error=True)
            return
        
        
        if selected_lab_sample_id:
            sample_ids = [s[0] for s in samples]
            if selected_lab_sample_id not in sample_ids:
                self.update_status(f"Error: Sample {selected_lab_sample_id} not found", error=True)
                return
        
        status_msg = f"Creating new test for WO {wo_int}"
        if selected_lab_sample_id:
            status_msg += f" (Sample: {selected_lab_sample_id})"
        self.update_status(status_msg + "...")
        
        def worker():
            try:
                new_test_id = self.insert_sample_test.create_empty_test(wo_int, selected_lab_sample_id)
                
                if new_test_id:
                    self.after(0, lambda: self._on_test_created(new_test_id))
                else:
                    self.after(0, lambda: self.update_status("Error creating test", error=True))
            except Exception as e:
                print(f"Error in add_new_sample_test worker: {e}")
                import traceback
                traceback.print_exc()
                self.after(0, lambda: self.update_status(f"Error: {e}", error=True))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()


    def _on_test_created(self, test_id):
      
        self.update_status(f"Test {test_id} created Reloading data...")
        
        work_order = self.filter_manager.widgets.get('LabReportingBatchID')
        if work_order:
            wo_value = work_order.get().strip()
            try:
                wo_int = int(wo_value)
                self.filter_manager.load_analytes_async(wo_int)
            except ValueError:
                pass
        
        self.after(500, self.load_table_data)
    
    def _on_data_edited(self):
      
        work_order = self.filter_manager.widgets.get('LabReportingBatchID')
        if work_order:
            wo_value = work_order.get().strip()
            try:
                wo_int = int(wo_value)
                self.filter_manager.load_analytes_async(wo_int)
            except ValueError:
                pass
        
        self.after(300, self.load_table_data)
    
    def _on_table1_edit(self, item_id, column, old_value, new_value):
        """
        Callback cuando se edita una celda en table1 (Sample Data)
        CORREGIDO: Usa LabSampleID como identificador único
        
        Args:
            item_id: ID del item en el Treeview
            column: Nombre de la columna editada
            old_value: Valor anterior
            new_value: Valor nuevo
        """
        try:
            # Obtener todos los valores del registro
            values = self.table1.item(item_id, 'values')
            
            # Estructura de columnas en table1:
            # [0]=Include, [1]=ItemID, [2]=LabReportingBatchID, [3]=LabSampleID, [4]=ClientSampleID...
            lab_sample_id = values[3]  # LabSampleID (ej: '2410001-001')
            
            print(f"[EDIT] Sample LabSampleID: {lab_sample_id}")
            print(f"       Campo: {column}")
            print(f"       {old_value} -> {new_value}")
            
            # Validar el campo si es necesario
            if not self._validate_sample_field(column, new_value):
                self.update_status(f"Error: Invalid value for {column}", error=True)
                self._revert_cell_value(self.table1, item_id, column, old_value)
                return
            
            # Actualizar en la base de datos usando LabSampleID
            success = self.update_sample.update_field(lab_sample_id, column, new_value)
            
            if success:
                self.update_status(f"✓ Updated {column} for Sample {lab_sample_id}")
                self._on_data_edited()
            else:
                # Si falla, revertir el cambio en el Treeview
                self.update_status(f"Failed to update {column}", error=True)
                self._revert_cell_value(self.table1, item_id, column, old_value)
                
        except Exception as e:
            print(f"Error in _on_table1_edit: {e}")
            import traceback
            traceback.print_exc()
            self.update_status(f"Error: {e}", error=True)
            self._revert_cell_value(self.table1, item_id, column, old_value)


    def _on_table2_edit(self, item_id, column, old_value, new_value):
        """
        Callback cuando se edita una celda en table2 (Sample Tests)
        
        Args:
            item_id: ID del item en el Treeview
            column: Nombre de la columna editada
            old_value: Valor anterior
            new_value: Valor nuevo
        """
        try:
            # Obtener todos los valores del registro
            values = self.table2.item(item_id, 'values')
            
            # Estructura de columnas en table2:
            # [0]=Include, [1]=SampleTestsID, [2]=ClientSampleID...
            sample_tests_id = values[1]  # SampleTestsID
            
            print(f"[EDIT] SampleTest ID: {sample_tests_id}")
            print(f"       Campo: {column}")
            print(f"       {old_value} -> {new_value}")
            
            # Validar el campo
            if not self._validate_sample_test_field(column, new_value):
                self.update_status(f"Error: Invalid value for {column}", error=True)
                self._revert_cell_value(self.table2, item_id, column, old_value)
                return
            
            # Actualizar en la base de datos usando SampleTestsID
            success = self.update_sample_test.update_field(sample_tests_id, column, new_value)
            
            if success:
                self.update_status(f"✓ Updated {column} for Test {sample_tests_id}")
                self._on_data_edited()
            else:
                # Si falla, revertir el cambio
                self.update_status(f"Failed to update {column}", error=True)
                self._revert_cell_value(self.table2, item_id, column, old_value)
                
        except Exception as e:
            print(f"Error in _on_table2_edit: {e}")
            import traceback
            traceback.print_exc()
            self.update_status(f"Error: {e}", error=True)
            self._revert_cell_value(self.table2, item_id, column, old_value)


    def _validate_sample_field(self, column, value):
        """
        Valida el valor de un campo de Sample antes de guardarlo
        
        Args:
            column: Nombre del campo
            value: Valor a validar
            
        Returns:
            bool: True si el valor es válido
        """
        # Permitir valores vacíos
        if value == '' or value is None:
            return True
        
        # Validar campos específicos si es necesario
        if column == 'Temperature':
            # Puede ser texto o número (ej: "1.5", "NA")
            return True
        
        # Por defecto, aceptar cualquier valor de texto
        return True


    def _validate_sample_test_field(self, column, value):
        """
        Valida el valor de un campo de SampleTest antes de guardarlo
        
        Args:
            column: Nombre del campo
            value: Valor a validar
            
        Returns:
            bool: True si el valor es válido
        """
        # Permitir valores vacíos
        if value == '' or value is None or str(value).strip() == '':
            return True
        
        # Campos que deben ser numéricos (float en la BD)
        numeric_fields = [
            'Result', 
            'DetectionLimit', 
            'Dilution', 
            'ReportingLimit',
            'PercentMoisture',
            'PercentRecovery',
            'RelativePercentDifference',
            'QCSpikeAdded'
        ]
        
        if column in numeric_fields:
            try:
                # Intentar convertir a float
                float(value)
                return True
            except ValueError:
                print(f"Validation failed: {column} debe ser un número, recibido: '{value}'")
                return False
        
        # Para campos de texto (Notes, Analyst, ResultUnits, etc.)
        return True


    def _revert_cell_value(self, table, item_id, column, old_value):
        """
        Revierte el valor de una celda en caso de error
        
        Args:
            table: El Treeview (self.table1 o self.table2)
            item_id: ID del item
            column: Nombre de la columna
            old_value: Valor original a restaurar
        """
        try:
            values = list(table.item(item_id, 'values'))
            column_index = table['columns'].index(column)
            values[column_index] = old_value
            table.item(item_id, values=values)
            print(f"[REVERT] Reverted {column} to: {old_value}")
        except Exception as e:
            print(f"Error reverting value: {e}")


    def initialize_data(self):
        try:
            self.update_status("Loading initial data...")
            self.filter_manager.load_work_orders()
        except Exception as e:
            self.update_status(f"Error initializing data: {e}", error=True)

    def on_filters_ready(self):
        self.after(150, self.load_table_data)

    def load_table_data(self):
        if self._load_in_progress:
            return
        try:
            batch_id, filters = self.filter_manager.view_data()
            if not batch_id:
                return
            self._load_in_progress = True
            self.update_status(f"Loading data for WO: {batch_id}...")
            self._load_samples_and_tests_async(batch_id, filters)
        except Exception as e:
            self._load_in_progress = False
            self.update_status(f"Error loading table data: {e}", error=True)

    def _load_samples_and_tests_async(self, batch_id, filters):
        """Cargar samples y tests usando DataLoader"""

        def on_data_loaded(samples, tests, error):
            if error:
                self.update_status(f"Error: {error}", error=True)
                self._set_load_done()
                return

            self._populate_tables(samples or [], tests or [])

        # Esto es asíncrono porque DataLoader crea el thread
        self.data_loader.load_data_async(batch_id, filters, on_data_loaded)


    # This methods inserts the data that comes
    def _populate_tables(self, samples, tests):

        try:

            # Clean tables

            for child in self.table1.get_children():

                self.table1.delete(child)

            for child in self.table2.get_children():

                self.table2.delete(child)

            # Insert sample data
            for row in samples:

                try:

                    if isinstance(row, (list, tuple)):

                        values = ('☐',) + tuple(row)

                    elif isinstance(row, dict):

                        values = ('☐',) + tuple(row.values())

                    self.table1.insert('', 'end', values=values)

                except Exception as e:

                    print(f"Error inserting sample: {e}")

            # Insert sample tests
            for row in tests:

                try:

                    if isinstance(row, (list, tuple)):

                        values=('☐',) + tuple(row)

                    elif isinstance(row, dict):

                        values=('☐',) + tuple(row.values())

                    self.table2.insert('', 'end', values=values)

                except Exception as e:
                    print(f"Error inserting test: {e}")

            # Update status
            self.data_loaded = True

            self.update_status(f"Loaded {len(samples)} samples and {len(tests)} tests")

        except Exception as e:
            self.update_status(f"Error populating tables: {e}", error=True)
        finally:
            self._set_load_done()

    def _set_load_done(self):
        self._load_in_progress = False
        self._load_completed = True

    def _on_table_click(self, event, table_name):
        result = self.table_manager.handle_checkbox_click(event, table_name)
        if result:
            lab_sample_id, action = result
            self.update_status(f"Sample {action}: {lab_sample_id}")

    """def _setup_action_buttons(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.X, padx=5, pady=5)

        self.report_btn = ttk.Button(frame, text="Generate Report", command=self._generate_report_async)
        self.report_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(frame, text="Clear Results", command=self._clear_results).pack(side=tk.RIGHT, padx=5)"""

    """def _create_actions_menu(self, parent):
        import tkinter.font as tkFont
        self.actions_button = ttk.Button(parent, text="☰ Actions", cursor="hand2", width=20)
        self.actions_button.grid(row=1, column=12, padx=2)
        self.actions_menu = tk.Menu(parent, tearoff=0, font=tkFont.Font(size=9))

        actions = [
            ("Create Sample", self._show_sample_wizard),
            ("Create Sample Tests", self._show_sample_test_wizard),
            ("-", None),
            ("Create QC", self._show_create_qc),
            ("Assign Data", self._show_assign_data)
        ]
        for label, cmd in actions:
            if label == "-":
                self.actions_menu.add_separator()
            else:
                self.actions_menu.add_command(label=label, command=cmd)

        self.actions_button.configure(command=lambda: self.actions_menu.post(
            self.actions_button.winfo_rootx(),
            self.actions_button.winfo_rooty() + self.actions_button.winfo_height()
        ))"""

    def update_status(self, message, error=False):
        self.status_label.config(text=message, foreground='red' if error else 'black')

    def _clear_results(self):
        self.table_manager.clear_table('table1')
        self.table_manager.clear_table('table2')
        self.current_batch_id = None
        self.data_loaded = False
        self.update_status("Results cleared")

    def view_data_wrapper(self):
        self.load_table_data()

    def _generate_report_async(self):
        pass

    def _show_sample_wizard(self):
        pass

    def _show_sample_test_wizard(self):
        pass

    def _show_create_qc(self):
        pass

    def _show_assign_data(self):
        pass

    def load_initial_data_async(self):
        if not self._load_started:
            self._load_started = True
            self.initialize_data()
