import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path

from BackEnd.Database.Queries.Select.select_samples import select_samples
from BackEnd.Database.Queries.Updates.update_assign_data import update_assign_data

class AssignData:

    def __init__(self, parent=None, selected_samples=None, selected_tests=None):
        BASE_DIR = Path(__file__).parent.resolve()
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Assign data")

        # Configuración de ventana
        window_width = 600
        window_height = 400
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.resizable(False, False)
        self.window.iconbitmap(BASE_DIR / "assets" / "logos" / "LOGO_SRL_FINAL.ico")

        # Datos seleccionados
        self.selected_samples = selected_samples or []
        self.selected_tests = selected_tests or []

        # Variables
        self.data_to_assign = tk.StringVar()
        self.field_to_assign = tk.StringVar()
        self.refresh_callback = None

        # Campos por tabla
        self.fields_samples = [
            "ClientSampleID", "Sampler", "DateCollected", "MatrixID",
            "LabAnalysisRefMethodID", "Temperature", "CollectMethod",
            "TotalContainers", "CoolerNumber"
        ]

        self.fields_sample_tests = [
            "AnalyteName", "Result", "ResultUnits", "LabQualifiers",
            "AnalyteType", "Test_Group", "Dilution", "ReportingBatch"
        ]

        # Determinar tabla automáticamente
        if self.selected_samples and not self.selected_tests:
            self.table_selection = tk.StringVar(value="Samples")
            self.table_locked = True
        elif self.selected_tests and not self.selected_samples:
            self.table_selection = tk.StringVar(value="Sample_Tests")
            self.table_locked = True
        else:
            self.table_selection = tk.StringVar(value="Samples")
            self.table_locked = False

        self.setup_ui()


    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = ttk.Label(main_frame, text="Asignar Datos a Muestras Seleccionadas",
                                font=("Century Gothic", 14, "bold"))
        title_label.pack(pady=(0, 10))

        # Info selección
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=10)

        if self.selected_samples:
            ttk.Label(info_frame, text=f"✓ {len(self.selected_samples)} Samples seleccionadas",
                      foreground="green", font=("Century Gothic", 10)).pack(anchor=tk.W)
        if self.selected_tests:
            ttk.Label(info_frame, text=f"✓ {len(self.selected_tests)} Sample Tests seleccionados",
                      foreground="green", font=("Century Gothic", 10)).pack(anchor=tk.W)

        # Separador
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=15)

        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)

        row = 0

        # Solo mostrar selector de tabla si tiene ambas seleccionadas
        if not self.table_locked:
            ttk.Label(form_frame, text="Tabla a modificar:",
                      font=("Century Gothic", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=8, padx=(0, 10))
            table_combo = ttk.Combobox(form_frame, textvariable=self.table_selection,
                                       values=["Samples", "Sample_Tests"],
                                       state="readonly", width=25)
            table_combo.grid(row=row, column=1, sticky=tk.W, pady=8)
            table_combo.bind('<<ComboboxSelected>>', self.on_table_selection_change)
            row += 1
        else:
            # Mostrar tabla bloqueada
            ttk.Label(form_frame, text="Tabla:",
                      font=("Century Gothic", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=8, padx=(0, 10))
            ttk.Label(form_frame, text=self.table_selection.get(),
                      foreground="blue", font=("Century Gothic", 10)).grid(row=row, column=1, sticky=tk.W, pady=8)
            row += 1

        # Campo a modificar
        ttk.Label(form_frame, text="Campo a modificar:",
                  font=("Century Gothic", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=8, padx=(0, 10))
        self.field_combo = ttk.Combobox(form_frame, textvariable=self.field_to_assign,
                                        state="readonly", width=25)
        self.field_combo.grid(row=row, column=1, sticky=tk.W, pady=8)
        row += 1

        # Nuevo valor
        ttk.Label(form_frame, text="Nuevo valor:",
                  font=("Century Gothic", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=8, padx=(0, 10))
        value_entry = ttk.Entry(form_frame, textvariable=self.data_to_assign, width=27)
        value_entry.grid(row=row, column=1, sticky=tk.W, pady=8)

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="✓ Actualizar",
                   command=self.update_data,
                   width=15, cursor="hand2").pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="⟲ Limpiar",
                   command=self.clear_fields,
                   width=15, cursor="hand2").pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="✕ Cerrar",
                   command=self.window.destroy,
                   width=15, cursor="hand2").pack(side=tk.LEFT, padx=5)

        # Inicializar combobox
        self.update_comboboxes()

    def on_table_selection_change(self, event=None):
        """Cuando cambia la tabla, actualizar los campos disponibles"""
        self.field_to_assign.set("")
        self.update_comboboxes()

    def update_comboboxes(self):
        """Actualizar los campos según la tabla seleccionada"""
        if self.table_selection.get() == "Samples":
            self.field_combo['values'] = self.fields_samples
        else:
            self.field_combo['values'] = self.fields_sample_tests

    def set_refresh_callback(self, callback):
        """Establecer callback para refrescar datos después de actualizar"""
        self.refresh_callback = callback

    def update_data(self):
        """Ejecutar la actualización"""
        try:
            if not self.field_to_assign.get():
                messagebox.showwarning("Error", "Selecciona un campo")
                return

            if not self.data_to_assign.get().strip():
                messagebox.showwarning("Error", "Ingresa un valor")
                return

            # Obtener IDs según la tabla seleccionada
            table = self.table_selection.get()

            if table == "Samples":
                if not self.selected_samples:
                    messagebox.showwarning("Error", "No hay samples seleccionadas")
                    return
                # LabSampleID está en posición 3 (índice [3])
                ids_to_update = [s['LabSampleID'] for s in self.selected_samples]
            else:  # Sample_Tests
                if not self.selected_tests:
                    messagebox.showwarning("Error", "No hay sample tests seleccionados")
                    return
                # LabSampleID está en posición 4 (índice [4])
                ids_to_update = [s['SampleTestsID'] for s in self.selected_tests]

            # Confirmar
            confirm = messagebox.askyesno(
                "Confirmar",
                f"¿Actualizar {len(ids_to_update)} registros?\n\n"
                f"Tabla: {table}\n"
                f"Campo: {self.field_to_assign.get()}\n"
                f"Nuevo valor: '{self.data_to_assign.get()}'\n\n"
                f"IDs: {', '.join(ids_to_update[:5])}{'...' if len(ids_to_update) > 5 else ''}"
            )

            if confirm:
                success = update_assign_data(
                    table,
                    self.field_to_assign.get(),
                    ids_to_update,
                    self.data_to_assign.get()
                )

                if success:
                    messagebox.showinfo("Éxito", f"{len(ids_to_update)} registros actualizados correctamente")
                    if self.refresh_callback:
                        self.refresh_callback()
                    self.window.destroy()
                else:
                    messagebox.showerror("Error", "No se pudieron actualizar los datos")

        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

    def clear_fields(self):
        """Limpiar todos los campos"""
        self.lab_reporting_batch_id.set("")
        self.data_to_assign.set("")
        self.field_to_assign.set("")
        self.table_selection.set("Samples")
        self.update_comboboxes()