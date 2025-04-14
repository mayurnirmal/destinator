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
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Assuming 'data' is your DataFrame containing place information
# Initialize TF-IDF Vectorizer (move this to your data preprocessing)
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(data['Description'].fillna(''))

# Content-based recommendation function (updated)
def content_based_recommendation(user_input, top_n_per_type=8):
    try:
        if not user_input or not str(user_input).strip():
            logger.warning("Empty user input for content-based recommendation")
            return pd.DataFrame(columns=data.columns)
            
        user_vector = tfidf.transform([user_input])
        similarity_scores = cosine_similarity(user_vector, tfidf_matrix)
        
        # Create a copy of the data to avoid SettingWithCopyWarning
        recommendations = data.copy()
        recommendations["Similarity"] = similarity_scores.flatten()
        
        # Get top recommendations and ensure we have the right columns
        top_recommendations = recommendations.nlargest(top_n_per_type, "Similarity")
        return top_recommendations.drop(columns=["Similarity"]).reset_index(drop=True)
        
    except Exception as e:
        logger.error(f"Error in content-based recommendation: {str(e)}")
        return pd.DataFrame(columns=data.columns)

# Collaborative filtering function (updated)
def collaborative_filtering(visited_places_names, top_n_per_type=8):
    try:
        if not visited_places_names:
            logger.warning("No visited places provided for collaborative filtering")
            return pd.DataFrame(columns=data.columns)
            
        # Filter visited places and get their tags
        visited_data = data[data["Place Name"].isin(visited_places_names)]
        if visited_data.empty:
            logger.warning(f"No matching places found for: {visited_places_names}")
            return pd.DataFrame(columns=data.columns)
            
        visited_tags = visited_data["Predicted_Tag"].unique()
        recommendations = pd.DataFrame()
        
        for tag in visited_tags:
            tag_recommendations = data[data["Predicted_Tag"] == tag].head(top_n_per_type)
            recommendations = pd.concat([recommendations, tag_recommendations])
            
        return recommendations.reset_index(drop=True)
        
    except Exception as e:
        logger.error(f"Error in collaborative filtering: {str(e)}")
        return pd.DataFrame(columns=data.columns)

# Hybrid recommendation function (updated)
def hybrid_recommendation(user_input=None, visited_places_names=None, total_recommendations=24):
    try:
        # Initialize empty dataframes for each recommendation type
        cb_recs = pd.DataFrame(columns=data.columns)
        cf_recs = pd.DataFrame(columns=data.columns)
        
        # Get content-based recommendations if user input is provided
        if user_input and str(user_input).strip():
            cb_recs = content_based_recommendation(user_input, top_n_per_type=total_recommendations)
            logger.info(f"Content-based recommendations found: {len(cb_recs)}")
        
        # Get collaborative filtering recommendations if visited places are provided
        if visited_places_names:
            # Normalize input (handle both string and list inputs)
            if isinstance(visited_places_names, str):
                visited_places_names = [visited_places_names]
                
            # Clean and deduplicate the input
            visited_places_names = [str(place).strip() for place in visited_places_names if str(place).strip()]
            visited_places_names = list(set(visited_places_names))
            
            if visited_places_names:
                cf_recs = collaborative_filtering(
                    visited_places_names,
                    top_n_per_type=max(1, total_recommendations//max(1, len(visited_places_names))))
                logger.info(f"Collaborative filtering recommendations found: {len(cf_recs)}")
        
        # Combine recommendations
        combined = pd.concat([cb_recs, cf_recs], ignore_index=True)
        
        # If we have both types, balance them
        if not cb_recs.empty and not cf_recs.empty:
            # Take weighted average based on number of recommendations from each
            cb_count = min(len(cb_recs), total_recommendations // 2)
            cf_count = min(len(cf_recs), total_recommendations - cb_count)
            
            cb_sample = cb_recs.head(cb_count)
            cf_sample = cf_recs.head(cf_count)
            combined = pd.concat([cb_sample, cf_sample], ignore_index=True)
        
        # Remove duplicates (prioritize content-based recommendations)
        combined = combined.drop_duplicates(subset=['Place ID'], keep='first')
        
        # Final selection
        final_recommendations = combined.head(total_recommendations)
        
        # If still empty, fall back to popular items
        if final_recommendations.empty:
            logger.warning("No recommendations found, falling back to popular items")
            final_recommendations = data.sample(min(len(data), total_recommendations))
            if 'Similarity' in final_recommendations.columns:
                final_recommendations = final_recommendations.drop(columns=['Similarity'])
        
        # Ensure we have all required columns
        required_columns = ['Place ID', 'Visit Link', 'Place Name', 'Image Link', 'Description',
                          'Package', 'Rating', 'Best time', 'city', 'state', 'Predicted_Tag']
        
        for col in required_columns:
            if col not in final_recommendations.columns and col in data.columns:
                final_recommendations[col] = None  # Fill missing columns with None
        
        return final_recommendations[required_columns].reset_index(drop=True)
        
    except Exception as e:
        logger.error(f"Error in hybrid recommendation: {str(e)}")
        # Fallback to returning popular items if error occurs
        return data.sample(min(len(data), total_recommendations))[required_columns].reset_index(drop=True)

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
    types = sorted(data['Predicted_Tag'].dropna().unique().tolist())
    return render_template('recom.html', types=types)

@app.route('/get_states_for_type', methods=['GET'])
def get_states_for_type():
    selected_type = request.args.get('type')
    if selected_type:
        filtered_states = data[data['Predicted_Tag'] == selected_type]['state'].dropna().unique().tolist()
        filtered_states.sort()
        return jsonify(filtered_states)
    return jsonify([])


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