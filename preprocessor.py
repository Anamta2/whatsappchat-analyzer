import re
import pandas as pd

def preprocessor(data):
    # Pattern 1: [date, time] sender: message
    pattern_msg = r'\[(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}:\d{2})\] (.*?): (.*)'

    # Pattern 2: [date, time] system notification (no colon)
    pattern_sys = r'\[(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}:\d{2})\] (.*)'

    messages = re.findall(pattern_msg, data)
    system_msgs = re.findall(pattern_sys, data)

    # Filter out system lines that already matched as messages
    system_msgs = [sys for sys in system_msgs if sys not in messages]

    # For messages: normal sender and message
    df1 = pd.DataFrame(messages, columns=['date', 'time', 'users', 'messages'])

    # For system notifications: mark user as 'group_notification'
    df2 = pd.DataFrame(system_msgs, columns=['date', 'time', 'messages'])
    df2['users'] = 'group_notification'
    df2 = df2[['date', 'time', 'users', 'messages']]

    # Combine both
    df = pd.concat([df1, df2])

    # Combine date & time
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'],
                                    format='%d/%m/%y %H:%M:%S',
                                    errors='coerce')

    df.drop(['date', 'time'], axis=1, inplace=True)
    df.rename(columns={'datetime': 'date'}, inplace=True)

    # Extract parts
    df['only_date']= df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num']= df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df


