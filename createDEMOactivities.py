import pandas as pd
import random
from datetime import datetime, timedelta

# Categories and other choices
categories = [
    "Birthday", "Anniversary", "Holiday", "Project Deadline", "Meeting", "Appointment", 
    "Learning", "Coding", "Personal", "Family", "Social", "Travel", "Errands", 
    "Shopping", "Health", "Fitness", "Sports", "Hobbies", "Creative Pursuits", 
    "Volunteer", "Other"
]
statuses = ["Pending", "In Progress", "Completed"]
priorities = ["High", "Medium", "Low"]
activities = [
    "Birthday Party", "Wedding Anniversary", "Christmas Holiday", "Project X Deadline", 
    "Team Meeting", "Doctor Appointment", "Online Course", "Code Review", "Personal Development", 
    "Family Gathering", "Social Event", "Business Trip", "Grocery Shopping", 
    "Health Checkup", "Workout Session", "Football Match", "Painting", 
    "Photography", "Volunteer Work", "Miscellaneous Task"
]

# Function to generate random date within the year
def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())),
    )

start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)

# Generate activities
data = []
for i in range(65):  # One activity per day for simplicity
    activity_status = random.choice(statuses)
    if activity_status == "In Progress":
        start_timeline = random_date(start_date, end_date)
        end_timeline = start_timeline + timedelta(days=random.randint(1, 30))
        timeline = f"{start_timeline.strftime('%Y-%m-%d')} - {end_timeline.strftime('%Y-%m-%d')}"
    else:
        timeline = ""
    activity = {
        "ID": i + 1,
        "Category": random.choice(categories),
        "activity": random.choice(activities),
        "Status": activity_status,
        "notification": random_date(start_date, end_date).strftime("%Y-%m-%d %H:%M:%S"),
        "Timeline": timeline,
        "Deadline": random_date(start_date, end_date).strftime("%Y-%m-%d"),
        "Priority": random.choice(priorities),
        "Notes": f"Note for activity {i+1}"
    }
    data.append(activity)

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("activities.csv", index=False)
print("activities.csv file has been created.")
