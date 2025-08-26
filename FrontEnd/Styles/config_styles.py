def configure_styles(style):
        """Configure modern styling for the application"""
        style.theme_use('clam')
        
        
        # Modern professional color palette
        primary_color = '#1a365d'       # Deep navy blue
        secondary_color = '#2d3748'     # Charcoal gray
        accent_color = '#3182ce'        # Professional blue
        dark_color = '#1a202c'          # Almost black
        light_color = '#f7fafc'         # Off white
        text_color = '#2d3748'          # Dark gray
        success_color = '#38a169'       # Forest green
        warning_color = '#d69e2e'       # Amber
        danger_color = '#e53e3e'         # Danger red
                
        # Custom style configurations
        style.configure('.', 
                           background=light_color, 
                           foreground=text_color,
                           font=('Century Gothic', 10))
        
        # Main frame with subtle gradient effect
        style.configure('Main.TFrame', background='#f5f7fa')
        
        # Header style
        style.configure('Header.TFrame', background=dark_color)
        style.configure('Header.TLabel', 
                           font=('Century Gothic', 18, 'bold'), 
                           foreground='white',
                           background=dark_color)
        
        # Notebook styling
        style.configure('Custom.TNotebook', background=light_color)
        style.configure('Custom.TNotebook.Tab', 
                           font=('Century Gothic', 10, 'bold'),
                           padding=[15, 5],
                           background='#dfe6e9',
                           foreground=dark_color)
        style.map('Custom.TNotebook.Tab',
                      background=[('selected', 'white')],
                      foreground=[('selected', primary_color)])
        
        # LabelFrame styling
        style.configure('TLabelframe', 
                           font=('Century Gothic', 10, 'bold'),
                           foreground=dark_color)
        style.configure('TLabelframe.Label', 
                           font=('Century Gothic', 10, 'bold'),
                           foreground=primary_color)
        
        # Button styles
        style.configure('Primary.TButton', 
                           background=primary_color,
                           foreground='white',
                           font=('Century Gothic', 10, 'bold'),
                           borderwidth=1,
                           padding=6)
        style.map('Primary.TButton',
                      background=[('active', '#2980b9'), ('disabled', '#bdc3c7')])
        
        style.configure('Success.TButton', 
                           background=success_color,
                           foreground='white',
                           font=('Century Gothic', 10, 'bold'),
                           borderwidth=1,
                           padding=6)
        style.map('Success.TButton',
                      background=[('active', '#219653'), ('disabled', '#bdc3c7')])
        
        style.configure('Danger.TButton', 
                           background=danger_color,
                           foreground='white',
                           font=('Century Gothic', 10, 'bold'),
                           borderwidth=1,
                           padding=6)
        style.map('Danger.TButton',
                      background=[('active', '#c0392b'), ('disabled', '#bdc3c7')])
        
        # Entry styling
        style.configure('TEntry', 
                           fieldbackground='white',
                           bordercolor=primary_color,
                           lightcolor=primary_color,
                           padding=5)
        
        # Treeview styling
        style.configure('Treeview',
                           font=('Century Gothic', 9),
                           rowheight=28,
                           background='white',
                           fieldbackground='white',
                           foreground=text_color)
        style.configure('Treeview.Heading',
                           font=('Century Gothic', 9, 'bold'),
                           background=dark_color,
                           foreground='white',
                           relief='flat')
        style.map('Treeview',
                      background=[('selected', primary_color)])
        
        # Scrollbar styling
        style.configure('TScrollbar', 
                           gripcount=0,
                           background='#bdc3c7',
                           troughcolor=light_color,
                           bordercolor=light_color,
                           arrowcolor=dark_color)
        style.map('TScrollbar',
                      background=[('active', '#95a5a6')])
        
        # Progressbar styling
        style.configure('TProgressbar',
                           thickness=20,
                           background=primary_color,
                           troughcolor=light_color,
                           bordercolor=light_color,
                           lightcolor=primary_color,
                           darkcolor=primary_color)
        
        # Status bar styling
        style.configure('Status.TFrame', 
                           background=dark_color)
        style.configure('Status.TLabel', 
                           font=('Century Gothic', 9),
                           background=dark_color,
                           foreground='white',
                           padding=3)
     
     
def configure_table_styles(style):
         
        style.configure("Excel.Treeview",
                             background="white",
                             foreground="black",
                             rowheight=25,
                             fieldbackground="white",
                             borderwidth=1,
                             relief="solid")
        
        style.map("Excel.Treeview",
                       background=[('selected', '#0078d4'),
                                   ('!selected', 'white')])