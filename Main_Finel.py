from tkinter import *
import pandas as pd
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import filedialog
import mysql.connector
import csv
from matplotlib.figure import Figure
from pandas import *


def perform_action():
    user_input = text_entry.get()  # Get the text entered by the user
    if user_input :
        
     # You can perform any action with the user input here, such as printing it
     # print("User Input:", user_input)
         # Execute the query and display the results in a table
     query=f"select * from school where school_Id={user_input}"
     cursor = conn.cursor()
     cursor.execute(query)
     result = cursor.fetchall()
    

     # Clear existing rows in the table
     for row in tree.get_children():
         tree.delete(row)
 
     # Insert the results into the table
     for row_data in result:
        tree.insert("", "end", values=row_data)
     analyze_data(result)
    
    
def combobox_value(name):
        # Replace 'your_column' with the name of the column you want to fetch from
    query = f"SELECT DISTINCT {name} FROM school"
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()

    # Extract unique values from the query results
    unique_values = [result[0] for result in results]
    return unique_values;
    
#DAtabase
import numpy as np
db_config = {
    "host": "localhost",     #  MySQL host
    "user": "root", #  MySQL username
    "password": "", #  MySQL password
    "database": "studentdata"  #  MySQL database
}

# Show Database Values
conn = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="studentdata"
)
    
# Create a function to establish a database connection and fetch data
def fetch_data():
    try:
        # Establish a connection to your MySQL database
        conn = mysql.connector.connect(
         host="localhost",
         user="root",
         password="",
         database="studentdata"
        )

        # Create a SQL query to fetch the data from the database
        query = "SELECT * FROM school"

        # Use pandas to execute the SQL query and fetch the data into a DataFrame
        data = pd.read_sql_query(query, conn)

        # Close the database connection
        conn.close()

        return data

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Create a function to perform analysis on specific columns and group by values
def analyze_data_new(data):
    analysis_window = tk.Tk()
    analysis_window.title("Column Analysis Results")

    # Specify the columns for which you want to perform group by and count
    group_by_columns = ["School_Id", "School_Type", "District", "Religion", "Cast", "Gender", "Ac_Year",  "Standard", "Student_Status"] #

    # Calculate the number of rows needed based on the number of columns
    num_columns = len(group_by_columns)
    num_tables = len(group_by_columns)

    # Create a 3x3 grid of tables
    num_rows = 3
    num_cols = 3

    # Calculate the total number of records
    total_records = len(data)

    # Create a frame for the label and place it at the top
    label_frame = tk.Frame(analysis_window)
    label_frame.grid(row=0, column=0, columnspan=num_cols, padx=10, pady=5, sticky="w")

    # Create a label displaying the total number of students
    total_label = tk.Label(label_frame, text=f"Total Students: {total_records}", font=("Helvetica", 16))
    total_label.pack()

    for i, column in enumerate(group_by_columns):
        # Create a frame for each table and label
        table_frame = tk.Frame(analysis_window)
        table_frame.grid(row=(i // num_cols) + 1, column=i % num_cols, padx=10, pady=5, sticky="nsew")

        # Group by the selected column and count unique values
        grouped_data = data.groupby(column).size().reset_index(name='Count')

        # Create a label for the column and place it in the frame
        column_label = tk.Label(table_frame, text=f"Analysis for Column: {column}")
        column_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Create a Treeview table for displaying the results
        table = ttk.Treeview(table_frame, columns=("Value", "Count"))
        table.heading("#1", text="Value")
        table.heading("#2", text="Count")

        # Specify the column width (adjust this as needed)
        table.column("#1", width=200)
        table.column("#2", width=100)

        for index, row in grouped_data.iterrows():
            table.insert("", "end", values=(row[column], row["Count"]))

        table.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Calculate and display the total row
        total_row = tk.Label(table_frame, text=f"Total: {grouped_data['Count'].sum()}")
        total_row.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

    # Create a vertical scrollbar for the window
    scrollbar = tk.Scrollbar(analysis_window, orient="vertical")
    scrollbar.grid(row=1, column=num_cols, rowspan=num_rows, sticky="ns")

    # Attach the scrollbar to each table
    for i in range(num_tables):
        analysis_window.grid_rowconfigure(i + 1, weight=1)
        analysis_window.grid_columnconfigure(i % num_cols, weight=1)

    analysis_window.mainloop()
    
    
# Create a function to display pie charts for all selected columns in a single window
def display_all_graphs(data):
    # Create a new window for the pie charts
    pie_window = tk.Tk()
    pie_window.geometry('1300x900')
    pie_window.title("All Graphs")

    # Create a Canvas widget for scrolling
    canvas = tk.Canvas(pie_window)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a scrollbar for the canvas
    scrollbar = ttk.Scrollbar(pie_window, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Configure the canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Create a frame to contain the pie charts
    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor=tk.NW)

    columns_per_row = 3
    current_row = 0
    current_column = 0

    for column in group_by_columns:
        if current_column == columns_per_row:
            current_row += 1
            current_column = 0

        # Group by the selected column and count unique values
        grouped_data = data.groupby(column).size().reset_index(name='Count')

        # Create a figure for the pie chart
        fig = Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)

        # Create a pie chart showing the distribution of the selected column
        ax.pie(grouped_data["Count"], labels=grouped_data[column], autopct='%1.1f%%', startangle=140)
        ax.set_title(f"{column} Distribution")

        # Embed the pie chart in the tkinter window
        pie_canvas = FigureCanvasTkAgg(fig, master=frame)
        pie_canvas.get_tk_widget().grid(row=current_row, column=current_column, padx=10, pady=10)

        current_column += 1

    # Create a window scrollbar
    canvas.config(scrollregion=canvas.bbox("all"))    
#Data Analysis
def analyze_data(data):
    # Extract data for analysis (e.g., count by gender)
    dropout_counts = {}
    for row in data:
        # gender = row[columns.index("Gender")]
        # g ender_counts[gender] = gender_counts.get(gender, 0) + 1
        dropout = row[columns.index("Student_Status")]
        dropout_counts[dropout] = dropout_counts.get(dropout, 0) + 1

     # Clear existing graphs (if any)
    for widget in f4.winfo_children():
        widget.destroy()
    # Create a bar chart for dropout distribution
    plt.figure(figsize=(5, 4))
    plt.bar(dropout_counts.keys(), dropout_counts.values())
    plt.title("Dropout Distribution")
    plt.xlabel("Student Status")
    plt.ylabel("Count")

    # Embed the bar chart in the tkinter frame f4
    canvas_bar = FigureCanvasTkAgg(plt.gcf(), master=f4)
    canvas_widget_bar = canvas_bar.get_tk_widget()
    canvas_widget_bar.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    
    
    dropout_counts = {}
    caste_counts = {"OPEN": 0, "SC": 0, "ST": 0, "OBC": 0}

    for row in data:
        dropout = row[columns.index("Student_Status")]
        dropout_counts[dropout] = dropout_counts.get(dropout, 0) + 1

        caste = row[columns.index("Cast")]
        caste_counts[caste] += 1
        
    # Clear existing graphs (if any)
    for widget in f5.winfo_children():
        widget.destroy()
    # Create a pie chart for caste distribution
    plt.figure(figsize=(4, 4))
    plt.pie(caste_counts.values(), labels=caste_counts.keys(), autopct='%1.1f%%', startangle=140)
    plt.title("Caste Distribution")

    # Embed the pie chart in the tkinter frame f4 below the bar chart
    canvas_pie = FigureCanvasTkAgg(plt.gcf(), master=f5)
    canvas_widget_pie = canvas_pie.get_tk_widget()
    canvas_widget_pie.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Call the analyze_data function
    
    
def clear_results():
    # Clear existing rows in the table
    for row in tree.get_children():
        tree.delete(row)
    for widget in f4.winfo_children():
        widget.destroy()
    for widget in f5.winfo_children():
        widget.destroy()
    district_combobox.set('')
    gender_combobox.set('')
    religion_combobox.set('')
    category_combobox.set('')
    school_type_combobox.set('')
    standard_combobox.set('')
    passout_dropout_combobox.set('')
    text_entry.delete(0, tk.END)  # Clear the text entry widget
def submit_query():
    # Get selected values from combo boxes

    selected_district = district_combobox.get()
    selected_gender= gender_combobox.get()
    selected_religion= religion_combobox.get()
    selected_category=category_combobox.get()
    selected_school_tpe=school_type_combobox.get()
    selected_standard=standard_combobox.get()
    selected_dropout=passout_dropout_combobox.get()
    user_input = text_entry.get()

    # Create a dynamic query based on selected values
    query = "SELECT * FROM school WHERE 1=1"


    if selected_district:
        query += f" AND district = '{selected_district}'"
    if selected_gender:
        query += f" AND gender = '{selected_gender}'"
    if selected_religion:
        query += f" AND religion = '{selected_religion}'"
    if selected_category:
        query += f" AND cast = '{selected_category}'"
    if selected_school_tpe:
        query += f" AND School_Type = '{selected_school_tpe}'"
    if selected_standard:
        query += f" AND Standard = {selected_standard}"
    if selected_dropout:
        query += f" AND Student_Status = '{selected_dropout}'"
    if user_input :
        query+= f"AND school_Id={user_input}    "


    # Execute the query and display the results in a table
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    

    # Clear existing rows in the table
    for row in tree.get_children():
        tree.delete(row)

    # Insert the results into the table
    for row_data in result:
        tree.insert("", "end", values=row_data)
    analyze_data(result)

def insert_data(cursor, data):
    insert_query = """
        INSERT INTO school (UID_No, School_Id, School_Type, District, Religion, Cast, Gender, Ac_Year, Cr_Year,Standard,Student_Status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.executemany(insert_query, data)
def select_csv_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        load_csv_data(file_path)

def load_csv_data(file_path):
   with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the header row if it exists

        # Connect to the MySQL database
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            # Read data from CSV and insert it into the database
            data_to_insert = [tuple(row) for row in csv_reader]
            insert_data(cursor, data_to_insert)

            # Commit changes and close the database connection
            connection.commit()
            connection.close()
            print("Data inserted successfully!")

        except mysql.connector.Error as error:
            print("Error:", error)

        
def on_submit():
    selected_state = state_combobox.get()
    selected_district = district_combobox.get()
    selected_taluka = taluka_combobox.get()
    selected_region = religion_combobox.get()
    selected_caste = category_combobox.get()
    selected_gender = gender_combobox.get()
    selected_standard = standard_combobox.get()
    
    # Print the selected values to the console
    print("Selected State:", selected_state)
    print("Selected District:", selected_district)
    print("Selected Taluka:", selected_taluka)
    print("Selected Region:", selected_region)
    print("Selected Caste:", selected_caste)
    print("Selected Gender:", selected_gender)
    print("Selected Standard:", selected_standard)
def on_select(event):
    selected_school_type = school_type_combobox.get()
    # You can perform actions based on the selected school type here
    print("Selected School Type:", selected_school_type)

def on_select(event):
    selected_category = category_combobox.get()
    # You can perform actions based on the selected category here
    print("Selected Category:", selected_category)

def on_select(event):
    selected_religion = religion_combobox.get()
    # You can perform actions based on the selected religion here
    print("Selected Religion:", selected_religion)
    
def populate_district_combobox(event):
    selected_state = state_combobox.get()
    district_combobox['values'] = list(gujarat_data[selected_state].keys())

''' def populate_taluka_combobox(event):
    selected_state = state_combobox.get()
    selected_district = district_combobox.get()
    taluka_combobox['values'] = gujarat_data[selected_state][selected_district] '''
# def callback():
#     l.configure(text=monthchoosen.get())
root = Tk()
root.title("E-Samiksha")

root.geometry("1100x750")
root.resizable(False, False)
f1 = Frame(root, bg="grey", borderwidth=6, relief=SUNKEN)
f1.pack(side=LEFT, fill="y")

f2 = Frame(root, borderwidth=8, bg="grey", relief=SUNKEN)
f2.pack(side=TOP, fill="x")


# Create a frame for the title with padding and margin
title_frame = tk.Frame(root, padx=20, pady=10)
title_frame.pack(fill="x")  # Expand horizontally

# Create a label for the title with custom font style and color
title_label = tk.Label(f1, text="E-Samiksha", font=("Helvetica", 23), fg="white", bg="blue",pady=3,borderwidth=8)
title_label.pack(padx=(0,2))
# l = Label(f1, text="Project Tkinter - Pycharm")
# l.pack( pady=142)
l = Label(f2, text="Admin Dashboard", font="Helvetica 14 bold")
l.pack()
f22 = Frame(root, borderwidth=8, relief=SUNKEN)
f22.pack(side=TOP, fill="x")
# Create a frame for the search widgets
# f22 = tk.Frame(root, borderwidth=8, relief=tk.SUNKEN)
# f22.grid(row=0, column=0, padx=10, pady=10, sticky="w")
# Create a Label for the search
l = tk.Label(f22, text="Search By School Id :", font="Helvetica 14",padx=10)
l.grid(row=0, column=0, sticky="w")
# Create a Text Entry widget for user input
text_entry = tk.Entry(f22)
text_entry.grid(row=0, column=1, sticky="w",padx=10)
# Create a Button to perform an action with the user input
action_button = ttk.Button(f22, text="Search", command=perform_action)
action_button.grid(row=0, column=3, sticky="w")

cursor = conn.cursor()
cursor.execute("select count('cast') from school")
result = cursor.fetchall()
total_records = result[0][0]
total_label1 = tk.Label(f22, text=f"Total Students: {total_records}", font=("Helvetica", 16))
total_label1.grid(row=0,column=10,sticky="ne",padx=(10,0))

''' l = Label(f22, text="Search School :", font="Helvetica 14")
l.pack()
# Create a Text Entry widget for user input
text_entry = tk.Entry(f22)
text_entry.pack()
# Create a Button to perform an action with the user input
action_button = ttk.Button(f22, text="Perform Action", command=perform_action)
action_button.pack() '''

''' 
name = Label(f1, text = "Name").grid(row=0,column=0)
email = Label(f1, text = "Email").grid(row=1,column=0) 
password = Label(f1, text = "Password").grid(row=2,column=0)  
sbmitbtn = Button(f1, text = "Submit",activebackground = "pink", activeforeground = "blue",command=callback).grid(row=3,column=0) 
# name.grid(row=0,column=0) '''


# 3 Layer State  
gujarat_data = {
    "Gujarat": {
        "Kachchh": ["Lakhpat", "Rapar", "Bhachau", "Anjar", "Bhuj", "Nakhatrana", "Abdasa", "Mandvi", "Mundra", "Gandhidham"],
        "Banaskantha": ["Tharad", "Dhanera", "Dantiwada", "Amirgadh", "Danta", "Vadgam", "Palanpur", "Deesa", "Deodar", "Bhabhar", "Kankrej"],
        "Patan": ["Santalpur", "Radhanpur", "Sidhpur", "Patan", "Harij", "Sami", "Chanasma"],
        "Mehsana": ["Satlasana", "Kheralu", "Unjha", "Visnagar", "Vadnagar", "Mahesana", "Becharaji", "Kadi"],
        "Sabarkantha": ["Vadali", "Idar", "Bhiloda", "Meghraj", "Himatnagar", "Prantij", "Talod", "Modasa", "Dhansura", "Malpur", "Bayad"],
        "Aravalli": ["Modasa", "Dhansura", "Malpur", "Bhiloda"],
        "Gandhinagar": ["Kalol", "Mansa", "Gandhinagar", "Dehgam"],
        "Ahmedabad": ["Mandal", "Detroj-Rampura", "Viramgam", "Sanand", "Ahmedabad City", "Daskroi", "Dholka", "Bavla", "Ranpur", "Barwala", "Dhandhuka"],
        "Surendranagar": ["Halvad", "Dhrangadhra", "Dasada", "Lakhtar", "Wadhwan", "Muli", "Chotila", "Sayla", "Chuda", "Limbdi"],
        "Rajkot": ["Maliya", "Morvi", "Tankara", "Wankaner", "Paddhari", "Rajkot", "Lodhika", "Kotda Sangani", "Jasdan", "Gondal", "Jamkandorna", "Upleta", "Dhoraji", "Jetpur"],
        "Jamnagar": ["Okhamandal", "Khambhalia", "Jamnagar", "Jodia", "Dhrol", "Kalavad", "Lalpur", "Kalyanpur", "Bhanvad", "Jamjodhpur"],
        "Porbandar": ["Porbandar", "Ranavav", "Kutiyana"],
        "Devbhoomi Dwarka": ["Khambhalia", "Bhanvad"],
        "Junagadh": ["Manavadar", "Vanthalali", "Junagadh", "Bhesan", "Visavadar", "Mendarda", "Keshod", "Mangrol", "Malia", "Talala", "Patana-Veraval", "Sutrapada", "Kodinar", "Una"],
        "Gir Somnath": ["Veraval", "Sutrapada", "Talala"],
        "Amreli": ["Kunkavav Vadia", "Babra", "Lathi", "Lilia", "Amreli", "Bagasara", "Dhari", "Savarkundla", "Khambha", "Jafrabad", "Rajula"],
        "Bhavnagar": ["Botad", "Vallabhipur", "Gadhada", "Umrala", "Bhavnagar", "Ghogha", "Sihor", "Gariadhar", "Palitana", "Talaja", "Mahuva"],
        "Botad": ["Botad", "Vallabhipur", "Gadhada", "Umrala"],
        "Narmada": ["Nandod", "Dediapada", "Sagbara", "Tilakwada"],
        "Navsari": ["Navsari", "Jalalpore", "Gandevi", "Chikhli", "Bansda"],
        "Valsad": ["Valsad", "Dharampur", "Pardi", "Kaprada", "Umbergaon"],
        "Surat": ["Olpad", "Mangrol", "Umarpada", "Mandvi", "Kamrej", "Surat City", "Chorasi", "Palsana", "Bardoli", "Mahuvad"],
        "Tapi": ["Nizar", "Uchchhal", "Songadh", "Vyara", "Valod"],
        "Dang": ["The Dangs"],
        "Dahod": ["Fatepura", "Jhalod", "Limkheda", "Dahod", "Garbada", "Devgadbaria", "Dhanpur"],
        "Anand": ["Tarapur", "Sojitra", "Umreth", "Anand", "Petlad", "Khambhat", "Borsad", "Anklav"],
        "Kheda": ["Kapadvanj", "Virpur", "Balasinor", "Khambhat", "Mehmedabad", "Kheda", "Mahudha", "Thasra"],
        "Panchmahal": ["Khanpur", "Kadana", "Santrampur", "Lunawada", "Shehera", "Morwa (Hadaf)", "Godhra", "Kalol", "Ghogha"],
        "Vadodara": ["Savli", "Vadodara", "Vaghodia", "JetpurPavi", "Chhota Udaipur", "Kavant", "Nasvadi", "Sankheda", "Dabhoi", "Padra", "Karjan"]
    }
}
# State ComboBox
state_label = tk.Label(f1, text="Select State:")
# state_label.pack(pady=(15,0))
state_combobox = ttk.Combobox(f1, values=list(gujarat_data.keys()))
state_combobox.bind("<<ComboboxSelected>>", populate_district_combobox)
# state_combobox.pack()

# District ComboBox
district_label = tk.Label(f1, text="Select District:",font="Helvetica 10",width=15)
district_label.pack(pady=(15,0))
# district_combobox = ttk.Combobox(f1, values=[])
district_combobox = ttk.Combobox(f1, values=combobox_value("District"))
# district_combobox.bind("<<ComboboxSelected>>", populate_taluka_combobox)
district_combobox.bind("<<ComboboxSelected>>", on_select)
district_combobox.pack()

# Taluka ComboBox
taluka_label = tk.Label(f1, text="Select Taluka:",font="Helvetica 10")
# taluka_label.pack(pady=(15,0))
taluka_combobox = ttk.Combobox(f1, values=[])
# taluka_combobox.pack()
# Religion ComboBox
religion_label = tk.Label(f1, text="Select Religion:",font="Helvetica 10")
religion_label.pack(pady=(15,0))

#religions = ["Hindu", "Muslim", "Sikh", "Christian", "Buddhist", "Jewish", "Other"]
religion_combobox = ttk.Combobox(f1, values=combobox_value("Religion"))
religion_combobox.bind("<<ComboboxSelected>>", on_select)
religion_combobox.pack()

# Gender ComboBox
gender_label = tk.Label(f1, text="Select Gender:",font="Helvetica 10")
gender_label.pack(pady=(15,0))
# genders = ["Male", "Female", "Other"]  # Add your genders here
gender_combobox = ttk.Combobox(f1, values=combobox_value("Gender"))
gender_combobox.pack()

# Category ComboBox
category_label = tk.Label(f1, text="Select Category:")
category_label.pack(pady=(15,0))

# categories = ["OPEN", "SC", "ST", "OBC", "Other"]
category_combobox = ttk.Combobox(f1, values=combobox_value("Cast"))
category_combobox.bind("<<ComboboxSelected>>", on_select)
category_combobox.pack()

# School Type ComboBox
school_type_label = tk.Label(f1, text="Select School Type:",font="Helvetica 10")
school_type_label.pack(pady=(15,0))

# school_types = ["Private", "Government"]
school_type_combobox = ttk.Combobox(f1, values=combobox_value("School_Type"))
school_type_combobox.bind("<<ComboboxSelected>>", on_select)
school_type_combobox.pack()

# Standard ComboBox
standard_label = tk.Label(f1, text="Select Standard:",font="Helvetica 10")
standard_label.pack(pady=(15,0))

# standards = [str(i) for i in range(8, 13)]  # Generate a list of grades 8 to 12
standard_combobox = ttk.Combobox(f1, values=combobox_value("Standard"))
standard_combobox.bind("<<ComboboxSelected>>",on_select)
standard_combobox.pack()

# Create a ComboBox for selecting passout/dropout
passout_dropout_label = ttk.Label(f1, text="Select Passout/Dropout:",font="Helvetica 10")
passout_dropout_label.pack(pady=(15,0))
passout_dropout_combobox = ttk.Combobox(f1, values=["Passout", "Dropout"])
passout_dropout_combobox.pack()

submit_button = tk.Button(f1, text="Submit", command=submit_query,width=15)
submit_button.pack(pady=(15,0))


f3 = Frame(root, bg="grey", borderwidth=6, relief=SUNKEN)
f3.pack(side=tk.BOTTOM, fill="x")
f4 = Frame(root, bg="grey", borderwidth=6, relief=SUNKEN)
f4.pack(side=tk.RIGHT, fill="x")
f5 = Frame(root, bg="grey", borderwidth=6, relief=SUNKEN)
f5.pack(side=tk.LEFT, fill="x")


# Create a frame for the graphs
# graph_frame = tk.Frame(f4)
# graph_frame.pack(side=tk.RIGHT, padx=10, pady=10, expand=2)

#CSV File 
select_button = tk.Button(f1, text="Select CSV File", command=select_csv_file)
select_button.pack(side=tk.BOTTOM,padx=10)
a=Label(f1,text="For Insert Data",font="Helvetica 14")
a.pack(side=tk.BOTTOM,padx=10, pady=10)


columns = ("UID_No", "School_Id","School_Type", "District", "Religion", "Cast", "Gender", "Ac_Year", "Cr_Year","Standard", "Student_Status") # Define column titles
tree = ttk.Treeview(f3, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)  # Set column titles
    # tree.column(col, width=ttk.Font().measure(col)) # Set initial column width
    tree.column(col, width=len(col) * 10)
tree.pack()
clear_button = tk.Button(f1, text="Clear", command=clear_results,width=15)
clear_button.pack(pady=(3,0))

# Full Analysis : 
a=Label(f22,text="Full Analysis :", font="Helvetica 14", pady=0)
# a.pack(pady="20")
a.grid(row=0,column=6,padx=(5,0))

# Create a button to trigger the analysis
analyze_button = tk.Button(f22, text="Tabular", command=lambda: analyze_data_new(fetch_data()))
# analyze_button.pack()
analyze_button.grid(row=0,column=7,padx=(2,0))


# Fetch the data from the database
data = fetch_data()

# Define the columns for which you want to create graphs
group_by_columns = ["School_Id", "School_Type", "District", "Religion", "Cast", "Gender", "Ac_Year", "Standard", "Student_Status"]

# Create a button to show all graphs
show_all_button = tk.Button(f22, text="Graphical", command=lambda: display_all_graphs(data))
# show_all_button.pack()
show_all_button.grid(row=0,column=8,padx=(2,0))
Edit = tk.Button(f1, text="Edit Data", command=on_submit,width=15)
# Edit.pack(pady=(15,0))

# root.attributes("-fullscreen", True)
root.mainloop()
