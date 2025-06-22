import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")

st.sidebar.title("WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    try:
        data = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        data = bytes_data.decode("utf-16")

    df = preprocessor.preprocessor(data)



    user_list = df['users'].unique().tolist()
    user_list.sort()
    user_list.insert(0, "overall")

    selected_user = st.sidebar.selectbox("Show analysis w.r.t", user_list)

    if st.sidebar.button("Show Analysis"):

        # --- Top KPIs ---
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # --- Timelines side by side ---
        timeline = helper.monthly_timeline(selected_user, df)
        daily_timeline = helper.daily_timeline(selected_user, df)  # assuming you have this helper

        timeline_col, daily_col = st.columns(2)

        with timeline_col:
            st.header("Monthly Timeline")
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['messages'], color='green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with daily_col:
            st.header("Daily Timeline")
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['messages'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # --- Heatmap + Busiest Users ---
        heatmap_col, busy_col = st.columns(2)

        with heatmap_col:
            st.header("Weekly Activity Map")
            user_heatmap = helper.activity_heatmap(selected_user, df)
            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)

        with busy_col:
            if selected_user == 'overall':
                st.header('Most Busy Users')
                x, new_df = helper.most_busy_users(df)
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
                st.dataframe(new_df)

        # --- Wordcloud + Most Common Words ---
        wordcloud_col, commonwords_col = st.columns(2)

        with wordcloud_col:
            st.header("Word Cloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis('off')
            st.pyplot(fig)

        with commonwords_col:
            st.header("Most Common Words")
            most_common_df = helper.most_common_words(selected_user, df)
            fig, ax = plt.subplots()
            ax.barh(most_common_df[0], most_common_df[1])
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # --- Emoji Analysis ---
        emoji_col1, emoji_col2 = st.columns(2)

        with emoji_col1:
            st.header("Emoji Analysis")
            emoji_df = helper.emoji_helper(selected_user, df)
            st.dataframe(emoji_df)

        with emoji_col2:
            if not emoji_df.empty:
                fig, ax = plt.subplots()
                ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
                st.pyplot(fig)
            else:
                st.write("No emojis found.")



















