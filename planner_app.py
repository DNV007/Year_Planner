import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QComboBox, QDateEdit, QLabel, QHeaderView, QMessageBox, QFormLayout, QFileDialog, QDateTimeEdit
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QColor, QPalette, QBrush, QIcon, QPixmap
import sqlite3
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from plyer import notification
import logging
from typing import List, Tuple

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO)

class Database:
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name
        self.conn = None

    def connect(self) -> sqlite3.Connection:
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def close(self) -> None:
        if self.conn:
            self.conn.close()

    def create_table(self) -> None:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                activity TEXT,
                status TEXT,
                notification TEXT,
                timeline TEXT,
                deadline TEXT,
                priority TEXT,
                notes TEXT
            )
        """)
        conn.commit()
        self.close()

    def load_data(self) -> pd.DataFrame:
        conn = self.connect()
        df = pd.read_sql_query("SELECT * FROM activities", conn)
        self.close()
        return df

    def add_activity(self, activity: dict) -> None:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO activities (category, activity, status, notification, timeline, deadline, priority, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            activity['category'], activity['activity'], activity['status'], activity['notification'],
            activity['timeline'], activity['deadline'], activity['priority'], activity['notes']
        ))
        conn.commit()
        self.close()

    def delete_activity(self, activity_id: int) -> None:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activities WHERE id=? ", (activity_id,))
        conn.commit()
        self.close()

class ActivityModel:
    def __init__(self, db: Database) -> None:
        self.db = db

    def load_data(self) -> pd.DataFrame:
        return self.db.load_data()

    def add_activity(self, activity: dict) -> None:
        self.db.add_activity(activity)

    def delete_activity(self, activity_id: int) -> None:
        self.db.delete_activity(activity_id)

class ActivityView(QMainWindow):
    def __init__(self, model: ActivityModel) -> None:
        super().__init__()
        self.model = model
        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle('Comprehensive Yearly Planner')
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon('app_icon2.ico'))
        # Set the background image
        background_pixmap = QPixmap('comprehensive_planner/resources/RS.jpeg')
        background_label = QLabel(self)
        background_label.setPixmap(background_pixmap)
        background_label.setGeometry(self.rect())  # Make sure the label covers the whole window

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))  # or any other color
        self.setPalette(palette)


        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Category", "Activity", "Status", "Notification", "Timeline", "Deadline", "Priority", "Notes"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            background-color: #ffffff;
            alternate-background-color: #f1f1f1;
            border: 1px solid #ccc;
            font-size: 14px;
            border-radius: 8px;
        """)
        layout.addWidget(self.table)

        # Form for adding new activity
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(30, 20, 30, 20)

        self.category_combobox = QComboBox()
        self.category_combobox.addItems([
                    "Birthday", "Anniversary", "Holiday", "Project Deadline", "Meeting", "Appointment", "Email", "Tax Return", 
                    "Learning", "Coding", "Personal", "Family", "Social", "Travel", "Errands", 
                    "Shopping", "Health", "Fitness", "Sports", "Hobbies", "Creative Pursuits", 
                    "Volunteer", "Other", "Wedding", "Graduation", "Party", "Conference", "Seminar", 
                    "Workshop", "Training", "Exam", "Interview", "Job Search", "Career Development", 
                    "Home Maintenance", "Household Chores", "Pet Care", "Gardening", "Cooking", 
                    "Financial Planning", "Budgeting", "Investing", "Real Estate", "Automotive", 
                    "Home Improvement", "DIY Project", "Renovation", "Moving", "Relocation", 
                    "Education", "Research", "Thesis", "Dissertation", "Academic", "School Event", 
                    "Community Service", "Charity Event", "Fundraiser", "Campaign", "Political Event", 
                    "Religious Event", "Spiritual", "Wellness", "Self-Care", "Mental Health", 
                    "Recreational", "Leisure", "Entertainment", "Arts", "Culture", "Music", 
                    "Theater", "Dance", "Film", "Photography", "Gaming", "Outdoor Activities", 
                    "Adventure", "Travel Planning", "Itinerary", "Trip", "Vacation", "Staycation"
                    ])
        self.category_combobox.setStyleSheet("""
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 14px;
            background-color: #ffffff;
        """)
        form_layout.addRow(QLabel("Category:"), self.category_combobox)

        self.activity_entry = QLineEdit()
        self.activity_entry.setStyleSheet("""
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 14px;
            background-color: #ffffff;
        """)
        form_layout.addRow(QLabel("Activity & Description:"), self.activity_entry)

        self.status_combobox = QComboBox()
        self.status_combobox.addItems(["Pending", "In Progress", "Completed"])
        self.status_combobox.setStyleSheet("""
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 14px;
            background-color: #ffffff;
        """)
        form_layout.addRow(QLabel("Status:"), self.status_combobox)

        self.notification_edit = QDateTimeEdit()
        self.notification_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.notification_edit.setDateTime(datetime.now().replace(hour=6, minute=0, second=0))
        self.notification_edit.setCalendarPopup(True)  # Show calendar popup for date selection
        self.notification_edit.setStyleSheet("""
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 14px;
            background-color: #ffffff;
        """)
        form_layout.addRow(QLabel("Notification Date and Time:"), self.notification_edit)

        self.timeline_edit = QLineEdit()
        self.timeline_edit.setStyleSheet("""
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 14px;
            background-color: #ffffff;
        """)
        form_layout.addRow(QLabel("Timeline:"), self.timeline_edit)

        self.deadline_edit = QDateEdit(datetime.now().replace(month=12, day=31))
        self.deadline_edit.setDisplayFormat("yyyy-MM-dd")
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setStyleSheet("""
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 14px;
            background-color: #ffffff;
        """)
        form_layout.addRow(QLabel("Deadline:"), self.deadline_edit)

        self.priority_combobox = QComboBox()
        self.priority_combobox.addItems(["High", "Medium", "Low"])
        self.priority_combobox.setStyleSheet("""
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 14px;
            background-color: #ffffff;
        """)
        form_layout.addRow(QLabel("Priority:"), self.priority_combobox)

        self.notes_edit = QLineEdit()
        self.notes_edit.setStyleSheet("""
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 14px;
            background-color: #ffffff;
        """)
        form_layout.addRow(QLabel("Notes:"), self.notes_edit)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(30, 20, 30, 20)

        self.add_button = QPushButton("Add Activity")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
            }
        """)
        self.add_button.clicked.connect(self.add_activity)
        button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Delete Selected Activity")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
            }
        """)
        self.delete_button.clicked.connect(self.delete_activity)
        button_layout.addWidget(self.delete_button)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 8px;
                font-size: 14px;
                background-color: #ffffff;
            }
        """)
        self.search_box.textChanged.connect(self.search_table)
        button_layout.addWidget(self.search_box)

        self.print_button = QPushButton("Print Table")
        self.print_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
            }
        """)
        self.print_button.clicked.connect(self.print_table)
        button_layout.addWidget(self.print_button)

        self.export_button = QPushButton("Export Data")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #FFC107;
                color: black;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
            }
        """)
        self.export_button.clicked.connect(self.export_data)
        button_layout.addWidget(self.export_button)

        self.start_date_edit = QDateEdit(datetime.now().replace(month=4, day=1))
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        button_layout.addWidget(self.start_date_edit)

        self.end_date_edit = QDateEdit(datetime.now().replace(month=12, day=31))
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        button_layout.addWidget(self.end_date_edit)

        self.gantt_chart_button = QPushButton("Generate Gantt Chart")
        self.gantt_chart_button.setStyleSheet("""
            QPushButton {
                background-color: #673AB7;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
            }
        """)
        self.gantt_chart_button.clicked.connect(self.generate_gantt_chart)
        button_layout.addWidget(self.gantt_chart_button)

        layout.addLayout(button_layout)

        self.load_data()

    def load_data(self):
        df = self.model.load_data()
        self.table.setRowCount(len(df))
        for i, row in df.iterrows():
            for j in range(len(row)):
                self.table.setItem(i, j, QTableWidgetItem(str(row.iloc[j])))

        self.table.resizeColumnsToContents()

    def add_activity(self):
        # Validate user input
        category = self.category_combobox.currentText()
        activity = self.activity_entry.text()
        status = self.status_combobox.currentText()
        notification = self.notification_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        timeline = self.timeline_edit.text()
        deadline = self.deadline_edit.date().toString("yyyy-MM-dd")
        priority = self.priority_combobox.currentText()
        notes = self.notes_edit.text()

        if not activity:
            QMessageBox.warning(self, 'Error', 'Activity description cannot be empty.')
            return

        # Insert activity into the database
        self.model.add_activity({
            'category': category,
            'activity': activity,
            'status': status,
            'notification': notification,
            'timeline': timeline,
            'deadline': deadline,
            'priority': priority,
            'notes': notes
        })

        # Update the table
        self.load_data()
        self.clear_form()

    def delete_activity(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            activity_id = self.table.item(selected_row, 0).text()
            self.model.delete_activity(activity_id)
            self.load_data()

    def search_table(self):
        search_text = self.search_box.text().lower()
        for row in range(self.table.rowCount()):
            match = False
            for column in range(self.table.columnCount()):
                item = self.table.item(row, column)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def print_table(self):
        try:
            from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)

            if dialog.exec_() == QPrintDialog.Accepted:
                self.table.render(printer)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Error printing table: {e}')

    def export_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx);;CSV Files (*.csv)")
        if path:
            df = self.model.load_data()
            try:
                if path.endswith('.csv'):
                    df.to_csv(path, index=False)
                elif path.endswith('.xlsx'):
                    df.to_excel(path, index=False)
                QMessageBox.information(self, 'Success', 'Data exported successfully.')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Error exporting data: {e}')

#
    def generate_gantt_chart(self):
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

        df = self.model.load_data()

        if df.empty:
            QMessageBox.warning(self, 'No Data', 'No activities found for the selected date range.')
            return

        # Group activities by name and combine timelines
        grouped_df = df.groupby('activity').agg({
            'status': 'first',
            'timeline': lambda x: ' ; '.join(x.dropna()),
            'deadline': 'first'
        }).reset_index()

        fig, ax = plt.subplots(figsize=(15, 8))

        # Customize colors and bar styles
        colors = ['#4CAF50', '#FFC107', '#f44336']  # Completed, In Progress, Pending
        status_to_color = {'Completed': 0, 'In Progress': 1, 'Pending': 2}
        bar_style = {'linewidth': 2, 'edgecolor': 'black'}

        for i, (activity, status, timelines, deadline) in enumerate(zip(grouped_df['activity'], grouped_df['status'], grouped_df['timeline'], grouped_df['deadline'])):
            timelines = timelines.split(' ; ')
            for timeline in timelines:
                if timeline and ' - ' in timeline:
                    try:
                        start, end = timeline.split(' - ')
                        start = datetime.strptime(start.strip(), "%Y-%m-%d")
                        end = datetime.strptime(end.strip(), "%Y-%m-%d")
                        ax.barh(i, (end - start).days, left=start, color=colors[status_to_color[status]], **bar_style)
                        # Adding text labels
                        #ax.text(start, i, start.strftime('%Y-%m-%d'), va='center', ha='right', fontsize=8, color='black')
                        #ax.text(end, i, end.strftime('%Y-%m-%d'), va='center', ha='left', fontsize=8, color='black')
                    except ValueError as e:
                        print(f"Error parsing timeline for activity '{activity}': {e}")

        # Add task labels
        ax.set_yticks(range(len(grouped_df)))
        ax.set_yticklabels(grouped_df['activity'], fontsize=12, fontweight='bold')

        # Customize axis labels and gridlines
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.grid(True, which='major', axis='both', linestyle='--', alpha=0.5)

        # Set background color
        ax.set_facecolor('#f9f9f9')

        # Add legend
        legend_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor=color) for color in colors]
        legend_labels = ['Completed', 'In Progress', 'Pending']
        ax.legend(legend_handles, legend_labels, loc='upper right', fontsize=10, frameon=False)

        # Improve overall layout and aesthetics
        plt.xlabel("Date", fontsize=14, fontweight='bold')
        plt.ylabel("Activity", fontsize=14, fontweight='bold')
        plt.title("Gantt Chart", fontsize=16, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()


    def clear_form(self):
        self.category_combobox.setCurrentIndex(0)
        self.activity_entry.clear()
        self.status_combobox.setCurrentIndex(0)
        self.notification_edit.setDateTime(datetime.now().replace(hour=6, minute=0, second=0))
        self.timeline_edit.clear()
        self.deadline_edit.setDate(datetime.now())
        self.priority_combobox.setCurrentIndex(0)
        self.notes_edit.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    db = Database('activities.db')
    db.create_table()
    model = ActivityModel(db)
    view = ActivityView(model)
    view.show()
    sys.exit(app.exec_())
