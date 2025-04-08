from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import re
import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load the dataset
data = pd.read_excel('Main Data/cleaned_file.xlsx')

# Combine features for TF-IDF
data["Features"] = (
    data["Predicted_Tag"] + " " + data["Package"].astype(str) + " " + data["Best time"]
)

# Initialize TF-IDF Vectorizer
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(data["Features"])

# Extract unique states and place types
states = sorted(data['state'].dropna().unique())
types = sorted(data['Predicted_Tag'].dropna().unique())

# Function to extract months from 'Best time' column
def extract_months(time_str):
    if isinstance(time_str, str):
        months = re.findall(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b', time_str)
        return months
    return time_str

data['Best time'] = data['Best time'].apply(extract_months)
current_month = datetime.datetime.now().strftime('%B')
data['Current_Month'] = current_month
data['Is_Best_Time'] = data['Best time'].apply(lambda x: current_month in x if isinstance(x, list) else False)

# Function to recommend places based on user input
def recommend_places(user_budget, user_type, user_state, data):
    filtered_df = data[(data['Predicted_Tag'] == user_type) & (data['state'].str.lower() == user_state.lower())]
    
    budget_min = user_budget * 0.75
    budget_max = user_budget * 1.25
    budget_filtered_df = filtered_df[(filtered_df['Package'] >= budget_min) & (filtered_df['Package'] <= budget_max)]
    
    if budget_filtered_df.empty:
        budget_filtered_df = filtered_df
    
    recommended_places = budget_filtered_df.sort_values(by=['Rating', 'Is_Best_Time'], ascending=[False, False])
    
    return recommended_places.head(6)

# Content-based recommendation function
def content_based_recommendation(user_input, top_n_per_type=8):
    user_vector = tfidf.transform([user_input])
    similarity_scores = cosine_similarity(user_vector, tfidf_matrix)
    data["Similarity"] = similarity_scores.flatten()
    filtered_data = data[data["Predicted_Tag"].str.lower() == user_input.lower()]
    recommendations = filtered_data.nlargest(top_n_per_type, "Similarity")
    return recommendations.drop(columns=["Similarity"])

# Collaborative filtering function
def collaborative_filtering(visited_places_names, top_n_per_type=8):
    visited_data = data[data["Place Name"].isin(visited_places_names)]
    visited_tags = visited_data["Predicted_Tag"].unique()
    recommendations = pd.DataFrame()
    for tag in visited_tags:
        tag_recommendations = data[data["Predicted_Tag"] == tag].head(top_n_per_type)
        recommendations = pd.concat([recommendations, tag_recommendations])
    return recommendations.head(top_n_per_type * len(visited_tags))

# Hybrid recommendation function
def hybrid_recommendation(user_input=None, visited_places_names=None, total_recommendations=24):
    recommendations = pd.DataFrame(columns=data.columns)
    
    if visited_places_names:
        # Ensure visited_places_names is a list of strings
        if isinstance(visited_places_names, list):
            visited_places_names = [place.strip() for place in visited_places_names if place.strip()]
        
        # Filter out empty strings and ensure uniqueness
        visited_places_names = list(set(visited_places_names))
        
        # Get recommendations based on visited places
        recommendations = collaborative_filtering(visited_places_names, top_n_per_type=total_recommendations // len(visited_places_names))
    
    if user_input:
        # Get recommendations based on user input
        user_recs = content_based_recommendation(user_input, top_n_per_type=total_recommendations)
        if isinstance(user_recs, pd.DataFrame):
            recommendations = pd.concat([recommendations, user_recs], ignore_index=True)
    
    # Ensure the final recommendations have the expected columns and drop duplicates
    expected_columns = ['Place ID', 'Visit Link', 'Place Name', 'Image Link', 'Description',
                        'Package', 'Rating', 'Best time', 'city', 'state', 'Predicted_Tag']
    
    # Drop duplicates based on 'Place ID' or any other unique identifier
    final_recommendations = recommendations[expected_columns].drop_duplicates(subset=['Place ID']).head(total_recommendations)
    
    return final_recommendations

# ✅ Home page (first page)
@app.route('/')
def home():
    return render_template('index1.html')

# ✅ Redirect to the recommendation page
@app.route('/start')
def start():
    return redirect(url_for('recom'))

# ✅ Recommendation input page
@app.route('/recom')
def recom():
    return render_template('recom.html')

# ✅ Handle recommendation logic and redirect to cards page
@app.route('/recommend', methods=['POST'])
def recommend():
    user_budget = int(request.form.get('budget'))
    user_type = request.form.get('place_type')
    user_state = request.form.get('state')

    recommendations = data[(data['Predicted_Tag'] == user_type) & (data['state'].str.lower() == user_state.lower())]
    
    return render_template('recom.html', recommendations=recommendations.to_dict(orient='records'))

# ✅ Display all tourist places (default card page)
@app.route('/tourist-places')
def tourist_places():
    return render_template('cards_fil.html', places=data.to_dict(orient='records'), states=states, types=types)

# ✅ Handle filtering via AJAX
@app.route('/filter', methods=['POST'])
def filter_places():
    filtered_data = data.copy()
    
    selected_state = request.form.get('state')
    selected_type = request.form.get('type')

    if selected_state:
        filtered_data = filtered_data[filtered_data['state'] == selected_state]
    
    if selected_type:
        filtered_data = filtered_data[filtered_data['Predicted_Tag'] == selected_type]
    
    return jsonify(filtered_data.to_dict(orient='records'))

# New route for hybrid recommendations
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the list of visited places from the form
        visited_places_names = request.form.getlist('visited_places_names')
        
        # Get the user input from the form
        user_input = request.form.get('user_input')
        
        # Call the hybrid_recommendation function
        recommendations = hybrid_recommendation(user_input=user_input, visited_places_names=visited_places_names)
        
        # Render the results template with the recommendations
        return render_template('results.html', recommendations=recommendations.to_dict('records'))
    
    # Render the index template for GET requests
    return render_template('index.html')

place_names = data['Place Name'].dropna().astype(str).tolist()
@app.route('/suggest')
def suggest():
    query = request.args.get('q', '').lower()
    matches = [name for name in place_names if query in name.lower()]
    return jsonify(matches[:10])  # Return top 10 suggestions


if __name__ == '__main__':
    app.run(debug=True)