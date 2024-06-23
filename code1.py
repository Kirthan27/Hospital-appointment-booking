import sqlite3
import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image

# Database Connection
conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()

# Create tables if not exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        doctor_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        specialization TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id INTEGER PRIMARY KEY,
        doctor_id INTEGER,
        patient_id INTEGER,
        appointment_date TEXT,
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    )
''')

# Function to insert default doctors
def insert_default_doctors():
    doctors = [
        ("Dr. Vinod kumar", "Cardiology"),
        ("Dr. Shaibi Mukerjee", "Pediatrics"),
        ("Dr. David Pandey", "Orthopedics"),
        ("Dr. Praveen Brown", "Dermatology"),
        ("Dr. Michael Pawar", "Ophthalmology")
    ]

    cursor.executemany("INSERT INTO doctors (name, specialization) VALUES (?, ?)", doctors)
    conn.commit()

# Check if doctors table is empty, then insert default doctors
cursor.execute("SELECT COUNT(*) FROM doctors")
count = cursor.fetchone()[0]
if count == 0:
    insert_default_doctors()

# Tkinter App
root = tk.Tk()
root.title("Hospital Appointment Booking System")

# Load and display background image
bg_image = Image.open("hospital_background.jpg")
bg_image = bg_image.resize((800, 600), Image.ANTIALIAS)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Define center coordinates
center_x = root.winfo_screenwidth() // 2
center_y = root.winfo_screenheight() // 2

# Functions
def view_available_doctors():
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()
    if doctors:
        messagebox.showinfo("Available Doctors", "\n".join(f"{doctor[0]}: {doctor[1]} ({doctor[2]})" for doctor in doctors))
    else:
        messagebox.showinfo("Available Doctors", "No doctors available.")

def schedule_appointment():
    patient_name = entry_patient_name.get().strip()
    doctor_id = entry_doctor_id.get().strip()
    
    if not (patient_name and doctor_id):
        messagebox.showwarning("Warning", "Please enter patient name and doctor ID.")
        return
    
    try:
        doctor_id = int(doctor_id)
    except ValueError:
        messagebox.showwarning("Warning", "Doctor ID must be a valid number.")
        return
    
    # Check if the provided doctor ID exists
    cursor.execute("SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,))
    doctor = cursor.fetchone()
    
    if not doctor:
        messagebox.showwarning("Warning", f"Doctor with ID {doctor_id} not found.")
        return
    
    cursor.execute("INSERT INTO patients (name) VALUES (?)", (patient_name,))
    patient_id = cursor.lastrowid
    
    cursor.execute("INSERT INTO appointments (doctor_id, patient_id, appointment_date) VALUES (?, ?, date('now'))", (doctor_id, patient_id))
    conn.commit()
    messagebox.showinfo("Success", "Appointment scheduled successfully.")

def view_scheduled_appointments():
    cursor.execute('''
        SELECT appointments.appointment_id, doctors.name, doctors.specialization, patients.name, appointments.appointment_date
        FROM appointments
        JOIN doctors ON appointments.doctor_id = doctors.doctor_id
        JOIN patients ON appointments.patient_id = patients.patient_id
    ''')
    appointments = cursor.fetchall()
    if appointments:
        appointment_info = "\n".join(f"Appointment ID: {appointment[0]}\nDoctor: {appointment[1]} ({appointment[2]})\nPatient: {appointment[3]}\nDate: {appointment[4]}\n" for appointment in appointments)
        messagebox.showinfo("Scheduled Appointments", appointment_info)
    else:
        messagebox.showinfo("Scheduled Appointments", "No appointments scheduled.")

# GUI Components
label_patient_name = tk.Label(root, text="Patient Name:", bg='white')
label_patient_name.place(x=center_x - 200, y=center_y - 50, anchor='center')

entry_patient_name = tk.Entry(root)
entry_patient_name.place(x=center_x - 50, y=center_y - 50, anchor='center')

label_doctor_id = tk.Label(root, text="Doctor ID:", bg='white')
label_doctor_id.place(x=center_x - 200, y=center_y, anchor='center')

entry_doctor_id = tk.Entry(root)
entry_doctor_id.place(x=center_x - 50, y=center_y, anchor='center')

button_view_doctors = tk.Button(root, text="View Available Doctors", command=view_available_doctors)
button_view_doctors.place(x=center_x - 150, y=center_y + 50, anchor='center')

button_schedule_appointment = tk.Button(root, text="Schedule Appointment", command=schedule_appointment)
button_schedule_appointment.place(x=center_x + 50, y=center_y + 50, anchor='center')

button_view_appointments = tk.Button(root, text="View Scheduled Appointments", command=view_scheduled_appointments)
button_view_appointments.place(x=center_x, y=center_y + 100, anchor='center')

# Main loop
root.mainloop()

# Close connection
conn.close()

