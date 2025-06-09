import os
import sys
from pathlib import Path
from flask import Flask, render_template, request
import pandas as pd

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Now import your modules
try:
    from src.recommendations import generate_recommendations
    from src.data_processing import load_data, calculate_index
except ImportError as e:
    print(f"ImportError: {e}")
    print("Current Python path:", sys.path)
    raise

app = Flask(__name__)

@app.route('/')
def dashboard():
    data_path = project_root / 'data' / 'processed' / 'clustered_data.csv'
    if not data_path.exists():
        return "Processed data not found. Please run data processing scripts first.", 400
    
    df = pd.read_csv(data_path)
    return render_template('index.html', cities=df.to_dict('records'))

@app.route('/policy_brief/<city>')
def policy_brief(city):
    """Generate policy brief for a specific city"""
    data_path = project_root / 'data' / 'processed' / 'clustered_data.csv'
    
    try:
        df = pd.read_csv(data_path)
        city_row = df[df['City Name'].str.strip().str.lower() == city.strip().lower()]
        
        if city_row.empty:
            return render_template('error.html', message=f"City '{city}' not found")
            
        city_data = {
            'City Name': city_row.iloc[0]['City Name'],
            'Zone Name': city_row.iloc[0]['Zone Name'],
            'Digital_Inclusion_Score': int(city_row.iloc[0]['Digital_Inclusion_Score']),
            'Cluster_Label': city_row.iloc[0].get('Cluster_Label', 'N/A'),
            'services': {
                'tax_payment': city_row.iloc[0].get('Online Payment of taxes (property / water) [Yes / No]', 'NO'),
                'traffic_violations': city_row.iloc[0].get('Online Payment against traffic violations (challans, fines, etc.) [Yes / No]', 'NO'),
                'service_connections': city_row.iloc[0].get('Online request for Service Connections (gas, water supply) [Yes / No]', 'NO'),
                'certificates': city_row.iloc[0].get('Online request for Certificates / Licenses (marriage, driving, birth & death certificates) [Yes / No]', 'NO'),
                'tenders': city_row.iloc[0].get('Online display of Tenders (for various works) across various departments/ utilities [Yes / No]', 'NO'),
                'grievance': city_row.iloc[0].get('Online Grievance management (tracking of complaints) [Yes / No]', 'NO'),
                'tickets': city_row.iloc[0].get('Online buying of Tickets and passes (e.g. public transport, cultural events) [Yes / No]', 'NO'),
                'disclosure': city_row.iloc[0].get('Online request of Disclosure of documents (e.g. budgets, plans, RTI requests) [Yes / No]', 'NO')
            }
        }
        
        recommendation = generate_recommendations(city_data)
        
    except Exception as e:
        city_data = {
            'City Name': city,
            'Digital_Inclusion_Score': 0,
            'Cluster_Label': 'Error'
        }
        recommendation = f"Error generating recommendations: {str(e)}"
    
    return render_template('policy_brief.html', 
                         city=city_data,
                         recommendation=recommendation)

if __name__ == '__main__':
    app.run(debug=True)