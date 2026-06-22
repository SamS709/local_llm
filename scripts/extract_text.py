#!/usr/bin/env python3

import os
import re
from pathlib import Path

import os

def extract_markdowns(directory, threshold=0):

    """
    Extract text and sources from all Markdown files in a directory and its subdirectories.
    
    Args:
        directory (str): Path to the directory containing Markdown files
        threshold (int): Minimum length of text to include (default: 0)
        
    Returns:
        list: A list of dictionaries with 'text' and 'source' keys
    """
    markdown_files = []
    results = []
    
    # Find all .md files recursively in the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Only process files where .md is the actual extension (not .pdf.md, .png.md, etc)
            if file.endswith('.md') and '.' not in file[:-3]:
                full_path = os.path.join(root, file)
                markdown_files.append(full_path)
    
    # Process each Markdown file
    for md_file in markdown_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Skip files that don't meet the threshold
            if len(content) < threshold:
                continue
                
            # Extract source from the first line if it's a heading
            source = os.path.basename(md_file).replace('.md', '')
            
            results.append({
                'text': content,
                'source': source
            })
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
            continue
    
    return results


def extract_rst(directory, threshold=0):
    """
    Extract text and sources from all RST files in a directory and its subdirectories.
    
    Args:
        directory (str): Path to the directory containing RST files
        threshold (int): Minimum length of text to include (default: 0)
        
    Returns:
        list: A list of dictionaries with 'text' and 'source' keys where 'source' is the filename
    """
    rst_files = []
    results = []
    
    # Find all .rst files recursively in the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.rst'):
                full_path = os.path.join(root, file)
                rst_files.append(full_path)
    
    # Process each RST file
    for rst_file in rst_files:
        try:
            with open(rst_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Skip files that don't meet the threshold
            if len(content) < threshold:
                continue
                
            # Use the filename (without extension) as the source
            source = os.path.basename(rst_file).replace('.rst', '')
            
            results.append({
                'text': content,
                'source': source
            })
        except Exception as e:
            print(f"Error reading {rst_file}: {e}")
            continue
    
    return results


# Example usage
if __name__ == "__main__":
    # This will process the current directory with a threshold of 10 characters
    directory = 'IsaacLab'
    threshold = 100
    rst_data = extract_rst(directory, threshold=threshold)
    print(f"Found {len(rst_data)} rst files with text length >= {threshold}")
    
    # for item in rst_data[:2]:  # Show first 3 results
    #     print(f"source: {item['source']}")
    #     print(f"Text preview: {item['text']}")
    #     print("-" * 50)


