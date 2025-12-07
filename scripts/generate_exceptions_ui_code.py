"""
Script para agregar la sección de excepciones en el diálogo de edición de reglas
"""

# Código de la sección de excepciones a insertar
exceptions_section_code = '''
            # NUEVA SECCIÓN: Excepciones (REFramework)
            # Verificar si esta regla soporta excepciones
            supports_exceptions = rule_id in [
                'NOMENCLATURA_001',
                'NOMENCLATURA_002',
                'NOMENCLATURA_003',
                'NOMENCLATURA_004',
                'NOMENCLATURA_005'
            ]
            
            exceptions_list = []  # Lista mutable para excepciones
            
            if supports_exceptions:
                # Separador
                ttk.Separator(params_frame, orient='horizontal').pack(fill=tk.X, pady=15)
                
                # Título de la sección
                tk.Label(
                    params_frame,
                    text="Excepciones de la Regla (REFramework)",
                    font=("Arial", 11, "bold"),
                    bg="white",
                    fg=PRIMARY_COLOR
                ).pack(anchor="w", pady=(10, 5))
                
                # Descripción
                tk.Label(
                    params_frame,
                    text="Variables o argumentos que deben ignorarse durante la validación de esta regla. Útil para nombres estándar del REFramework como Config, TransactionItem, etc.",
                    font=("Arial", 9),
                    bg="white",
                    fg="gray",
                    wraplength=520,
                    justify=tk.LEFT
                ).pack(anchor="w", pady=(0, 10))
                
                # Frame para la lista de excepciones
                exceptions_frame = tk.Frame(params_frame, bg="white")
                exceptions_frame.pack(fill=tk.BOTH, expand=True, pady=10)
                
                # Listbox con scrollbar
                exceptions_list_frame = tk.Frame(exceptions_frame, bg="white")
                exceptions_list_frame.pack(fill=tk.BOTH, expand=True)
                
                exceptions_scrollbar = tk.Scrollbar(exceptions_list_frame)
                exceptions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                exceptions_listbox = tk.Listbox(
                    exceptions_list_frame,
                    font=("Arial", 10),
                    yscrollcommand=exceptions_scrollbar.set,
                    selectmode=tk.SINGLE,
                    height=8,
                    bg="#F9F9F9"
                )
                exceptions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                exceptions_scrollbar.config(command=exceptions_listbox.yview)
                
                # Cargar excepciones actuales
                current_exceptions = parameters.get('exceptions', [])
                exceptions_list = list(current_exceptions)  # Copia mutable
                
                for exc in exceptions_list:
                    exceptions_listbox.insert(tk.END, exc)
                
                # Frame para botones de gestión
                exceptions_buttons_frame = tk.Frame(params_frame, bg="white")
                exceptions_buttons_frame.pack(fill=tk.X, pady=10)
                
                # Entry para nueva excepción
                new_exception_var = tk.StringVar()
                new_exception_entry = tk.Entry(
                    exceptions_buttons_frame,
                    textvariable=new_exception_var,
                    font=("Arial", 10),
                    width=30
                )
                new_exception_entry.pack(side=tk.LEFT, padx=(0, 10))
                
                def add_exception():
                    """Agregar nueva excepción a la lista"""
                    exception_name = new_exception_var.get().strip()
                    
                    if not exception_name:
                        messagebox.showwarning(
                            "Campo Vacío",
                            "Por favor ingrese un nombre de excepción",
                            parent=dialog
                        )
                        return
                    
                    if exception_name in exceptions_list:
                        messagebox.showwarning(
                            "Duplicado",
                            f"La excepción '{exception_name}' ya existe en la lista",
                            parent=dialog
                        )
                        return
                    
                    # Agregar a lista y listbox
                    exceptions_list.append(exception_name)
                    exceptions_listbox.insert(tk.END, exception_name)
                    new_exception_var.set('')  # Limpiar campo
                
                def remove_exception():
                    """Eliminar excepción seleccionada"""
                    selection = exceptions_listbox.curselection()
                    if not selection:
                        messagebox.showwarning(
                            "Sin Selección",
                            "Por favor seleccione una excepción para eliminar",
                            parent=dialog
                        )
                        return
                    
                    index = selection[0]
                    exception_name = exceptions_listbox.get(index)
                    
                    # Confirmar eliminación
                    if messagebox.askyesno(
                        "Confirmar Eliminación",
                        f"¿Eliminar la excepción '{exception_name}'?",
                        parent=dialog
                    ):
                        exceptions_list.remove(exception_name)
                        exceptions_listbox.delete(index)
                
                # Botón Agregar
                add_exception_btn = tk.Button(
                    exceptions_buttons_frame,
                    text="➕ Agregar",
                    command=add_exception,
                    bg=PRIMARY_COLOR,
                    fg="white",
                    font=("Arial", 9, "bold"),
                    padx=15,
                    pady=5
                )
                add_exception_btn.pack(side=tk.LEFT, padx=5)
                
                # Botón Eliminar
                remove_exception_btn = tk.Button(
                    exceptions_buttons_frame,
                    text="➖ Eliminar Seleccionado",
                    command=remove_exception,
                    bg="#DC3545",
                    fg="white",
                    font=("Arial", 9, "bold"),
                    padx=15,
                    pady=5
                )
                remove_exception_btn.pack(side=tk.LEFT, padx=5)
                
                # Permitir agregar con Enter
                new_exception_entry.bind('<Return>', lambda e: add_exception())
        '''

print("Código de la sección de excepciones generado")
print(f"Líneas de código: {len(exceptions_section_code.split(chr(10)))}")
print("\nEste código debe insertarse después de la línea 712 en rules_management_screen.py")
print("(después de prefix_desc.pack y antes de # Conjuntos)")
