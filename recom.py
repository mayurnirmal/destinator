from flask import Flask, render_template, request
import pandas as pd
import re
import datetime

app = Flask(__name__)

# Load the Excel dataset
data = pd.read_excel('Main Data/cleaned_file.xlsx')

# Function to extract months from 'Best time' column
def extract_months(time_str):
    if isinstance(time_str, str):  
        months = re.findall(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b', time_str)
        return months
    return time_str  

# Apply the function to extract months
data['Best time'] = data['Best time'].apply(extract_months)

# Get the current month
current_month = datetime.datetime.now().strftime('%B')
data['Current_Month'] = current_month

# Check if the current month is in the 'Best time' list
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

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/recommend', methods=['POST'])
# def recommend():
#     user_budget = int(request.form.get('budget'))
#     user_type = request.form.get('place_type')
#     user_state = request.form.get('state')

#     recommendations = recommend_places(user_budget, user_type, user_state, data)
    
#     return render_template('index.html', recommendations=recommendations.to_dict(orient='records'))

# if __name__ == '__main__':
#     app.run(debug=True)
@app.route('/')
def index():
    return render_template('recom.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    user_budget = int(request.form.get('budget'))
    user_type = request.form.get('place_type')
    user_state = request.form.get('state')

    recommendations = data[(data['Predicted_Tag'] == user_type) & (data['state'].str.lower() == user_state.lower())]
    
    return render_template('recom.html', recommendations=recommendations.to_dict(orient='records'))

@app.route('/cards')
def show_cards():
    states = sorted(data['state'].dropna().unique())  
    types = sorted(data['Predicted_Tag'].dropna().unique())  
    return render_template('cards_fil.html', places=data.to_dict(orient='records'), states=states, types=types)

if __name__ == '__main__':
    app.run(debug=True)
