from pathlib import Path
import requests
import yaml
import sys
import typer
from datetime import datetime


# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from scraping_utility.core.parsing.scraper import extract_web_content
from scraping_utility.core.utility.visualize import (
    create_dataframes,
    analyze_and_visualize,
    save_results
)

def rera_scrape():
    # Load headers and request payload from YAML file
    config_path = Path(__file__).parent / 'core' / 'utility' / 'constants.yml'
    with config_path.open('r') as f:
        config = yaml.safe_load(f)
        headers = config['headers']
        request_payload = config['request_payload']

    # Define the URL
    url = "https://rera.karnataka.gov.in/projectViewDetails"

    # Send the request
    response = requests.post(url, headers=headers, data=request_payload)

    # Check the response status code
    if response.status_code == 200:
        print("Request successful!")
        # Extract content
        extracted_content = extract_web_content(response.content, url)
        
        # Create DataFrames
        dfs = create_dataframes(extracted_content)
        
        # Generate visualizations
        plots = analyze_and_visualize(dfs)
        
        # Generate visualizations
        plots = analyze_and_visualize(dfs)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent / 'output' / timestamp
        save_results(dfs, plots, output_dir)
        
        # Print summary
        print("\nData Summary:")
        for name, df in dfs.items():
            print(f"\n{name.upper()} DataFrame:")
            print(f"Shape: {df.shape}")
            print("\nFirst few rows:")
            print(df.head())
            print("\nColumns:", df.columns.tolist())
            
        print(f"\nResults saved to: {output_dir}")
        
    else:
        print(f"Request failed with status code: {response.status_code}")

if __name__ == "__main__":
    typer.run(rera_scrape)