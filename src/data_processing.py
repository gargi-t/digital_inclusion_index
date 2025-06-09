import pandas as pd
import numpy as np
from pathlib import Path

def load_data(filepath):
    """Load and clean the raw data"""
    df = pd.read_csv(filepath)
    df = df.replace('NA', np.nan)
    return df

def calculate_index(df):
    """Calculate digital inclusion index (0-8 scale)"""
    services = [
        'Online Payment of taxes (property / water) [Yes / No]',
        'Online Payment against traffic violations (challans, fines, etc.) [Yes / No]',
        'Online request for Service Connections (gas, water supply) [Yes / No]',
        'Online request for Certificates / Licenses (marriage, driving, birth & death certificates) [Yes / No]',
        'Online display of Tenders (for various works) across various departments/ utilities [Yes / No]',
        'Online Grievance management (tracking of complaints) [Yes / No]',
        'Online buying of Tickets and passes (e.g. public transport, cultural events) [Yes / No]',
        'Online request of Disclosure of documents (e.g. budgets, plans, RTI requests) [Yes / No]'
    ]
    
    df['Digital_Inclusion_Score'] = df[services].apply(lambda x: x.str.upper().eq('YES').sum(), axis=1)
    return df

if __name__ == "__main__":
    # Get absolute paths using Pathlib
    project_root = Path(__file__).parent.parent
    input_path = project_root / 'data' / 'raw' / 'Digital_availability_0.csv'
    output_path = project_root / 'data' / 'processed' / 'processed_data.csv'
    
    # Create processed directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Process data
    df = load_data(input_path)
    df = calculate_index(df)
    df.to_csv(output_path, index=False)
    print(f"Data successfully processed and saved to {output_path}")