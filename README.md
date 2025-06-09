# India's Digital Divide: A City-Level Inclusion Index with AI-Powered Policy Recommendations

## Overview
This project addresses India's growing digital divide by developing a city-level inclusion index using real-world data. It leverages machine learning to classify cities, predict underserved areas, and provide actionable policy suggestions tailored to each city's cluster.

## Features
- Digital Inclusion Index (0-8 scale)
- City clustering (Advanced/Emerging/Lagging)
- Predictive analytics for service gaps
- AI-generated policy recommendations
- Interactive web dashboard

## Installation
1. Clone this repository
2. Install requirements: `pip install -r requirements.txt`
3. Set up environment variables (create `.env` file from `.env.example`)
4. Run data processing: `python src/data_processing.py`
5. Run clustering: `python src/clustering.py`

## Usage
Start the web dashboard:
`python app/app.py`

Then visit http://localhost:5000 in your browser.

## Data
Add your city data in CSV format to `data/raw/` with the same structure as the sample file.

## Tech Stack
- Python (Pandas, Scikit-learn)
- Flask
- HTML/CSS/JS
- Jinja2 templating
- Pickle for model persistence

## License
MIT License - see LICENSE file for details