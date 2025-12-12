import tkinter as tk
from tkinter import ttk

class EditableTreeview:
    """
    Clase para manejar la edición de celdas en un Treeview
    """
    def __init__(self, tree, on_edit_callback=None, editable_columns=None):
        """
        Args:
            tree: El widget Treeview
            on_edit_callback: Función callback(item_id, column, old_value, new_value)
            editable_columns: Lista de columnas editables. Si es None, todas son editables
        """
        self.tree = tree
        self.on_edit_callback = on_edit_callback
        self.editable_columns = editable_columns
        self.entry_popup = None
        self.current_item = None
        self.current_column = None
        
        # Bind doble clic para editar
        self.tree.bind('<Double-Button-1>', self._on_double_click)
        
    def _on_double_click(self, event):
        """Maneja el doble clic en una celda"""
        region = self.tree.identify_region(event.x, event.y)
        if region != 'cell':
            return
            
        # Identificar item y columna
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if not item or not column:
            return
            
        # Convertir column de '#1' a index numérico
        column_index = int(column.replace('#', '')) - 1
        column_name = self.tree['columns'][column_index]
        
        # Verificar si la columna es editable
        if self.editable_columns and column_name not in self.editable_columns:
            return
            
        # No permitir editar la columna de checkbox 'Include'
        if column_name == 'Include':
            return
            
        self._create_entry_popup(item, column_name, column_index)
        
    def _create_entry_popup(self, item, column_name, column_index):
        """Crea el Entry widget para editar la celda"""
        # Obtener valor actual
        values = self.tree.item(item, 'values')
        if not values or column_index >= len(values):
            return
            
        current_value = values[column_index]
        
        # Guardar referencia
        self.current_item = item
        self.current_column = column_name
        
        # Obtener coordenadas de la celda
        x, y, width, height = self.tree.bbox(item, column_name)
        
        # Crear Entry widget
        self.entry_popup = tk.Entry(self.tree, width=width)
        self.entry_popup.insert(0, current_value)
        self.entry_popup.select_range(0, tk.END)
        self.entry_popup.focus()
        
        # Posicionar el Entry sobre la celda
        self.entry_popup.place(x=x, y=y, width=width, height=height)
        
        # Bindings
        self.entry_popup.bind('<Return>', self._on_enter_pressed)
        self.entry_popup.bind('<Escape>', self._on_escape_pressed)
        self.entry_popup.bind('<FocusOut>', self._on_focus_out)
        
    def _on_enter_pressed(self, event):
        """Guardar cambios al presionar Enter"""
        self._save_edit()
        
    def _on_escape_pressed(self, event):
        """Cancelar edición al presionar Escape"""
        self._cancel_edit()
        
    def _on_focus_out(self, event):
        """Guardar cambios al perder el foco"""
        self._save_edit()
        
    def _save_edit(self):
        """Guarda los cambios en el Treeview"""
        if not self.entry_popup:
            return
            
        new_value = self.entry_popup.get()
        
        # Obtener valores actuales
        values = list(self.tree.item(self.current_item, 'values'))
        column_index = self.tree['columns'].index(self.current_column)
        old_value = values[column_index]
        
        # Actualizar valor si cambió
        if new_value != old_value:
            values[column_index] = new_value
            self.tree.item(self.current_item, values=values)
            
            # Llamar callback si existe
            if self.on_edit_callback:
                self.on_edit_callback(
                    self.current_item,
                    self.current_column,
                    old_value,
                    new_value
                )
        
        self._cleanup()
        
    def _cancel_edit(self):
        """Cancela la edición"""
        self._cleanup()
        
    def _cleanup(self):
        """Limpia el Entry popup"""
        if self.entry_popup:
            self.entry_popup.destroy()
            self.entry_popup = None
        self.current_item = None
        self.current_column = None


