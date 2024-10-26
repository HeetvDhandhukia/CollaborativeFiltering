import streamlit as st
import pandas as pd
import random

# Load the Bollywood movies dataset
movies_df = pd.read_csv("BollywoodMovieDetail.csv")

# Define allowed genres for the dropdown
allowed_genres = ["Action", "Romance", "Adventure", "Family", "Comedy", "Horror"]

# Extract only the allowed genres from the dataset
genre_options = sorted(
    {genre.strip() for genres in movies_df['genre'].dropna() for genre in genres.split('|')}
    .intersection(allowed_genres)
)

# Extract unique actors from the dataset
actor_options = sorted(
    set(
        actor.strip()
        for actors in movies_df['actors'].dropna()
        for actor in actors.split('|')
    )
)

# Function to recommend top-rated movies by genre and actor
def recommend_top_movies(df, genre, actor, n=5):
    filtered_movies = df[df['genre'].str.contains(genre, case=False, na=False)]
    if actor:
        filtered_movies = filtered_movies[filtered_movies['actors'].str.contains(actor, case=False, na=False)]
    sorted_movies = filtered_movies.sort_values(by='hitFlop', ascending=False)
    return sorted_movies[['title', 'hitFlop', 'actors']].head(n)

# Function to get a random top movie and actor highlight
def get_random_top_highlight(df):
    top_movies = df.sort_values(by='hitFlop', ascending=False).head(10)
    random_movie = top_movies.sample(1).iloc[0]
    lead_actor = random_movie['actors'].split('|')[0].strip()
    return random_movie['title'], lead_actor, random_movie['hitFlop']

# Streamlit UI configuration
st.set_page_config(
    page_title="Mood-Based Bollywood Movie Recommender",
    page_icon="🎥",
    layout="wide"
)

# Sidebar for inputs
st.sidebar.header("🎛 Filter Options")
selected_genre = st.sidebar.selectbox("Select a Genre:", genre_options)
selected_actor = st.sidebar.selectbox("Search by Actor (Optional):", [""] + actor_options)
num_recommendations = st.sidebar.slider("Number of Recommendations:", 1, 10, 5)

# Initial Top Movie and Actor Highlights (before button click)
if 'highlight' not in st.session_state:
    st.session_state['highlight'] = get_random_top_highlight(movies_df)

# Display Top Movie & Actor Highlights
st.markdown("### ⭐ Today's Movie & Actor Highlights")
col1, col2 = st.columns(2)
top_movie, top_actor, top_rating = st.session_state['highlight']
col1.metric("Top Movie", top_movie, f"Rating: {top_rating}")
col2.metric("Top Actor", top_actor)

# Fetch recommendations on button click
if st.button("🎉 Get Recommendations"):
    with st.spinner("Fetching the best movies for you..."):
        recommendations = recommend_top_movies(movies_df, selected_genre, selected_actor, num_recommendations)

    if not recommendations.empty:
        st.success(f"Here are the top {num_recommendations} movies!")
        
        # Update Top Movie & Actor Highlights after generating recommendations
        st.session_state['highlight'] = get_random_top_highlight(movies_df)

        # Display recommendations with expandable movie details
        for idx, row in recommendations.iterrows():
            with st.expander(f"📽️ {row['title']} (Rating: {row['hitFlop']})"):
                st.write(f"**Actors:** {row['actors']}")
    else:
        st.error(f"Sorry, no movies found matching your criteria.")

# Footer message
st.markdown("💡 *Tip: Try combining genres and actors for unique recommendations!*")
