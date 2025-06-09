import openai
import pandas as pd
from dotenv import load_dotenv
import os
from pathlib import Path
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure OpenAI
OPENAI_AVAILABLE = False
client = None
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
        # Test OpenAI connection with a simple request
        try:
            client.models.list()
            OPENAI_AVAILABLE = True
            print("OpenAI connection successful")
        except Exception as e:
            print(f"OpenAI connection test failed: {str(e)}")
    else:
        print("OpenAI API key not found in .env file")
except Exception as e:
    print(f"OpenAI setup failed: {str(e)}")
    OPENAI_AVAILABLE = False

def generate_basic_recommendations(city_data):
    """Generate fallback recommendations when OpenAI is unavailable"""
    try:
        services = city_data.get('services', {})
        score = city_data.get('Digital_Inclusion_Score', 0)
        
        # Convert service values to consistent format
        missing_services = [
            name for name, value in services.items() 
            if str(value).strip().upper() in ['NO', 'N', 'FALSE', '0', '']
        ]
        
        if score >= 6:
            status = "performing well"
        elif score >= 3:
            status = "making progress"
        else:
            status = "needing significant improvement"
            
        if missing_services:
            # Map internal names to user-friendly names
            service_names = {
                'tax_payment': 'Online Tax Payments',
                'traffic_violations': 'Traffic Violation Payments',
                'service_connections': 'Service Connection Requests',
                'certificates': 'Certificate/License Requests',
                'tenders': 'Tender Displays',
                'grievance': 'Grievance Management',
                'tickets': 'Ticket Purchases',
                'disclosure': 'Document Disclosure'
            }
            friendly_names = [service_names.get(s, s) for s in missing_services[:3]]
            rec = f"{city_data.get('City Name', 'The city')} is {status} in digital services (Score: {score}/8). " \
                  f"Priority implementations: {', '.join(friendly_names)}."
        else:
            rec = f"{city_data.get('City Name', 'The city')} has all digital services implemented (Score: {score}/8). " \
                  "Consider enhancing user experience and accessibility of existing services."
        
        return rec
        
    except Exception as e:
        return f"Recommendation: Focus on improving digital services infrastructure. (System Error: {str(e)})"

def generate_ai_recommendations(city_data):
    """Generate AI-powered recommendations using OpenAI"""
    if not OPENAI_AVAILABLE or not client:
        return generate_basic_recommendations(city_data)
    
    try:
        # Prepare service status text
        services_status = []
        service_mapping = {
            'tax_payment': 'Online Tax Payments',
            'traffic_violations': 'Online Traffic Violation Payments',
            'service_connections': 'Online Service Connection Requests',
            'certificates': 'Online Certificate/License Requests',
            'tenders': 'Online Tender Displays',
            'grievance': 'Online Grievance Management',
            'tickets': 'Online Ticket Purchases',
            'disclosure': 'Online Document Disclosure'
        }
        
        for key, name in service_mapping.items():
            status = city_data.get('services', {}).get(key, 'NO')
            services_status.append(f"- {name}: {'✅ Available' if str(status).upper() in ['YES', 'Y', 'TRUE', '1'] else '❌ Not Available'}")

        prompt = f"""
        Analyze the digital services status for {city_data['City Name']} ({city_data['Zone Name']}):

        Current Digital Inclusion Score: {city_data.get('Digital_Inclusion_Score', 0)}/8
        Services Status:
        {chr(10).join(services_status)}

        As a digital policy expert, provide specific recommendations:
        1. Identify the 2-3 most critical missing services to implement
        2. Suggest practical implementation steps for each
        3. Estimate potential impact on citizens
        4. Provide examples from similar cities
        5. Suggest quick wins and long-term strategies

        Format with clear sections and bullet points.
        Keep under 250 words.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in urban digital transformation and e-governance."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=350,
            timeout=10
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"AI Recommendation Error: {str(e)}")
        return generate_basic_recommendations(city_data)

def generate_recommendations(city_data):
    """Main recommendation generator with fallback logic"""
    if OPENAI_AVAILABLE:
        try:
            print("Attempting to generate AI recommendations...")
            ai_rec = generate_ai_recommendations(city_data)
            print("AI recommendations generated successfully")
            return ai_rec
        except Exception as e:
            print(f"AI generation failed, using basic recommendations: {str(e)}")
            return generate_basic_recommendations(city_data)
    else:
        print("OpenAI not available, using basic recommendations")
        return generate_basic_recommendations(city_data)

if __name__ == "__main__":
    # Test the recommendations
    data_path = Path(__file__).parent.parent / 'data' / 'processed' / 'clustered_data.csv'
    
    try:
        df = pd.read_csv(data_path)
        print("\n=== Testing Recommendations Engine ===\n")
        print(f"OpenAI Available: {OPENAI_AVAILABLE}")
        
        test_city = df.iloc[0]
        city_data = {
            'City Name': test_city['City Name'],
            'Zone Name': test_city['Zone Name'],
            'Digital_Inclusion_Score': test_city['Digital_Inclusion_Score'],
            'services': {
                'tax_payment': test_city.get('Online Payment of taxes (property / water) [Yes / No]', 'NO'),
                'traffic_violations': test_city.get('Online Payment against traffic violations (challans, fines, etc.) [Yes / No]', 'NO'),
                'service_connections': test_city.get('Online request for Service Connections (gas, water supply) [Yes / No]', 'NO'),
                'certificates': test_city.get('Online request for Certificates / Licenses (marriage, driving, birth & death certificates) [Yes / No]', 'NO'),
                'tenders': test_city.get('Online display of Tenders (for various works) across various departments/ utilities [Yes / No]', 'NO'),
                'grievance': test_city.get('Online Grievance management (tracking of complaints) [Yes / No]', 'NO'),
                'tickets': test_city.get('Online buying of Tickets and passes (e.g. public transport, cultural events) [Yes / No]', 'NO'),
                'disclosure': test_city.get('Online request of Disclosure of documents (e.g. budgets, plans, RTI requests) [Yes / No]', 'NO')
            }
        }
        
        print(f"\nTesting city: {city_data['City Name']}")
        print("Service Status:")
        for service, status in city_data['services'].items():
            print(f"- {service}: {status}")
        
        print("\nGenerating recommendations...")
        recommendation = generate_recommendations(city_data)
        
        print("\n=== FINAL RECOMMENDATION ===")
        print(recommendation)
        
    except Exception as e:
        print(f"\nError testing recommendations: {str(e)}")