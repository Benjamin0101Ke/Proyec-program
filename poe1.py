import tkinter as tk
from tkinter import ttk, messagebox,filedialog
from tkcalendar import Calendar
import sqlite3
import os
from datetime import datetime


def seleccionar_ubicacion():
    global db_path, conn, cursor
    db_directory = filedialog.askdirectory(title="Selecciona la ubicación para guardar la base de datos")
    if not db_directory:
        messagebox.showwarning("Advertencia", "No se seleccionó ninguna ubicación. Se usará la carpeta actual.")
        db_directory = os.getcwd()  # Carpeta actual como predeterminada
    
    db_path = os.path.join(db_directory, "tasks.db")

    # Conectar a la base de datos y crear el archivo si no existe
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"Conexión a la base de datos SQLite establecida con éxito en {db_path}.")
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")

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

# Llamar a la función para seleccionar la ubicación al inicio del programa
seleccionar_ubicacion()
def agregar_tarea():
    title = title_entry.get()
    description = desc_entry.get("1.0", tk.END)
    due_date = cal.get_date()
    due_time = time_entry.get()  # Obtener la hora de vencimiento
    category = category_var.get()
    priority = priority_var.get()

    if title == "" or due_time == "":  # Validación de que no estén vacíos
        messagebox.showwarning("Advertencia", "El título y la hora no pueden estar vacíos.")
        return

    # Validar formato de hora
    try:
        datetime.strptime(due_time, "%H:%M")  # Verificar que la hora esté en el formato correcto
    except ValueError:
        messagebox.showwarning("Advertencia", "El formato de la hora debe ser HH:MM.")
        return

    # Combinar fecha y hora
    due_datetime = f"{due_date} {due_time}:00"  # Agregar los segundos por defecto

    # Insertar tarea en la base de datos
    cursor.execute("INSERT INTO tasks (title, description, due_date, category, priority) VALUES (?, ?, ?, ?, ?) ",
                   (title, description.strip(), due_datetime, category, priority))
    conn.commit()

    Recargar_tareas()

    # Limpiar campos de entrada
    title_entry.delete(0, tk.END)
    desc_entry.delete("1.0", tk.END)
    time_entry.delete(0, tk.END)  # Limpiar el campo de hora

    # Última tarea agregada
    ultima_tarea = task_tree.get_children()[-1]
    task_tree.selection_set(ultima_tarea)
 
def calculo_de_fechas(due_datetime_str):
    try:
        # Intentamos convertir la fecha y hora proporcionada al formato correcto
        due_datetime = datetime.strptime(due_datetime_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return "Fecha o hora no válida"
    
    # Obtener la fecha y hora actuales
    current_datetime = datetime.now()

    # Calcular el tiempo restante entre la fecha de vencimiento y la actual
    remaining_time = due_datetime - current_datetime

    # Si el tiempo restante es negativo, significa que ya está vencido
    if remaining_time.total_seconds() < 0:
        return "Vencido"
    else:
        # De lo contrario, mostramos el tiempo restante
        days = remaining_time.days
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        # Devolver el tiempo restante en un formato legible
        return f"{days} días, {hours} horas, {minutes} minutos"


# Función para cargar tareas desde la base de datos
def Recargar_tareas(search_query=""):
    # Limpiar cualquier tarea previa en la vista
    for row in task_tree.get_children():
        task_tree.delete(row)
    
    # Consultar tareas con el filtro de búsqueda
    query = "SELECT * FROM tasks WHERE title LIKE ?"
    cursor.execute(query, ('%' + search_query + '%',))

    tasks = cursor.fetchall()

    if tasks: 
        for task in tasks:
            remaining_time = calculo_de_fechas(task[3])
            task_id, title, description, due_date, category, priority = task
            tags = []  # Establecer etiquetas para cambiar el color si es necesario
            if remaining_time == "Vencido":
                tags.append("vencido")  # Etiqueta de tarea vencida
            task_tree.insert("", tk.END, values=(task_id, title, description, due_date, category, priority, remaining_time), tags=tags)
            
    else:
        pass

    root.after(60000, Recargar_tareas)  # Actualizar la vista cada minuto

    
    for row in task_tree.get_children():
        task_tree.delete(row)
    
    
    query = "SELECT * FROM tasks WHERE title LIKE ?"
    cursor.execute(query, ('%' + search_query + '%',))

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

    root.after(60000, Recargar_tareas)  
    
    

    for row in task_tree.get_children():
        task_tree.delete(row)  # Eliminar todas las filas existentes en el árbol

    query = "SELECT * FROM tasks WHERE title LIKE ?"
    cursor.execute(query, ('%' + search_query + '%',))

    tasks = cursor.fetchall()  


    
    print("Tareas cargadas:")
    for task in tasks:
        print(task)  

    for task in tasks:
        remaining_time = calculo_de_fechas(task[3])
        task_id, title, description, due_date, category, priority = task
        tags = [] 
        if remaining_time == "Vencido":
            tags.append("vencido") 
        task_tree.insert("", tk.END, values=(task_id, title, description, due_date, category, priority, remaining_time), tags=tags)

    for row in task_tree.get_children():
        task_tree.delete(row)  

    query = "SELECT * FROM tasks WHERE title LIKE ?"
    cursor.execute(query, ('%' + search_query + '%',))

    for task in cursor.fetchall():
        remaining_time = calculo_de_fechas(task[3])
        task_id, title, description, due_date, category, priority = task
        tags = []  
        if remaining_time == "Vencido":
            tags.append("vencido")  
        task_tree.insert("", tk.END, values=(task_id, title, description, due_date, category, priority, remaining_time), tags=tags)

    for row in task_tree.get_children():
        task_tree.delete(row)
    query = "SELECT * FROM tasks WHERE title LIKE ?"
    cursor.execute(query, ('%' + search_query + '%',))
    for task in cursor.fetchall():
        remaining_time = calculo_de_fechas(task[3])
        task_id, title, description, due_date, category, priority = task
        tags = [] 
        if remaining_time == "Vencido":
            tags.append("vencido")  
        task_tree.insert("", tk.END, values=(task_id, title, description, due_date, category, priority, remaining_time), tags=tags)
    root.after(60000, Recargar_tareas)  

# Función para eliminar una tarea y reiniciar el ID
    selected_item = task_tree.selection()
    if not selected_item:
        return

    task_id = task_tree.item(selected_item, "values")[0]


    confirm = messagebox.askyesno("Confirmación", "¿Estás seguro de que quieres eliminar esta tarea?")
    if confirm:
        
        cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()  

        Recargar_tareas()

def eliminar_tarea():
    selected_item = task_tree.selection()  
    if selected_item:  
        task_id = task_tree.item(selected_item, "values")[0]


        confirm = messagebox.askyesno("Confirmación", "¿Estás seguro de que quieres eliminar esta tarea?")
        if confirm:

            cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            conn.commit()

            Recargar_tareas()
def editar_tarea():
    selected_item = task_tree.selection()
    if not selected_item:
        return

    # Obtener los valores de la tarea seleccionada
    task_id, title, description, due_date, category, priority, _ = task_tree.item(selected_item, "values")

    # Crear cuadro de diálogo para editar la tarea
    edit_window = tk.Toplevel(root)
    edit_window.title("Editar Tarea")
    edit_window.geometry("400x450")

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

    # Fecha de vencimiento
    tk.Label(edit_window, text="Fecha de vencimiento:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
    cal_edit = Calendar(edit_window, selectmode="day", date_pattern="yyyy-mm-dd")
    cal_edit.grid(row=2, column=1, padx=10, pady=10)

    # Hora de vencimiento
    tk.Label(edit_window, text="Hora de vencimiento:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
    hour_var = tk.StringVar(edit_window)
    hour_var.set("12:00")  # Valor por defecto

    hour_menu = ttk.Combobox(edit_window, textvariable=hour_var, values=["{:02d}:00".format(i) for i in range(24)], state="readonly")
    hour_menu.grid(row=3, column=1, padx=10, pady=10)

    # Si la tarea ya tiene una fecha y hora, establecerlos en el calendario y selector de hora
    if due_date:
        try:
            due_datetime = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
            cal_edit.selection_set(due_datetime.date())  # Establecer solo la fecha
            hour_var.set(due_datetime.strftime("%H:%M"))  # Establecer la hora
        except ValueError:
            pass

    # Categoría
    tk.Label(edit_window, text="Categoría:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
    category_var_edit = tk.StringVar()
    category_menu_edit = ttk.Combobox(edit_window, textvariable=category_var_edit, values=["Ejercicio", "Comida", "Actividad"], state="readonly")
    category_menu_edit.grid(row=4, column=1, padx=10, pady=10)
    category_var_edit.set(category)

    # Prioridad
    tk.Label(edit_window, text="Prioridad:").grid(row=5, column=0, padx=10, pady=10, sticky="w")
    priority_var_edit = tk.StringVar()
    priority_menu_edit = ttk.Combobox(edit_window, textvariable=priority_var_edit, values=["Alta", "Media", "Baja"], state="readonly")
    priority_menu_edit.grid(row=5, column=1, padx=10, pady=10)

    # Función para guardar los cambios
    def guardar_datos():
        new_title = title_entry_edit.get()
        new_description = desc_entry_edit.get("1.0", tk.END).strip()
        new_due_date = cal_edit.get_date()  # Fecha seleccionada
        new_due_time = hour_var.get()  # Hora seleccionada
        new_category = category_var_edit.get()
        new_priority = priority_var_edit.get()

        # Combinar la fecha y la hora
        new_due_datetime_str = f"{new_due_date} {new_due_time}:00"
        try:
            new_due_datetime = datetime.strptime(new_due_datetime_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showwarning("Advertencia", "La fecha o la hora no son válidas.")
            return

        # Validación de que el título no esté vacío
        if new_title == "":
            messagebox.showwarning("Advertencia", "El título no puede estar vacío.")
            return

        # Actualización de la tarea en la base de datos
        cursor.execute("UPDATE tasks SET title=?, description=?, due_date=?, category=?, priority=? WHERE id=?",
                       (new_title, new_description, new_due_datetime, new_category, new_priority, task_id))
        conn.commit()  # Guardar cambios en la base de datos

        Recargar_tareas()  # Recargar la lista de tareas para reflejar los cambios
        edit_window.destroy()  # Cerrar la ventana de edición

    # Crear el botón de guardar cambios
    save_button = tk.Button(edit_window, text="Guardar cambios", command=guardar_datos)
    save_button.grid(row=6, column=0, columnspan=2, pady=10)  # Usar grid en lugar de pack para asegurar posición

    edit_window.mainloop()
    # Crear el botón de guardar cambios
    save_button = tk.Button(edit_window, text="Guardar cambios", command=guardar_datos)
    save_button.grid(row=6, column=0, columnspan=2, pady=10)  # Usar grid en lugar de pack para asegurar posición

    edit_window.mainloop()

    # Crear el botón de guardar cambios
    save_button = tk.Button(edit_window, text="Guardar cambios", command=guardar_datos)
    save_button.grid(row=5, column=0, columnspan=2, pady=10)  # Usar grid en lugar de pack para asegurar posición

    edit_window.mainloop()


    # Crear el botón de guardar cambios
    save_button = tk.Button(edit_window, text="Guardar cambios", command=guardar_datos)
    save_button.grid(row=5, column=0, columnspan=2, pady=10)  # Usar grid en lugar de pack para asegurar posición

    edit_window.mainloop()


# Función para buscar tareas
def search_tasks():
    search_query = search_entry.get()
    Recargar_tareas(search_query)

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
main_frame = tk.Frame(root, bg="#EAEDED", bd=2, relief="solid")
main_frame.pack(pady=20, fill="both", expand=True)

# Configuración del frame para entradas (lado izquierdo)
entry_frame = tk.Frame(main_frame, bg="#EAEDED", bd=2, relief="solid")
entry_frame.pack(side="left", padx=20, pady=20, fill="y", expand=True)

# Configuración de las entradas
tk.Label(entry_frame, text="Título de la tarea:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
title_entry = tk.Entry(entry_frame, width=30)
title_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")  # Expande horizontalmente

tk.Label(entry_frame, text="Descripción:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
desc_entry = tk.Text(entry_frame, width=30, height=5)
desc_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")  # Expande horizontalmente

tk.Label(entry_frame, text="Fecha de vencimiento:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
cal = Calendar(entry_frame, selectmode="day", date_pattern="yyyy-mm-dd")
cal.grid(row=2, column=1, padx=10, pady=10, sticky="ew")  # Expande horizontalmente

tk.Label(entry_frame, text="Categoría:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
category_var = tk.StringVar()
category_menu = ttk.Combobox(entry_frame, textvariable=category_var, values=["Ejercicio", "Comida", "Actividad"], state="readonly")
category_menu.grid(row=3, column=1, padx=10, pady=10, sticky="ew")  # Expande horizontalmente

tk.Label(entry_frame, text="Prioridad:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
priority_var = tk.StringVar()
priority_menu = ttk.Combobox(entry_frame, textvariable=priority_var, values=["Alta", "Media", "Baja"], state="readonly")
priority_menu.grid(row=4, column=1, padx=10, pady=10, sticky="ew")  # Expande horizontalmente

# En la sección de entradas, donde se selecciona la fecha de vencimiento, agrega un campo para la hora
tk.Label(entry_frame, text="Hora de vencimiento:").grid(row=2, column=2, padx=10, pady=10, sticky="w")
time_entry = tk.Entry(entry_frame, width=15)  # Campo para hora en formato HH:MM
time_entry.grid(row=2, column=3, padx=10, pady=10, sticky="ew")


# Configuración del frame de botones
button_frame = tk.Frame(entry_frame, bg="#EAEDED")
button_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")  
add_button = tk.Button(button_frame, text="Añadir tarea", command=agregar_tarea)
add_button.pack(side="left", padx=5, fill="x", expand=True)

edit_button = tk.Button(button_frame, text="Editar tarea", command=editar_tarea)
edit_button.pack(side="left", padx=5, fill="x", expand=True)

delete_button = tk.Button(button_frame, text="Eliminar tarea", command=eliminar_tarea)
delete_button.pack(side="left", padx=5, fill="x", expand=True)

# Configuración del frame de tareas (lado derecho)
task_frame = tk.Frame(main_frame, bg="#EAEDED", bd=2, relief="solid")
task_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

# Configuración de la búsqueda
tk.Label(task_frame, text="Buscar tareas:").pack(padx=10, pady=10)
search_entry = tk.Entry(task_frame, width=50)
search_entry.pack(padx=10, pady=10, fill="x")  # Ajusta el campo de búsqueda al ancho

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

# Al mostrar las tareas


# Configuración para que el árbol se ajuste al tamaño
task_tree.pack(fill="both", expand=True)

task_tree.tag_configure("vencido", background="red", foreground="white")

Recargar_tareas()

root.mainloop()

conn.close()
