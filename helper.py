from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import re
import emoji



extract = URLExtract()

# ✅ Universal filter
def get_clean_messages(selected_user, df):
    # Always drop group notifications
    temp_df = df[df['users'] != 'group_notification']

    # Filter by user if needed
    if selected_user != 'overall':
        temp_df = temp_df[temp_df['users'] == selected_user]

    # Remove media omitted lines
    temp_df = temp_df[~temp_df['messages'].str.contains('omitted', case=False, na=False)]

    # Remove known system event phrases
    system_phrases = [
        "added", "removed", "changed the", "deleted this message",
        "joined from the community", "joined using this group's invite link",
        "created this group"
    ]
    temp_df = temp_df[~temp_df['messages'].str.lower().apply(lambda msg: any(phrase in msg for phrase in system_phrases))]

    return temp_df


def fetch_stats(selected_user, df):
    temp_df = get_clean_messages(selected_user, df)
    num_messages = temp_df.shape[0]

    words = []
    for message in temp_df['messages']:
        words.extend(message.split())

    # Media: check original df, not cleaned
    media_df = df[df['users'] != 'group_notification']
    if selected_user != 'overall':
        media_df = media_df[media_df['users'] == selected_user]
    num_media_messages = media_df[media_df['messages'].str.contains('omitted', case=False, na=False)].shape[0]

    # Links: check original df too
    links = []
    for message in media_df['messages']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


def most_busy_users(df):
    temp_df = df[df['users'] != 'group_notification']
    x = temp_df['users'].value_counts().head()
    percent_df = round((temp_df['users'].value_counts() / temp_df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'users': 'percent'})
    return x, percent_df


def create_wordcloud(selected_user, df):
    temp_df = get_clean_messages(selected_user, df)
    wc = WordCloud(width=800, height=400, min_font_size=10, background_color='white').generate(temp_df['messages'].str.cat(sep=" "))
    return wc


def most_common_words(selected_user, df):
    temp_df = get_clean_messages(selected_user, df)

    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read().splitlines()



    words = []
    for message in temp_df['messages']:
        for word in message.lower().split():
            word = re.sub(r'\W+', '', word)
            if word and word not in stop_words and not word.startswith('91') and not word.isdigit():
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df


def emoji_helper(selected_user, df):
    # ✅ Remove system notifications
    if selected_user == 'overall':
        temp_df = df[df['users'] != 'group_notification']
    else:
        temp_df = df[(df['users'] == selected_user) & (df['users'] != 'group_notification')]

    emojis = []
    for message in temp_df['messages']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))


    return emoji_df

def monthly_timeline(selected_user,df):

    if selected_user != 'overall':
        df = df[df['users'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['messages'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['messages'].reset_index()

    return daily_timeline

def activity_heatmap(selected_user,df):

    if selected_user != 'overall':
        df = df[df['users'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='messages', aggfunc='count').fillna(0)
    return user_heatmap










