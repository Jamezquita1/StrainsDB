import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta
from pushbullet import Pushbullet
from datetime import timedelta

#Sets timer on pushbullet reminders
REMINDER_DELAY = timedelta(days=7)

class StrainDatabaseApp:
    def __init__(self, root
        self.root = root
        self.root.title("Strain Database")

        # Pushbullet API Key (replace with your actual API key)
        self.pushbullet_api_key = ""

        # Variables for entry form
        self.entry_name_var = tk.StringVar()
        self.genotype_var = tk.StringVar()
        self.location_var = tk.StringVar()
        self.construction_var = tk.StringVar()
        self.details_var = tk.StringVar()
        self.date_frozen_var = tk.StringVar()
        self.user_var = tk.StringVar()
        self.vials_var = tk.StringVar()

        # Create frames for different screens
        self.home_frame = ttk.Frame(root)
        self.entry_frame = ttk.Frame(root)
        self.vial_usage_frame = ttk.Frame(root)

        # Initialize the viewer frame
        self.create_database_viewer()
        self.create_vial_usage_viewer()

        # Set the initial screen to the home screen
        self.current_frame = self.home_frame

        self.create_home_screen()
        self.create_entry_screen()

        # Connect to SQLite database
        self.conn = sqlite3.connect("strain_database.db")
        self.create_table()

    def create_home_screen(self):
        # Home Screen
        ttk.Label(self.home_frame, text="C. elegans Strains", font=("Helvetica", 16)).pack(pady=20)

        # Add Entry Button
        ttk.Button(self.home_frame, text="Add Entry", command=self.show_entry_screen).pack(pady=10)

        # View Database Button
        ttk.Button(self.home_frame, text="View Database", command=self.show_database_screen).pack(pady=10)

        # Add a "Vial Usage" button
        ttk.Button(self.home_frame, text="Vial Usage", command=self.show_vial_usage).pack(pady=10)

        self.home_frame.pack(expand=True, fill="both")

    def create_entry_screen(self):
        # Entry Screen
        ttk.Label(self.entry_frame, text="Entry Form", font=("Helvetica", 16)).pack(pady=20)

        # Entry Name
        self.create_label_and_entry("Entry Name:", self.entry_name_var)
        # Genotype
        self.create_label_and_entry("Genotype:", self.genotype_var)
        # Location
        self.create_label_and_entry("Location:", self.location_var)
        # Construction
        self.create_label_and_entry("Construction:", self.construction_var)
        # Details
        self.create_label_and_entry("Details:", self.details_var)
        # Date Frozen
        ttk.Label(self.entry_frame, text="Date Frozen:").pack()
        self.date_frozen_entry = ttk.Entry(self.entry_frame, textvariable=self.date_frozen_var)
        self.date_frozen_entry.pack()
        # User
        self.create_label_and_entry("User:", self.user_var)
        # Vials
        self.create_label_and_entry("Vials:", self.vials_var)

        # Add Entry Button
        ttk.Button(self.entry_frame, text="Add Entry", command=self.add_entry).pack(pady=10)
        # Save Edit Button
        ttk.Button(self.entry_frame, text="Save Edit", command=self.save_edit).pack(pady=10)
        # Cancel Button
        ttk.Button(self.entry_frame, text="Cancel", command=self.cancel_edit).pack(pady=10)

    def create_label_and_entry(self, label_text, text_variable):
        ttk.Label(self.entry_frame, text=label_text).pack()
        ttk.Entry(self.entry_frame, textvariable=text_variable).pack()

    def create_database_viewer(self):
        # Database Viewer Screen
        self.viewer_frame = ttk.Frame(self.root)
        ttk.Label(self.viewer_frame, text="Database Viewer", font=("Helvetica", 16)).pack(pady=20)

        # Create a Treeview widget to display the entries
        columns = ("ID", "Entry Name", "Genotype", "Location", "Construction", "Details", "Date Frozen", "User", "Vials")
        self.tree = ttk.Treeview(self.viewer_frame, columns=columns, show="headings", selectmode="browse")

        # Set column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)  # Adjust width as needed

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.viewer_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        # Pack the Treeview and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Back to Home Button
        ttk.Button(self.viewer_frame, text="Back to Home", command=self.show_home_screen_from_viewer).pack(pady=15)
        # Delete Entry Button
        ttk.Button(self.viewer_frame, text="Delete Entry", command=self.delete_selected_entry).pack(pady=5)
        # Add an "Edit" button
        ttk.Button(self.viewer_frame, text="Edit", command=self.edit_selected_entry).pack(pady=5)

        # Add Take Vial Button
        ttk.Button(self.viewer_frame, text="Take Vial", command=self.take_vial).pack(pady=15)

        # Bind the Treeview to call edit_selected_entry when double-clicking an entry
        self.tree.bind("<Double-1>", lambda event: self.edit_selected_entry())

    def show_home_screen(self):
        self.entry_frame.pack_forget()
        self.home_frame.pack(expand=True, fill="both")
        self.current_frame = self.home_frame

    def show_entry_screen(self, editing=False):
        self.home_frame.pack_forget()
        self.entry_frame.pack(expand=True, fill="both")
        self.current_frame = self.entry_frame

        # Remove existing buttons and entry widgets
        for widget in self.entry_frame.winfo_children():
            widget.pack_forget()

        # Create Entry widgets
        labels_and_vars = [
            ("Entry Name:", self.entry_name_var),
            ("Genotype:", self.genotype_var),
            ("Location:", self.location_var),
            ("Construction:", self.construction_var),
            ("Details:", self.details_var),
            ("Date Frozen:", self.date_frozen_var),
            ("User:", self.user_var),
            ("Vials:", self.vials_var)
        ]

        for label, var in labels_and_vars:
            ttk.Label(self.entry_frame, text=label).pack()
            ttk.Entry(self.entry_frame, textvariable=var).pack()

        # Buttons for both modes
        if not editing:
            ttk.Button(self.entry_frame, text="Add Entry", command=self.add_entry).pack(pady=10)
            ttk.Button(self.entry_frame, text="Cancel", command=self.cancel_entry).pack(pady=10)
        else:
            ttk.Button(self.entry_frame, text="Save Edit", command=self.save_edit).pack(pady=10)
            ttk.Button(self.entry_frame, text="Cancel", command=self.cancel_edit).pack(pady=10)

        # Fetch and display the selected entry information when editing
        if editing:
            selected_item = self.tree.selection()
            entry_id = self.tree.item(selected_item, "values")[0]  # Assuming the ID is the first column

            # Fetch data from the database based on the ID
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM strain_entries WHERE id=?", (entry_id,))
            entry_data = cursor.fetchone()

            # Directly set values in Entry widgets
            self.entry_name_var.set(entry_data[1])  # Entry Name
            self.genotype_var.set(entry_data[2])  # Genotype
            self.location_var.set(entry_data[3])  # Location
            self.construction_var.set(entry_data[4])  # Construction
            self.details_var.set(entry_data[5])  # Details
            self.date_frozen_var.set(entry_data[6])  # Date Frozen
            self.user_var.set(entry_data[7])  # User
            self.vials_var.set(entry_data[8])  # Vials

    def show_database_screen(self):
        # If the viewer frame doesn't exist, create it
        if not hasattr(self, 'viewer_frame'):
            self.create_database_viewer()

        # Switch to the database viewer screen
        self.home_frame.pack_forget()
        self.viewer_frame.pack(expand=True, fill="both")
        self.current_frame = self.viewer_frame

        # Populate the Treeview with data from the database
        self.populate_treeview()

    def populate_treeview(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch data from the database and insert into Treeview
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM strain_entries")
        entries = cursor.fetchall()

        for entry in entries:
            # Specify the order of columns when inserting into the Treeview
            new_values = (
                entry[0],  # id
                entry[1],  # entry_name
                entry[2],  # genotype
                entry[3],  # location
                entry[4],  # construction
                entry[5],  # details
                entry[6],  # date_frozen
                entry[7],  # user
                entry[8]  # vials
            )
            self.tree.insert("", "end", iid=entry[0], values=new_values)

    def print_table_schema(self, table_name='strain_entries'):
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = cursor.fetchall()
        print("Table Schema:")
        for column in schema:
            print(column)

    def add_entry(self):
        # Get values from Entry widgets
        entry_name = self.entry_name_var.get()
        genotype = self.genotype_var.get()
        location = self.location_var.get()
        construction = self.construction_var.get()
        details = self.details_var.get()
        date_frozen = self.date_frozen_var.get()
        user = self.user_var.get()
        vials = self.vials_var.get()

        # Validate date format
        if not self.is_valid_date(date_frozen):
            messagebox.showerror("Invalid Date", "Please enter a valid date in the format YYYY-MM-DD.")
            return

        # Calculate the next entry number
        next_entry_number = self.calculate_next_entry_number()

        # Save the data to the SQLite database
        self.save_to_database(next_entry_number, entry_name, genotype, location, construction, details, date_frozen, user, vials)

        # Clear Entry widgets for the next entry
        self.clear_entries()

        # After adding, show the entry screen without editing

        # Fetch and display the added entry information in the Treeview
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM strain_entries WHERE id=?", (next_entry_number,))

        # Commit the changes before fetching data
        self.conn.commit()

        entry_data = cursor.fetchone()

        # Populate the Treeview with the added entry
        new_values = (
            entry_data[0], entry_data[1], entry_data[2], entry_data[3], entry_data[4], entry_data[5], entry_data[6],
            entry_data[7], entry_data[8])
        self.tree.insert("", "end", values=new_values)

    def is_valid_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def calculate_next_entry_number(self):
        # Fetch the maximum ID from the strain_entries table
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(id) FROM strain_entries")
        max_id = cursor.fetchone()[0]

        # If there are no entries, start from 1, otherwise increment the maximum ID
        return 1 if max_id is None else max_id + 1

    def clear_entries(self):
        self.entry_name_var.set("")
        self.genotype_var.set("")
        self.location_var.set("")
        self.construction_var.set("")
        self.details_var.set("")
        self.date_frozen_var.set("")
        self.user_var.set("")
        self.vials_var.set("")

    def create_table(self):
        # Create a table if it doesn't exist
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strain_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_name TEXT,
                genotype TEXT,
                location TEXT,  
                construction TEXT,  
                details TEXT,
                date_frozen TEXT,
                user TEXT,
                vials INTEGER
            )
        ''')

        # Create a table if it doesn't exist for vial usage
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vial_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                entry_name TEXT,
                genotype TEXT,
                date TEXT,
                original_vials INTEGER,
                vials_taken INTEGER,
                vials_remaining INTEGER,
                FOREIGN KEY (entry_name, genotype) REFERENCES strain_entries (entry_name, genotype)
            )
        ''')

        self.conn.commit()

    def delete_selected_entry(self):
        # Get the selected item in the Treeview
        selected_item = self.tree.selection()

        if not selected_item:
            # No item selected, show a message or handle accordingly
            messagebox.showinfo("Delete Entry", "Please select an entry to delete.")
            return

        # Get the entry ID from the selected item
        entry_id = self.tree.item(selected_item, "values")[0]

        # Confirm deletion with the user
        confirmation = messagebox.askyesno("Delete Entry", "Are you sure you want to delete this entry?")

        if confirmation:
            # Delete the entry from the database
            self.delete_entry_from_database(entry_id)

            # Refresh the Treeview to reflect the changes
            self.populate_treeview()

    def edit_selected_entry(self):
        selected_item = self.tree.selection()

        if not selected_item:
            messagebox.showinfo("Edit Entry", "Please select an entry to edit.")
            return

        # Get values of the selected entry
        entry_id = self.tree.item(selected_item, "values")[0]  # Assuming the ID is the first column

        # Switch to the entry form screen for editing
        self.show_entry_screen(editing=True)

        # Populate the entry form with the data of the selected entry
        self.entry_name_var.set(self.tree.item(selected_item, "values")[1])  # Entry Name
        self.genotype_var.set(self.tree.item(selected_item, "values")[2])  # Genotype
        self.location_var.set(self.tree.item(selected_item, "values")[3])  # Location
        self.construction_var.set(self.tree.item(selected_item, "values")[4])  # Construction
        self.details_var.set(self.tree.item(selected_item, "values")[5])  # Details
        self.date_frozen_var.set(self.tree.item(selected_item, "values")[6])  # Date Frozen
        self.user_var.set(self.tree.item(selected_item, "values")[7])  # User
        self.vials_var.set(self.tree.item(selected_item, "values")[8])  # Vials

    def delete_entry_from_database(self, entry_id):
        # Delete entry from the database based on the entry ID
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM strain_entries WHERE id=?", (entry_id,))
        self.conn.commit()

    def save_to_database(self, entry_id, entry_name, genotype, location, construction, details, date_frozen, user, vials):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO strain_entries (id, entry_name, genotype, location, construction, details, date_frozen, user, vials)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, entry_name, genotype, location, construction, details, date_frozen, user, int(vials)))
        self.conn.commit()

    def cancel_edit(self):
        # Clear Entry widgets
        self.clear_entries()
        # Hide the entry frame
        self.entry_frame.pack_forget()
        # Switch back to the database viewer screen without saving changes
        self.show_database_screen()

    def cancel_entry(self):
        # Clear Entry widgets
        self.clear_entries()
        # Hide the entry frame
        self.entry_frame.pack_forget()
        # Switch back to the home screen without saving changes
        self.show_home_screen()

    def save_edit(self):
        # Get values from Entry widgets
        entry_name = self.entry_name_var.get()
        genotype = self.genotype_var.get()
        location = self.location_var.get()
        construction = self.construction_var.get()
        details = self.details_var.get()
        date_frozen = self.date_frozen_var.get()
        user = self.user_var.get()
        vials = self.vials_var.get()

        # Get the ID of the selected entry
        selected_item = self.tree.selection()
        entry_id = self.tree.item(selected_item, "values")[0]

        # Update the data in the SQLite database
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE strain_entries
            SET entry_name=?, genotype=?, location=?, construction=?, details=?, date_frozen=?, user=?, vials=?
            WHERE id=?
        ''', (entry_name, genotype, location, construction, details, date_frozen, user, int(vials), entry_id))
        self.conn.commit()

        # Update the Treeview with the edited entry data
        edited_data = (entry_id, entry_name, genotype, location, construction, details, date_frozen, user, int(vials))
        self.update_treeview(selected_item, edited_data)

        # Inform the user that the edit was successful
        messagebox.showinfo("Edit Entry", "Entry successfully edited.")

        # Clear Entry widgets
        self.clear_entries()
        # Hide the entry frame
        self.entry_frame.pack_forget()
        # Switch back to the database viewer screen and refresh the Treeview
        self.show_database_screen()

    def update_treeview(self, item, edited_data):
        # Update the data in the SQLite database
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE strain_entries
            SET entry_name=?, genotype=?, location=?, construction=?, details=?, date_frozen=?, user=?, vials=?
            WHERE id=?
        ''', (edited_data[1], edited_data[2], edited_data[3], edited_data[4], edited_data[5],
              edited_data[6], edited_data[7], edited_data[8], edited_data[0]))
        self.conn.commit()

        # Fetch the current selected item
        selected_item = self.tree.selection()

        # Clear existing items in the Treeview
        for child in self.tree.get_children():
            self.tree.delete(child)

        # Repopulate the Treeview with data from the database
        self.populate_treeview()

        # Check if the selected item exists and set the selection again
        if selected_item and self.tree.exists(selected_item):
            self.tree.selection_set(selected_item)
            self.tree.focus(selected_item)

    def show_home_screen_from_viewer(self):
        self.viewer_frame.pack_forget()
        self.home_frame.pack(expand=True, fill="both")
        self.current_frame = self.home_frame

    def take_vial(self):
        # Get the selected item in the Treeview
        selected_item = self.tree.selection()

        if not selected_item:
            messagebox.showinfo("Take Vial", "Please select an entry to take a vial.")
            return

        # Prompt the user for their name
        user_name = simpledialog.askstring("Take Vial", "Enter your name:")
        if not user_name:
            return  # User canceled the input

        # Get the entry ID and vial count from the selected item
        entry_id = self.tree.item(selected_item, "values")[0]
        entry_name = self.tree.item(selected_item, "values")[1]
        genotype = self.tree.item(selected_item, "values")[2]
        original_vials = int(self.tree.item(selected_item, "values")[8])

        if original_vials == 0:
            messagebox.showinfo("Take Vial", "No vials left!")
        else:
            # Prompt the user for the number of vials to take
            vials_taken = simpledialog.askinteger("Take Vial", "Enter the number of vials to take:",
                                                  minvalue=1, maxvalue=original_vials)

            if vials_taken is None:
                return  # User canceled the input

            # Calculate the remaining vials after the user takes some
            vials_remaining = max(0, original_vials - vials_taken)

            # Update the vial count in the "strain_entries" table
            cursor = self.conn.cursor()
            cursor.execute("UPDATE strain_entries SET vials=? WHERE id=?", (vials_remaining, entry_id))
            self.conn.commit()

            # Record the vial usage in the "vial_usage" table
            self.record_vial_usage(user_name, entry_name, genotype, original_vials, vials_taken, vials_remaining)

            # Fully refresh the database viewer to reflect changes
            self.refresh_database_viewer()

            # Show a pop-up notification for taking vials
            messagebox.showinfo("Take Vial",
                                f"{vials_taken} vials taken. Remaining: {vials_remaining}/{original_vials}")

            # Check if this is the last vial
            if vials_remaining == 0:
                self.handle_last_vial(entry_id, entry_name, genotype)

    def handle_last_vial(self, entry_id, entry_name, genotype):
        # Show a pop-up for the last vial and ask for a reminder
        response = messagebox.askquestion(
            "Take Vial",
            f"Last vial taken for {entry_name}, ({genotype}). Please refreeze the strain! Would you like a 1-week reminder?"
        )

        if response == "yes":
            # Schedule a reminder for 1 week
            self.schedule_reminder(entry_id, entry_name, genotype)

    def schedule_reminder(self, entry_id, entry_name, genotype):
        # Calculate the date for the reminder
        reminder_date = datetime.now() + REMINDER_DELAY

        # Format the date as a string (optional, unused in this snippet)
        formatted_date = reminder_date.strftime("%Y-%m-%d %H:%M:%S")

        # Notification title and body
        title = "Strain Reminder"
        body = f"Don't forget to refreeze the strain {entry_name}, ({genotype})!"

        # Send notification
        self.send_push_notification(title, body)

    def send_push_notification(self, title, body):
        # Check if the Pushbullet API key is set
        if not self.pushbullet_api_key:
            messagebox.showinfo("Pushbullet API Key", "Please set your Pushbullet API key.")
            return

        # Send the Pushbullet notification
        pb = Pushbullet(self.pushbullet_api_key)
        pb.push_note(title, body)

    def record_vial_usage(self, user_name, entry_name, genotype, original_vials, vials_taken, vials_remaining):
        # Convert original_vials to an integer before recording
        original_vials = int(original_vials)

        # Record vial usage in the "vial_usage" table
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO vial_usage (user, entry_name, genotype, date, original_vials, vials_taken, vials_remaining)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_name, entry_name, genotype, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              original_vials, vials_taken, original_vials - vials_taken))
        self.conn.commit()

    def create_vial_usage_viewer(self):
        # Vial Usage Viewer Screen
        ttk.Label(self.vial_usage_frame, text="Vial Usage Viewer", font=("Helvetica", 16)).pack(pady=20)

        # Create a Treeview widget to display vial usage
        columns_vial_usage = ("ID", "User", "Entry Name", "Genotype", "Date", "Vials Taken", "Vials Remaining")
        self.tree_vial_usage = ttk.Treeview(self.vial_usage_frame, columns=columns_vial_usage, show="headings",
                                            selectmode="browse")

        # Set column headings
        for col in columns_vial_usage:
            self.tree_vial_usage.heading(col, text=col)
            self.tree_vial_usage.column(col, width=100)  # Adjust width as needed

        # Add scrollbar
        scrollbar_vial_usage = ttk.Scrollbar(self.vial_usage_frame, orient="vertical",
                                             command=self.tree_vial_usage.yview)
        self.tree_vial_usage.configure(yscroll=scrollbar_vial_usage.set)

        # Pack the Treeview and scrollbar
        self.tree_vial_usage.pack(side="left", fill="both", expand=True)
        scrollbar_vial_usage.pack(side="right", fill="y")

        # Back to Home Button
        ttk.Button(self.vial_usage_frame, text="Back to Home", command=self.show_home_screen_from_vial_usage).pack(
            pady=10)

        # Hide the frame initially
        self.vial_usage_frame.pack_forget()

    def populate_vial_usage_treeview(self):
        # Clear existing items
        for item in self.tree_vial_usage.get_children():
            self.tree_vial_usage.delete(item)

        # Fetch vial usage data from the database and insert into Treeview
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM vial_usage")
        vial_usage_entries = cursor.fetchall()

        for vial_usage_entry in vial_usage_entries:
            # Format the date to display only the date portion
            formatted_date = datetime.strptime(vial_usage_entry[4], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")

            # Specify the order of columns when inserting into the Treeview
            new_values = (
                vial_usage_entry[0],  # id
                vial_usage_entry[1],  # user
                vial_usage_entry[2],  # entry_name
                vial_usage_entry[3],  # genotype
                formatted_date,  # formatted date
                vial_usage_entry[6],  # vials_taken
                vial_usage_entry[7]  # remaining_vials
            )
            self.tree_vial_usage.insert("", "end", iid=vial_usage_entry[0], values=new_values)

    def show_home_screen_from_vial_usage(self):
        # Hide the vial usage frame
        self.vial_usage_frame.pack_forget()

        # Switch back to the home screen
        self.home_frame.pack(expand=True, fill="both")
        self.current_frame = self.home_frame

    def show_database_screen_from_vial_usage(self):
        # Hide the vial usage frame
        self.vial_usage_frame.pack_forget()

        # If the viewer frame doesn't exist, create it
        if not hasattr(self, 'viewer_frame'):
            self.create_database_viewer()

        # Switch to the database viewer screen
        self.viewer_frame.pack(expand=True, fill="both")
        self.current_frame = self.viewer_frame

        # Populate the Treeview with data from the database
        self.populate_treeview()

    def show_vial_usage(self):
        # If the vial usage frame doesn't exist, create it
        if not hasattr(self, 'vial_usage_frame'):
            self.create_vial_usage_viewer()

        # Populate the vial usage Treeview with data from the database
        self.populate_vial_usage_treeview()

        # Switch to the vial usage screen
        self.home_frame.pack_forget()
        self.viewer_frame.pack_forget()  # Hide the database viewer if it's currently visible
        self.vial_usage_frame.pack(expand=True, fill="both")
        self.current_frame = self.vial_usage_frame

    def refresh_database_viewer(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM strain_entries")
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = StrainDatabaseApp(root)
    root.mainloop()
