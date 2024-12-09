from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def create_dataframes(extracted_content):
    """
    Convert extracted content into structured pandas DataFrames
    """
    dfs = {}
    
    # Main text content DataFrame
    if extracted_content['visible_text']:
        dfs['text_content'] = pd.DataFrame({
            'content': extracted_content['visible_text'],
            'length': [len(text) for text in extracted_content['visible_text']],
            'word_count': [len(text.split()) for text in extracted_content['visible_text']],
            'type': 'visible_text'
        })
    
    # JavaScript content DataFrame
    if extracted_content['js_content']:
        js_df = pd.DataFrame({
            'content': extracted_content['js_content'],
            'length': [len(text) for text in extracted_content['js_content']],
            'word_count': [len(text.split()) for text in extracted_content['js_content']],
            'type': 'javascript'
        })
        if 'text_content' in dfs:
            dfs['text_content'] = pd.concat([dfs['text_content'], js_df], ignore_index=True)
        else:
            dfs['text_content'] = js_df
    
    # Links DataFrame
    if extracted_content['links']:
        dfs['links'] = pd.DataFrame(extracted_content['links'])
    
    # Metadata DataFrame
    metadata = extracted_content['metadata']
    dfs['metadata'] = pd.DataFrame([{
        'title': metadata['title'],
        'description': metadata['description'],
        'keyword_count': len(metadata['keywords']),
        'keywords': ', '.join(metadata['keywords'])
    }])
    
    # Structured Data DataFrame (if present)
    if extracted_content['structured_data']:
        structured_data_rows = []
        for data in extracted_content['structured_data']:
            if isinstance(data, dict):
                row = {
                    'type': data.get('@type', 'Unknown'),
                    'content': str(data)
                }
                structured_data_rows.append(row)
        if structured_data_rows:
            dfs['structured_data'] = pd.DataFrame(structured_data_rows)
    
    return dfs

def analyze_and_visualize(dfs):
    """
    Create visualizations of the scraped data
    """
    plots = {}
    
    if 'text_content' in dfs and not dfs['text_content'].empty:
        # Content Length Distribution
        plt.figure(figsize=(10, 6))
        sns.histplot(data=dfs['text_content'], x='length', hue='type', bins=30)
        plt.title('Distribution of Content Length')
        plt.xlabel('Content Length (characters)')
        plt.ylabel('Count')
        plots['length_distribution'] = plt.gcf()
        plt.close()
        
        # Word Count Distribution
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=dfs['text_content'], x='type', y='word_count')
        plt.title('Word Count Distribution by Content Type')
        plt.ylabel('Word Count')
        plots['word_count_distribution'] = plt.gcf()
        plt.close()
    
    if 'links' in dfs and not dfs['links'].empty:
        # Link Text Length Distribution
        plt.figure(figsize=(10, 6))
        sns.histplot(data=dfs['links'], x=dfs['links']['text'].str.len(), bins=20)
        plt.title('Distribution of Link Text Length')
        plt.xlabel('Link Text Length (characters)')
        plt.ylabel('Count')
        plots['link_length_distribution'] = plt.gcf()
        plt.close()
    
    return plots

def save_results(dfs, plots, output_dir):
    """
    Save DataFrames and plots to files
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save DataFrames to CSV
    for name, df in dfs.items():
        df.to_csv(output_path / f"{name}.csv", index=False)
    
    # Save plots
    for name, plot in plots.items():
        plot.savefig(output_path / f"{name}.png")
