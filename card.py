from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# Load the Excel dataset
data = pd.read_excel('Main Data/cleaned_file.xlsx')

@app.route('/')
def index():
    # Convert DataFrame to a list of dictionaries
    places = data.to_dict(orient='records')
    
    return render_template('card.html', places=places)

if __name__ == '__main__':
    app.run(debug=True)
