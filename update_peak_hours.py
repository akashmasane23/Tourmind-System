import pandas as pd
import random

# Load data
places_df = pd.read_csv("data/places.csv")
peak_df = pd.read_csv("data/peak_hours_nearby.csv")

# Merge to get activity_type
df = pd.merge(peak_df, places_df[['place_name', 'activity_type']], left_on='place', right_on='place_name', how='left')

# Define logical peak and avoid times based on activity type
def get_logical_times(activity):
    activity = str(activity).lower()
    
    if "temple" in activity or "spiritual" in activity:
        # Temples are busy early morning and evening. Best to go mid-morning or afternoon.
        best_opts = ["Morning (9-11 AM)", "Afternoon (1-4 PM)"]
        avoid_opts = ["Early Morning (6-9 AM)", "Evening (5-8 PM)"]
        
    elif "fort" in activity or "adventure" in activity:
        # Forts are too hot in the afternoon. Best early morning.
        best_opts = ["Early Morning (6-9 AM)", "Morning (8-11 AM)"]
        avoid_opts = ["Afternoon (1-4 PM)", "Evening (Late)"]
        
    elif "mall" in activity or "shopping" in activity or "market" in activity:
        # Malls open at 10 or 11. Busy in evening.
        best_opts = ["Morning (11 AM - 1 PM)", "Afternoon (1-4 PM)"]
        avoid_opts = ["Evening (5-9 PM)", "Weekends"]
        
    elif "museum" in activity or "historical" in activity or "palace" in activity:
        # Museums usually open around 9-10 AM. Busy in afternoon/weekend.
        best_opts = ["Morning (9-11 AM)", "Early Afternoon (1-3 PM)"]
        avoid_opts = ["Afternoon (3-5 PM)", "Weekends"]
        
    elif "park" in activity or "nature" in activity or "garden" in activity:
        # Parks are hot in afternoon. Busy in evening.
        best_opts = ["Early Morning (6-9 AM)", "Morning (8-10 AM)"]
        avoid_opts = ["Evening (5-8 PM)", "Afternoon (1-4 PM)"]
        
    else:
        # Default fallback
        best_opts = ["Morning (9-11 AM)", "Afternoon (2-4 PM)"]
        avoid_opts = ["Evening (5-8 PM)", "Weekends"]
        
    return random.choice(best_opts), random.choice(avoid_opts)

# Update the times intelligently
for idx, row in df.iterrows():
    bt, at = get_logical_times(row['activity_type'])
    
    # Specific override for Shaniwar Wada
    if "shaniwar wada" in str(row['place']).lower():
        bt = "Morning (9-11 AM)"
        at = "Evening (5-7 PM)"
        
    # Specific override for Dagdusheth
    if "dagdusheth" in str(row['place']).lower():
        bt = "Afternoon (1-3 PM) - Less crowded"
        at = "Evening (6-9 PM) - Aarti time"

    df.at[idx, 'best_time'] = bt
    df.at[idx, 'avoid_time'] = at

# Save back to CSV
df[['place', 'best_time', 'avoid_time', 'peak_season', 'average_crowd', 'nearby_attractions']].to_csv("data/peak_hours_nearby.csv", index=False)
print("Updated peak_hours_nearby.csv intelligently.")
