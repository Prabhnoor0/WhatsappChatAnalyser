import re
import pandas as pd

def preprocess(data):
    # Regular expression pattern to match the date, time, and am/pm or 24 hour format
    pattern = r'(\d{1,2}/\d{1,2}/\d{4}), (\d{1,2}:\d{2}(?:\s?[APap][Mm])?) - (.*?): (.*)'

    # Lists to hold the extracted data
    dates = []
    times = []
    periods = []
    senders = []
    messages = []

    # Temporary variables to handle multiline messages
    current_message = ""
    current_date = ""
    current_time = ""
    current_period = ""
    current_sender = ""

    # Process the dataset
    for line in data.split('\n'):
        match = re.match(pattern, line)
        if match:
            if current_message:  # Save the previous message if there is one
                messages.append(current_message.strip())
                dates.append(current_date)
                times.append(current_time)
                senders.append(current_sender)
                periods.append(current_period)

            # Extract new date, time, message, and sender
            current_date = match.group(1)
            current_time = match.group(2)
            current_sender = match.group(3)
            current_message=match.group(4)
            
            # Append the date, time, and sender to their respective lists
            dates.append(current_date)
            times.append(current_time)
            senders.append(current_sender)
                
                # Determine period (AM/PM or 24-hour)
            if "AM" in current_time.upper():
                current_period = "AM"
            elif "PM" in current_time.upper():
                current_period = "PM"
            else:
                current_period = "24-hour"

            periods.append(current_period)
        
        else:
            # Continuation of the previous message
            current_message += " " + line.strip()

    # Append the last message
    if current_message:
        messages.append(current_message.strip())
        dates.append(current_date)
        times.append(current_time)
        senders.append(current_sender)
        periods.append(current_period)

    # Debugging: print lengths of all lists
    #messages.pop()
    print(f"Lengths -> Dates: {len(dates)}, Times: {len(times)}, Periods: {len(periods)}, Senders: {len(senders)}, Messages: {len(messages)}")

    min_length = min(len(dates), len(times), len(periods), len(senders), len(messages))
    dates = dates[:min_length]
    times = times[:min_length]
    periods = periods[:min_length]
    senders = senders[:min_length]
    messages = messages[:min_length]
    # Create the DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Time': times,
        'Period': periods,
        'Sender': senders,
        'Message': messages
    })
    df["Message"] = df["Message"].astype(str)
    df["Sender"] = df["Sender"].astype(str)

    df=df[1:]
    df['Date']=pd.to_datetime(df['Date'], format='%d/%m/%Y',errors='coerce')
    df['Date'] = df['Date'].fillna(pd.to_datetime(df['Date'], format='%d/%m/%y', errors='coerce'))
    df['year']=df['Date'].dt.year
    df['month']=df['Date'].dt.month_name()
    df['date'] = df['Date'].dt.day
     # Remove any accidental "24-hour" strings
    df['Time'] = df['Time'].str.replace("24-hour", "", regex=True).str.strip()

    # Convert time format (handling both 12-hour and 24-hour)
    df['time'] = pd.to_datetime(df['Time'], format='%I:%M %p', errors='coerce').combine_first(
    pd.to_datetime(df['Time'], format='%H:%M', errors='coerce')
    )

 
    df['hour']=df['time'].dt.hour
    df['min']=df['time'].dt.minute
    df['time']=df['time'].dt.time
    df['Day_name']=df['Date'].dt.day_name()
    return df
