import tk


def create_splash_screen(self):
        """Crear la pantalla splash con validaciones mejoradas"""
        self.splash = tk.Toplevel(self.root)
        self.splash.title("SRL")
        self.splash.geometry("450x350")
        self.splash.configure(bg='#2c3e50')
        
        self.center_splash_window()
        self.splash.transient(self.root)
        self.splash.grab_set()
        self.splash.overrideredirect(True)
        
        # Frame principal con padding
        main_splash_frame = tk.Frame(self.splash, bg="#2c3e50")
        main_splash_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Logo
        self.setup_splash_logo(main_splash_frame)
        
        # Título mejorado
        title_label = tk.Label(
            main_splash_frame, 
            text="App", 
            font=('Century Ghotic', 14, 'bold'),
            fg='white',
            bg='#2c3e50',
            justify=tk.CENTER
        )
        title_label.pack(pady=(20, 5))
        
        # Subtítulo
        subtitle_label = tk.Label(
            main_splash_frame, 
            text="Data Management", 
            font=('Century Ghotic', 9),
            fg='#bdc3c7',
            bg='#2c3e50'
        )
        subtitle_label.pack(pady=(0, 25))
        
        # Barra de progreso
        self.setup_splash_progress(main_splash_frame)
        
        # Label de estado
        self.splash_status_label = tk.Label(
            main_splash_frame, 
            text="Initializing...", 
            font=('Century Ghotic', 9),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        self.splash_status_label.pack(pady=(15, 10))
        
        # Frame inferior para información
        bottom_frame = tk.Frame(main_splash_frame, bg='#2c3e50')
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # Información de versión
        version_label = tk.Label(
            bottom_frame, 
            text="Version 1.0.1", 
            font=('Century Ghotic', 8),
            fg='#95a5a6',
            bg='#2c3e50'
        )
        version_label.pack(side=tk.LEFT)
        
        # Información de conexión
        self.connection_info_label = tk.Label(
            bottom_frame, 
            text=f"DB: SRLFLORIDA", 
            font=('Century Ghotic', 8),
            fg='#95a5a6',
            bg='#2c3e50'
        )
        self.connection_info_label.pack(side=tk.RIGHT)