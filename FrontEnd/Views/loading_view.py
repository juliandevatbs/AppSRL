from pathlib import Path
import threading
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from FrontEnd.Styles.config_styles import configure_styles
from BackEnd.Database.General.get_connection import DatabaseConnection


class LoadingView:
    def __init__(self, root, logo_path=None, app_instance=None):
        self.root = root
        self.file_path = logo_path
        self.app_instance = app_instance
        self.db_connection = None
        self.db_config = "DB_ACTIVE_CONFIG"

        self.style = ttk.Style()
        configure_styles(self.style)
        self.add_custom_styles()

        self.splash = None
        self.splash_logo_image = None
        self.splash_progress_bar = None
        self.splash_status_label = None

    def create_splash_screen(self):
        azul_fondo = "#1a365d"
        self.splash = tk.Toplevel(self.root)
        self.splash.title("SRL")
        self.splash.geometry("450x300")
        self.splash.configure(bg=azul_fondo)

        self.center_splash_window()
        self.splash.transient(self.root)
        self.splash.grab_set()
        self.splash.overrideredirect(True)

        main_frame = tk.Frame(self.splash, bg=azul_fondo)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.setup_splash_logo(main_frame, azul_fondo)

        title_label = tk.Label(
            main_frame,
            text="SRL",
            fg="white",
            bg=azul_fondo,
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(10, 5))

        subtitle_label = tk.Label(
            main_frame,
            text="Data Management System",
            fg="white",
            bg=azul_fondo,
            font=("Arial", 10)
        )
        subtitle_label.pack(pady=(0, 15))

        self.setup_splash_progress(main_frame)

        self.splash_status_label = tk.Label(
            main_frame,
            text="Initializing...",
            fg="white",
            bg=azul_fondo,
            font=("Arial", 9)
        )
        self.splash_status_label.pack(pady=(10, 5))

        bottom_frame = tk.Frame(main_frame, bg=azul_fondo)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        version_label = tk.Label(bottom_frame, text="Version 1.0.1", fg="#cccccc", bg=azul_fondo, font=("Arial", 8))
        version_label.pack(side=tk.LEFT)

        connection_label = tk.Label(bottom_frame, text="DB: SRLFLORIDA", fg="#cccccc", bg=azul_fondo, font=("Arial", 8))
        connection_label.pack(side=tk.RIGHT)

    def start_loading_sequence(self):
        def loading_thread():
            try:
                self.safe_update_progress(10, "Initializing system...")
                time.sleep(0.5)

                self.safe_update_progress(30, "Loading core modules...")
                time.sleep(0.5)

                self.safe_update_progress(50, "Testing database connection...")
                db = DatabaseConnection()
                success, message = db.test_connection()

                if not success:
                    self.safe_update_progress(50, "Database connection failed!")
                    time.sleep(1)
                    self.root.after(0, lambda: self.show_connection_error(message))
                    return

                self.db_connection = db.get_conn()
                self.safe_update_progress(70, "Database connection established!")
                time.sleep(0.6)

                self.safe_update_progress(85, "Setting up interface...")
                if self.app_instance:
                    self.root.after(0, lambda: configure_styles(self.app_instance.style))
                time.sleep(0.5)

                self.safe_update_progress(95, "Configuring components...")
                if self.app_instance:
                    self.root.after(0, self.app_instance.setup_main_interface)
                time.sleep(0.6)

                self.safe_update_progress(100, "Ready!")
                time.sleep(0.7)

                self.root.after(0, self.close_splash_and_show_main)

            except Exception as e:
                error_msg = f"Initialization error: {str(e)}"
                self.safe_update_progress(0, "Initialization failed!")
                self.root.after(0, lambda: self.show_connection_error(error_msg))

        thread = threading.Thread(target=loading_thread, daemon=True)
        thread.start()

    def safe_update_progress(self, progress, status_text):
        self.root.after(0, lambda: self.update_splash_progress(progress, status_text))

    def show_connection_error(self, error_message):
        if hasattr(self, 'splash') and self.splash.winfo_exists():
            self.splash.destroy()

        self.root.deiconify()

        error_win = tk.Toplevel(self.root)
        error_win.title("Database Connection Error")
        error_win.geometry("450x280")
        error_win.configure(bg='#1a365d')
        error_win.transient(self.root)
        error_win.grab_set()

        self.center_window(error_win, 450, 280)

        main_frame = tk.Frame(error_win, bg='#1a365d')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        error_icon = tk.Label(main_frame, text="⚠️", fg="white", bg='#1a365d', font=("Arial", 24))
        error_icon.pack(pady=(5, 10))

        title_label = tk.Label(main_frame, text="Database Connection Failed", fg="white", bg='#1a365d', font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))

        error_text = tk.Text(
            main_frame,
            height=5,
            width=50,
            bg="#2d4a66",
            fg='white',
            font=('Arial', 9),
            wrap=tk.WORD,
            relief="flat",
            bd=1
        )
        error_text.pack(pady=(0, 15))
        error_text.insert(tk.END, error_message)
        error_text.configure(state=tk.DISABLED)

        btn_frame = tk.Frame(main_frame, bg='#1a365d')
        btn_frame.pack()

        retry_btn = tk.Button(btn_frame, text="Retry Connection", bg="#4a90e2", fg="white", font=("Arial", 9, "bold"),
                             relief="flat", padx=15, pady=5, command=lambda: self.retry_connection(error_win))
        retry_btn.pack(side=tk.LEFT, padx=5)

        config_btn = tk.Button(btn_frame, text="Change Config", bg="#f5a623", fg="white", font=("Arial", 9, "bold"),
                              relief="flat", padx=15, pady=5, command=lambda: self.show_config_dialog(error_win))
        config_btn.pack(side=tk.LEFT, padx=5)

        exit_btn = tk.Button(btn_frame, text="Exit Application", bg="#d0021b", fg="white", font=("Arial", 9, "bold"),
                            relief="flat", padx=15, pady=5, command=self.root.quit)
        exit_btn.pack(side=tk.LEFT, padx=5)

    def retry_connection(self, error_window):
        error_window.destroy()
        self.root.withdraw()
        self.create_splash_screen()
        self.start_loading_sequence()

    def show_config_dialog(self, error_window):
        config_win = tk.Toplevel(error_window)
        config_win.title("Database Configuration")
        config_win.geometry("300x200")
        config_win.configure(bg='#1a365d')
        config_win.transient(error_window)
        config_win.grab_set()

        self.center_window(config_win, 300, 200)

        frame = tk.Frame(config_win, bg='#1a365d')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(frame, text="Select Database Configuration:", fg="white", bg='#1a365d', font=("Arial", 10, "bold")).pack(pady=(0, 15))

        selected_config = tk.StringVar(value=self.db_config)

        btn_frame = tk.Frame(frame, bg='#1a365d')
        btn_frame.pack(pady=(15, 0))

        apply_btn = tk.Button(btn_frame, text="Apply & Retry", bg="#4a90e2", fg="white", font=("Arial", 9, "bold"),
                             relief="flat", padx=15, pady=5, command=lambda: self.apply_config_and_retry(selected_config.get(), config_win, error_window))
        apply_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(btn_frame, text="Cancel", bg="#7f8c8d", fg="white", font=("Arial", 9, "bold"),
                              relief="flat", padx=15, pady=5, command=config_win.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def apply_config_and_retry(self, new_config, config_window, error_window):
        self.db_config = new_config
        config_window.destroy()
        self.retry_connection(error_window)

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def center_splash_window(self):
        self.splash.update_idletasks()
        width, height = 450, 300
        screen_w = self.splash.winfo_screenwidth()
        screen_h = self.splash.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.splash.geometry(f"{width}x{height}+{x}+{y}")

    def setup_splash_logo(self, parent_frame, bg="#1a365d"):
        try:
            if self.file_path and Path(self.file_path).exists():
                original_image = Image.open(self.file_path)
                resized_image = original_image.resize((70, 70), Image.Resampling.LANCZOS)
                self.splash_logo_image = ImageTk.PhotoImage(resized_image)

                logo_label = tk.Label(
                    parent_frame,
                    image=self.splash_logo_image,
                    bg=bg,
                    borderwidth=0,
                    highlightthickness=0
                )
                logo_label.pack(pady=(5, 10))
            else:
                raise FileNotFoundError("Logo not found")
        except Exception:
            placeholder_label = tk.Label(parent_frame, text="🔬", fg="white", bg=bg, font=("Arial", 28))
            placeholder_label.pack(pady=(10, 10))

    def setup_splash_progress(self, parent_frame):
        self.splash_progress_bar = ttk.Progressbar(
            parent_frame, 
            length=250, 
            mode='determinate',
            style='Custom.Horizontal.TProgressbar'
        )
        self.splash_progress_bar.pack(pady=(5, 5))

    def update_splash_progress(self, progress, status_text):
        if hasattr(self, 'splash') and self.splash and self.splash.winfo_exists():
            try:
                self.splash_progress_bar['value'] = progress
                self.splash_status_label.config(text=status_text)
                self.splash.update()
            except tk.TclError:
                pass

    def close_splash_and_show_main(self):
        if hasattr(self, 'splash') and self.splash and self.splash.winfo_exists():
            try:
                self.splash.grab_release()
                self.splash.destroy()
            except tk.TclError:
                pass

        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', False)
        self.root.focus_force()

    def add_custom_styles(self):
        base_blue = "#1a365d"
        dark_blue = "#2d4a66"

        self.style.configure('Custom.Horizontal.TProgressbar',
                           troughcolor=dark_blue,
                           background="#4a90e2",
                           thickness=12,
                           bordercolor=base_blue)