from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd

app = Flask(__name__)

# Load the dataset
data = pd.read_excel('Main Data/cleaned_file.xlsx')

# @app.route('/')
# def index():
#     states = sorted(data['state'].dropna().unique())  # Unique states for dropdown
#     types = sorted(data['Predicted_Tag'].dropna().unique())  # Unique place types
#     return render_template('cards_fil.html', places=data.to_dict(orient='records'), states=states, types=types)

# @app.route('/filter', methods=['POST'])
# def filter_places():
#     filtered_data = data.copy()
    
#     selected_state = request.form.get('state')
#     selected_type = request.form.get('type')

#     if selected_state:
#         filtered_data = filtered_data[filtered_data['state'] == selected_state]
    
#     if selected_type:
#         filtered_data = filtered_data[filtered_data['Predicted_Tag'] == selected_type]
    
#     return jsonify(filtered_data.to_dict(orient='records'))

# if __name__ == '__main__':
#     app.run(debug=True)

@app.route('/cards')
def index():
    states = sorted(data['state'].dropna().unique())  
    types = sorted(data['Predicted_Tag'].dropna().unique())  
    return render_template('cards_fil.html', places=data.to_dict(orient='records'), states=states, types=types)

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

@app.route('/')
def go_to_search():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
