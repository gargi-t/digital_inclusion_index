import pandas as pd
from sklearn.cluster import KMeans
import joblib
from pathlib import Path

def cluster_cities(data_path, n_clusters=3):
    """Cluster cities based on their digital services"""
    df = pd.read_csv(data_path)
    
    services = [
        col for col in df.columns 
        if '[Yes / No]' in col and df[col].notna().any()
    ]
    
    X = df[services].apply(lambda x: x.str.upper().eq('YES').astype(int))
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['Cluster'] = kmeans.fit_predict(X)
    df['Cluster_Label'] = df['Cluster'].map({
        0: 'Digitally Lagging', 
        1: 'Emerging', 
        2: 'Digitally Advanced'
    })
    
    return df, kmeans

if __name__ == "__main__":
    # Set up paths
    project_root = Path(__file__).parent.parent
    input_path = project_root / 'data' / 'processed' / 'processed_data.csv'
    output_path = project_root / 'data' / 'processed' / 'clustered_data.csv'
    model_path = project_root / 'models' / 'clustering_model.pkl'
    
    # Verify input file exists
    if not input_path.exists():
        raise FileNotFoundError(
            f"Processed data not found at {input_path}\n"
            "Please run data_processing.py first"
        )
    
    # Create models directory if needed
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Run clustering
    clustered_df, model = cluster_cities(input_path)
    
    # Save results
    clustered_df.to_csv(output_path, index=False)
    joblib.dump(model, model_path)
    
    print(f"Clustering completed. Results saved to:\n"
          f"- {output_path}\n"
          f"- {model_path}")