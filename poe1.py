import tkinter as tk # sirve para crear la ventana
from tkinter import ttk, messagebox,filedialog # sirve para crear la ventana y los botones
from tkcalendar import Calendar # sirve para crear el calendario
import sqlite3 #sirve para crear la base de datos
import os
from datetime import datetime # sirve para el tiempo


db_path = ""  # sirve para guardar la ubicación de la base de datos


def seleccionar_ubicacion(): #
    """
    Permite al usuario seleccionar una ubicación para guardar la base de datos.
    """
    global db_path, conn, cursor
    db_directory = filedialog.askdirectory(title="Selecciona la ubicación para guardar la base de datos")
    if not db_directory:  
        messagebox.showwarning("Advertencia!!", "no se seleccionó ninguna ubicación. Se usará la carpeta actual.")
        db_directory = os.getcwd()  

    db_path = os.path.join(db_directory, "tasks.db")
    conectar_db()  # Conectar o crear la base de datos


def conectar_db():

    global conn, cursor
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"Conexión a la base de datos SQLite establecida con éxito en {db_path}.")
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return

    # Crear tabla de tareas si no existe
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT NOT NULL,
        category TEXT,
        priority TEXT
    )
    """)
    conn.commit()



default_directory = os.getcwd()  
db_path = os.path.join(default_directory, "tasks.db")

if os.path.exists(db_path):
    print(f"Base de datos encontrada en {db_path}. Conectando...")
    conectar_db()  
else:
    print("No se encontró una base de datos existente. Solicita al usuario seleccionar una ubicación.")
    seleccionar_ubicacion()
    # Asegurarse de que la fecha esté en el formato correcto


def calculo_de_fechas(due_date):
    """
    Calcula el tiempo restante hasta una fecha de vencimiento.
    """
    try:
        # Intentar convertir la fecha de vencimiento al formato correcto
        due_datetime = datetime.strptime(due_date, "%Y-%m-%d %H:%M")
    except ValueError:
        # Si hay un error en el formato, devolver "Formato inválido"
        return "Formato inválido"
    
    actualidad = datetime.now()
    remaining_time = due_datetime - actualidad

    if remaining_time.total_seconds() < 0:
        return "Vencido"
    else:
        dias = remaining_time.days
        horas, remainder = divmod(remaining_time.seconds, 3600)
        minutos, _ = divmod(remainder, 60)
        return f"{dias} días, {horas} horas, {minutos} minutos"



def agregar_tarea():

    hora = hour_var.get()
    minuto = minute_var.get()
    fecha_de_calendario = cal.get_date()  

    title = title_entry.get()
    description = desc_entry.get("1.0", tk.END)
    due_date = f"{fecha_de_calendario} {hora.zfill(2)}:{minuto.zfill(2)}"
    category = category_var.get()
    priority = priority_var.get()

    if title == "" or due_date == "":  # Validación de que no estén vacíos
        messagebox.showwarning("Advertencia", "El título y la hora no pueden estar vacíos.")
        return

    # Insertar tarea en la base de datos
    cursor.execute("INSERT INTO tasks (title, description, due_date, category, priority) VALUES (?, ?, ?, ?, ?) ",
                   (title, description.strip(), due_date, category, priority))
    conn.commit()

    Recargar_tareas()

    # Limpiar campos de entrada
    title_entry.delete(0, tk.END)
    desc_entry.delete("1.0", tk.END) 
   


    # Última tarea agregada
    ultima_tarea = task_tree.get_children()[-1]
    task_tree.selection_set(ultima_tarea)
 
 

# Función para cargar tareas desde la base de datos con búsqueda por título y prioridad
def Recargar_tareas(search_query="", priority_filter=""):
    # Limpiar cualquier tarea previa en la vista
    for row in task_tree.get_children():
        task_tree.delete(row)
    
    # Consultar tareas con el filtro de búsqueda
    query = "SELECT * FROM tasks WHERE title LIKE ?"
    params = ('%' + search_query + '%',)

    # Si se seleccionó una prioridad, agregar al filtro
    if priority_filter:
        query += " AND priority = ?"
        params += (priority_filter,)

    cursor.execute(query, params)
    tasks = cursor.fetchall()

    if tasks:  
        for task in tasks:
            remaining_time = calculo_de_fechas(task[3])
            task_id, title, description, due_date, category, priority = task
            tags = []  
            if remaining_time == "Vencido":
                tags.append("vencido") 
            task_tree.insert("", tk.END, values=(task_id, title, description, due_date, category, priority, remaining_time), tags=tags)
    else:
        pass

    root.after(60000, Recargar_tareas)  # Actualizar la vista cada minuto


def eliminar_tarea():
    selected_item = task_tree.selection()  
    if selected_item:  
        task_id = task_tree.item(selected_item, "values")[0]


        confirm = messagebox.askyesno("Confirmación", "¿Estás seguro de que quieres eliminar esta tarea?")
        if confirm:

            cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            conn.commit()

            Recargar_tareas()

# Función para editar una tarea
def editar_tarea():
    selected_item = task_tree.selection()
    if not selected_item:
        messagebox.showwarning("Advertencia", "Por favor, selecciona una tarea para editar.")
        return

    # Obtener los valores de la tarea seleccionada
    task_values = task_tree.item(selected_item, "values")
    task_id, title, description, due_date, category, priority, _ = task_values

    # Crear la ventana de edición
    edit_window = tk.Toplevel(root)
    edit_window.title("Editar Tarea")
    edit_window.geometry("400x500")

    # Título de la tarea
    tk.Label(edit_window, text="Título:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    title_entry_edit = tk.Entry(edit_window, width=30)
    title_entry_edit.grid(row=0, column=1, padx=10, pady=10)
    title_entry_edit.insert(0, title)

    # Descripción de la tarea
    tk.Label(edit_window, text="Descripción:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    desc_entry_edit = tk.Text(edit_window, width=30, height=5)
    desc_entry_edit.grid(row=1, column=1, padx=10, pady=10)
    desc_entry_edit.insert("1.0", description)


    # Hora de vencimiento
    tk.Label(edit_window, text="Hora de vencimiento:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
    hour_var = tk.StringVar(value="12")
    hour_spinbox = tk.Spinbox(edit_window, from_=0, to=23, wrap=True, textvariable=hour_var, width=5, state="readonly")
    hour_spinbox.grid(row=3, column=1, padx=0, pady=10, sticky="w")

    minute_var = tk.StringVar(value="00")
    minute_spinbox = tk.Spinbox(edit_window, from_=0, to=59, wrap=True, textvariable=minute_var, width=5, state="readonly", format="%02.0f")
    minute_spinbox.grid(row=3, column=2, padx=2, pady=10, sticky="w")

    # Categoría
    tk.Label(edit_window, text="Categoría:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
    category_var = tk.StringVar(value=category)
    category_menu = ttk.Combobox(edit_window, textvariable=category_var, values=["Ejercicio", "Comida", "Actividad"], state="readonly")
    category_menu.grid(row=4, column=1)

    # Prioridad
    tk.Label(edit_window, text="Prioridad:").grid(row=5, column=0, padx=10, pady=10, sticky="w")
    priority_var = tk.StringVar(value=priority)
    priority_menu = ttk.Combobox(edit_window, textvariable=priority_var, values=["Alta", "Media", "Baja"], state="readonly")
    priority_menu.grid(row=5, column=1, padx=10, pady=10)

    # Función para guardar los datos actualizados
    def guardar_datos():
        new_title = title_entry_edit.get()
        new_description = desc_entry_edit.get("1.0", tk.END).strip()
        new_due_date = cal.get_date()
        new_hour = hour_var.get()
        new_minute = minute_var.get()
        new_category = category_var.get()
        new_priority = priority_var.get()

        # Validar formato de fecha y hora
        try:
            due_datetime = f"{new_due_date} {new_hour}:{new_minute}:00"
            datetime.strptime(due_datetime, "%Y-%m-%d %H:%M:%S")  # Verifica el formato
        except ValueError:
            messagebox.showerror("Error", "La fecha y hora ingresadas no son válidas.")
            return

        # Actualizar los datos en la tabla
        task_tree.item(selected_item, values=(task_id, new_title, new_description, new_due_date, new_category, new_priority, due_datetime))
        messagebox.showinfo("Éxito", "Tarea actualizada correctamente.")
        edit_window.destroy()

    # Botón para guardar cambios
    save_button = tk.Button(edit_window, text="Guardar cambios", command=guardar_datos)
    save_button.grid(row=6, column=0, columnspan=2, pady=0)

    edit_window.mainloop()
    
def search_tasks():
    search_query = search_entry.get()
    priority_filter = priority_combobox.get()  # Obtener la prioridad seleccionada
    Recargar_tareas(search_query, priority_filter)


    task_tree.delete(*task_tree.get_children())  # Eliminar todas las filas del árbol

    # Consulta SQL para buscar tareas
    if search_query and priority_filter:
        cursor.execute("SELECT id, title, description, due_date, category, priority FROM tasks WHERE title LIKE ? AND priority = ?", (f"%{search_query}%", priority_filter))
    elif search_query:
        cursor.execute("SELECT id, title, description, due_date, category, priority FROM tasks WHERE title LIKE ?", (f"%{search_query}%",))
    elif priority_filter:
        cursor.execute("SELECT id, title, description, due_date, category, priority FROM tasks WHERE priority = ?", (priority_filter,))
    else:
        cursor.execute("SELECT id, title, description, due_date, category, priority FROM tasks")

    tasks = cursor.fetchall()

    for task in tasks:
        task_id, title, description, due_date, category, priority = task
        remaining_time = calculo_de_fechas(due_date)
        task_tree.insert("", "end", values=(task_id, title, description, due_date, category, priority, remaining_time))
# Cerrar la conexión al cerrar la ventana
def on_close():
    conn.close()
    root.quit()

# Configuración de la ventana principal
root = tk.Tk()
root.title("Gestor de Tareas")
root.geometry("1200x700")
root.iconbitmap("gatito.ico")
root.configure(bg="#EAEDED")


# Cambiar la fuente por defecto
root.option_add("*Font", "Arial 10")

# Asociar el evento de cierre de ventana con la función on_close
root.protocol("WM_DELETE_WINDOW", on_close)

# Crear el menú
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Menú principal
main_menu = tk.Menu(menu_bar, tearoff=0, bg="#007acc", fg="white")
menu_bar.add_cascade(label="Opciones", menu=main_menu)
main_menu.add_command(label="Añadir tarea", command=agregar_tarea)
main_menu.add_command(label="Eliminar tarea", command=eliminar_tarea)
main_menu.add_command(label="Editar tarea", command=editar_tarea)
main_menu.add_separator()
main_menu.add_command(label="Salir", command=root.quit)

# Frame principal
# Configuración del marco principal
main_frame = tk.Frame(root, bg="#835581", bd=2, relief="solid")
main_frame.pack(pady=20, fill="both", expand=True)

# Configuración del frame para entradas (lado izquierdo)
entry_frame = tk.Frame(main_frame, bg="#8E6189", bd=2, relief="solid")
entry_frame.pack(side="left", padx=20, pady=20, fill="y", expand=True)

# Configuración de las entradas
tk.Label(entry_frame, text="Título de la tarea:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
title_entry = tk.Entry(entry_frame, width=30)
title_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")  # Expande horizontalmente

tk.Label(entry_frame, text="Descripción:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
desc_entry = tk.Text(entry_frame, width=30, height=5)
desc_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")  # Expande horizontalmente

# Spinbox para las horas (1-12)
hour_var = tk.StringVar(value="12")
hour_spinbox = tk.Spinbox(entry_frame, from_=1, to=24, wrap=True, textvariable=hour_var, width=5, state="readonly")
hour_spinbox.grid(row=2, column=2, padx=10, pady=10, sticky="w")
# Spinbox para los minutos (00-59)
minute_var = tk.StringVar(value="00")
minute_spinbox = tk.Spinbox(entry_frame, from_=0, to=59, wrap=True, textvariable=minute_var, width=5, state="readonly", format="%02.0f")
minute_spinbox.grid(row=2, column=3, pady=12, padx=12, sticky="w")


tk.Label(entry_frame, text="Categoría:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
category_var = tk.StringVar()
category_menu = ttk.Combobox(entry_frame, textvariable=category_var, values=["Ejercicio", "Comida", "Actividad"], state="readonly")
category_menu.grid(row=3, column=1, padx=10, pady=10, sticky="ew")  # Expande horizontalmente

tk.Label(entry_frame, text="Prioridad:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
priority_var = tk.StringVar()
priority_menu = ttk.Combobox(entry_frame, textvariable=priority_var, values=["Alta", "Media", "Baja"], state="readonly")
priority_menu.grid(row=4, column=1, padx=10, pady=10, sticky="ew")  # Expande horizontalmente

# En la sección de entradas, donde se selecciona la fecha de vencimiento, agrega un campo para la hora
tk.Label(entry_frame, text="Hora de vencimiento:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
cal = Calendar(entry_frame, selectmode="day", date_pattern="y-mm-dd")
cal.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

# Configuración del frame de botones
button_frame = tk.Frame(entry_frame, bg="#FAEBD7")
button_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")  
add_button = tk.Button(button_frame, text="Añadir tarea", command=agregar_tarea)
add_button.pack(side="left", padx=5, fill="x", expand=True)

edit_button = tk.Button(button_frame, text="Editar tarea", command=editar_tarea)
edit_button.pack(side="left", padx=5, fill="x", expand=True)

delete_button = tk.Button(button_frame, text="Eliminar tarea", command=eliminar_tarea)
delete_button.pack(side="left", padx=5, fill="x", expand=True)

# Configuración del frame de tareas (lado derecho)
task_frame = tk.Frame(main_frame, bg="#EBE1D9", bd=2, relief="flat")
task_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

# Configuración de la búsqueda
tk.Label(task_frame, text="Buscar tareas:").pack(padx=10, pady=10)
search_entry = tk.Entry(task_frame, width=50)
search_entry.pack(padx=10, pady=10, fill="x")  # Ajusta el campo de búsqueda al ancho
# Añadir el Combobox para seleccionar la prioridad en el área de búsqueda
tk.Label(task_frame, text="Buscar por prioridad:").pack(padx=10, pady=10)
priority_combobox = ttk.Combobox(task_frame, values=["", "Alta", "Media", "Baja"], state="readonly")
priority_combobox.pack(padx=10, pady=10, fill="x")  # Ajusta el Combobox al ancho

search_button = tk.Button(task_frame, text="Buscar", command=search_tasks)
search_button.pack(padx=10, pady=10)

# Árbol para mostrar tareas
task_tree = ttk.Treeview(task_frame, columns=("ID", "Título", "Descripción", "Fecha de vencimiento", "Categoría", "Prioridad", "Tiempo restante"), show="headings")
task_tree.heading("ID", text="ID")
task_tree.heading("Título", text="Título")
task_tree.heading("Descripción", text="Descripción")
task_tree.heading("Fecha de vencimiento", text="Fecha de vencimiento")
task_tree.heading("Categoría", text="Categoría")
task_tree.heading("Prioridad", text="Prioridad")
task_tree.heading("Tiempo restante", text="Tiempo restante")
task_tree.heading("Fecha de vencimiento", text="Fecha y hora de vencimiento")

# Configuración para que el árbol se ajuste al tamaño
task_tree.pack(fill="both", expand=True)

task_tree.tag_configure("vencido", background="red", foreground="white")

Recargar_tareas()

root.mainloop()

conn.close()
