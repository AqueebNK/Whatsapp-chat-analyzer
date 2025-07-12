import re
import pandas as pd

def preprocess(data):
    # Updated pattern to also match narrow space before AM/PM
    pattern = r'\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}[\u202f\s][APMapm]{2}'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Clean messages and fix formatting
    messages = [msg.strip(" -\n") for msg in messages]

    # Clean dates: replace narrow no-break space with regular space
    clean_dates = [d.replace('\u202f', ' ') for d in dates]

    df = pd.DataFrame({'user_message': messages, 'message_date': clean_dates})

    # Parse datetime with correct format
    df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y, %I:%M %p')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user + message
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Add period column
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f"{hour}-00")
        elif hour == 0:
            period.append("00-1")
        else:
            period.append(f"{hour}-{hour + 1}")
    df['period'] = period

    return df
