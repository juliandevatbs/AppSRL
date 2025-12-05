from pathlib import Path
import sys
import threading
import tkinter as tk
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor

from BackEnd.Config.fields import INITIAL_DATA_FILTERS, INITIAL_DATA_SAMPLE_TABLE
from BackEnd.Database.Queries.Select.SelectInitialData import SelectInitialData
from BackEnd.Processes.DataFormatters.data_formatter import data_formatter
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

    def _setup_ui(self):
        self.status_label = ttk.Label(self, text="Ready - Use 'View Data' to load information")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        filter_container, self.filter_frame = self.filter_manager.create_filter_frame(self)
        self._create_actions_menu(self.filter_frame)

        results_frame = ttk.Frame(self)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        results_notebook = ttk.Notebook(results_frame)
        results_notebook.pack(fill=tk.BOTH, expand=True)

        self._setup_tables(results_notebook)
        self._setup_action_buttons()

    def _setup_tables(self, notebook):
        def col(w, a, t, s=False): return {'width': w, 'anchor': a, 'text': t, 'stretch': s}

        table1_columns = {
            'Include': col(150, tk.CENTER, 'Include'),
            'itemID': col(150, tk.CENTER, 'itemID'),
            'LabReportingBatchID': col(300, tk.CENTER, 'LabReportingBatchID'),
            'LabSampleID': col(300, tk.W, 'LabSampleID'),
            'ClientSampleID': col(400, tk.CENTER, 'ClientSampleID'),
            'Sampler': col(400, tk.CENTER, 'Sampler'),
            'Datecollected': col(400, tk.CENTER, 'Datecollected'),
            'MatrixID': col(400, tk.CENTER, 'MatrixID'),
            'Temperature': col(250, tk.CENTER, 'Temperature'),
            'ShippingBatchID': col(300, tk.CENTER, 'ShippingBatchID'),
            'CollectMethod': col(400, tk.CENTER, 'CollectMethod'),
            'CollectionAgency': col(400, tk.CENTER, 'CollectionAgency'),
            'AdaptMatrixID': col(400, tk.CENTER, 'AdaptMatrixID'),
            'LabID': col(250, tk.CENTER, 'LabID'),
        }

        table2_columns = {
            'Include': col(120, tk.CENTER, 'Include'),
            'SampleTestsID': col(300, tk.CENTER, 'SampleTestsID'),
            'ClientSampleID': col(400, tk.CENTER, 'ClientSampleID'),
            'LabAnalysisRefMethodID': col(400, tk.CENTER, 'LabAnalysisRefMethodID'),
            'LabSampleID': col(300, tk.W, 'LabSampleID'),
            'AnalyteName': col(400, tk.CENTER, 'AnalyteName'),
            'Result': col(250, tk.CENTER, 'Result'),
            'ResultUnits': col(300, tk.CENTER, 'ResultUnits'),
            'DetectionLimit': col(250, tk.CENTER, 'DetectionLimit'),
            'Dilution': col(250, tk.CENTER, 'Dilution'),
            'ReportingLimit': col(250, tk.CENTER, 'ReportingLimit'),
            'ProjectName': col(350, tk.CENTER, 'ProjectName'),
            'DateCollected': col(400, tk.CENTER, 'DateCollected'),
            'MatrixID': col(300, tk.CENTER, 'MatrixID'),
            'AnalyteType': col(300, tk.CENTER, 'AnalyteType'),
            'LabReportingBatchID': col(400, tk.CENTER, 'LabReportingBatchID'),
            'Notes': col(400, tk.CENTER, 'Notes', s=True),
            'Sampler': col(400, tk.CENTER, 'Sampler'),
            'Analyst': col(400, tk.CENTER, 'Analyst'),
        }

        t1_frame, self.table1 = self.table_manager.create_table(notebook, 'table1', table1_columns)
        notebook.add(t1_frame, text="Sample Data")

        t2_frame, self.table2 = self.table_manager.create_table(notebook, 'table2', table2_columns)
        notebook.add(t2_frame, text="Sample Tests")

        self.table1.bind('<ButtonRelease-1>', lambda e: self._on_table_click(e, 'table1'))
        self.table2.bind('<ButtonRelease-1>', lambda e: self._on_table_click(e, 'table2'))

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

        # Esto ES asíncrono porque DataLoader crea el thread
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

    def _setup_action_buttons(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.X, padx=5, pady=5)

        self.report_btn = ttk.Button(frame, text="Generate Report", command=self._generate_report_async)
        self.report_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(frame, text="Clear Results", command=self._clear_results).pack(side=tk.RIGHT, padx=5)

    def _create_actions_menu(self, parent):
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
        ))

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
