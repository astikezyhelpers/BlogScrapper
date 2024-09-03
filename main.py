import requests
from bs4 import BeautifulSoup
import pandas as pd
import unicodedata
import html
import re
import json

# Set the query and URL
query = "hindi to english learning blog -site:youtube.com -site:reddit.com -site:quora.com"
url = f"https://www.google.com/search?q={query}&tbs=qdr:y"

# Set the headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}

# Send the request
print(f"Sending request to: {url}")
response = requests.get(url, headers=headers)
print(f"Response Status Code: {response.status_code}")

# If the response is successful
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'lxml')
    results = []
    
    # Parse the search results
    for g in soup.find_all('div', class_='g'):
        link_tag = g.find('a')
        title_tag = g.find('h3')

        if not link_tag or not title_tag:
            print("Link or title tag not found, skipping this result.")
            continue

        link = link_tag['href']
        title = title_tag.text
        
        snippet_element = g.find('span', class_='aCOpRe')
        snippet = snippet_element.text if snippet_element else 'No snippet available'

        if any(excluded in link for excluded in ["youtube.com", "reddit.com", "quora.com"]):
            print(f"Excluding result from: {link}")
            continue

        # Clean the title and snippet
        title = html.unescape(title)
        title = unicodedata.normalize('NFKC', title).strip()

        snippet = html.unescape(snippet)
        snippet = unicodedata.normalize('NFKC', snippet).strip()

        snippet = re.sub(r'\s+', ' ', snippet)  # Normalize whitespace

        print(f"Found result - Title: {title}, Link: {link}, Snippet: {snippet}")

        results.append({'title': title, 'link': link, 'snippet': snippet})

    print(f"Total results found: {len(results)}")

    # Scrape content from each link
    for result in results:
        print(f"Scraping content from: {result['link']}")
        response = requests.get(result['link'], headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve content from {result['link']} (Status Code: {response.status_code})")
            continue

        blog_soup = BeautifulSoup(response.text, 'lxml')
        
        headings = [heading.text for heading in blog_soup.find_all(['h1', 'h2', 'h3'])]
        paragraphs = [p.text for p in blog_soup.find_all('p')]

        # Clean the headings and paragraphs
        headings = [re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', html.unescape(heading)).strip()) for heading in headings]
        paragraphs = [re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', html.unescape(p)).strip()) for p in paragraphs]

        print(f"Headings found: {len(headings)}")
        print(f"Paragraphs found: {len(paragraphs)}")

        relevant_content = {
            "headings": headings,
            "paragraphs": paragraphs
        }
        
        result['relevant_content'] = relevant_content

    # Reformat the results into the desired structure
    reformatted_results = []
    for result in results:
        reformatted_results.append({
            "title": result["title"],
            "link": result["link"],
            "snippet": result["snippet"],
            "relevant_content": result["relevant_content"]
        })

    # Save the content while preserving the correct encoding
    with open('reformatted_hindi_to_english_learning_blogs.json', 'w', encoding='utf-8') as file:
        json.dump(reformatted_results, file, ensure_ascii=False, indent=4)

    print("Scraping and saving process completed.")
else:
    print(f"Failed to retrieve Google search results (Status Code: {response.status_code})")
