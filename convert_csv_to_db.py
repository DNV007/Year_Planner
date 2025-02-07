import pandas as pd
import sqlite3

def convert_csv_to_sqlite(csv_file, db_name):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Print DataFrame columns to check for correct names
    print("Columns in CSV file:", df.columns)

    # Connect to (or create) the SQLite database
    conn = sqlite3.connect(db_name)

    # Drop the activities table if it exists
    conn.execute("DROP TABLE IF EXISTS activities")

    # Create the activities table
    create_table_query = """
    CREATE TABLE activities (
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
    """
    conn.execute(create_table_query)

    # Map CSV column names to SQLite column names
    column_mapping = {
        'Activity & Description': 'activity',
        'Status': 'status',
        'Notification Date and time': 'notification',
        'Timeline': 'timeline',
        'Deadline': 'deadline',
        'Category': 'category',
        'Priority': 'priority',
        'Notes': 'notes'
    }

    # Rename columns in DataFrame to match SQLite schema
    df.rename(columns=column_mapping, inplace=True)

    # Ensure all required columns are present
    required_columns = ['category', 'activity', 'status', 'notification', 'timeline', 'deadline', 'priority', 'notes']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"CSV file is missing required column: {col}")

    # Handle potential issues with data types
    # Convert datetime columns to strings if necessary
    for column in ['notification', 'deadline']:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors='coerce').astype(str)

    # Insert data into the activities table
    df.to_sql('activities', conn, if_exists='replace', index=False)

    # Close the database connection
    conn.close()

    print("CSV data successfully converted to SQLite database.")

# File names
csv_file = "activities.csv"
db_name = "activities.db"

# Run the conversion
convert_csv_to_sqlite(csv_file, db_name)
