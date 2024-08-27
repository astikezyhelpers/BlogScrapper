import requests
from bs4 import BeautifulSoup
import pandas as pd

query = "hindi to english learning blog -site:youtube.com -site:reddit.com -site:quora.com"
url = f"https://www.google.com/search?q={query}&tbs=qdr:y"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}

# Debug: Start scraping process
print(f"Sending request to: {url}")

response = requests.get(url, headers=headers)

# Debug: Check response status
print(f"Response Status Code: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'lxml')
    results = []
    for g in soup.find_all('div', class_='g'):
        link_tag = g.find('a')
        title_tag = g.find('h3')

        # Debug: Check if link and title tags are found
        if not link_tag or not title_tag:
            print("Link or title tag not found, skipping this result.")
            continue

        link = link_tag['href']
        title = title_tag.text
        
        # Check if the snippet exists
        snippet_element = g.find('span', class_='aCOpRe')
        snippet = snippet_element.text if snippet_element else 'No snippet available'

        # Exclude YouTube, Reddit, and Quora content
        if any(excluded in link for excluded in ["youtube.com", "reddit.com", "quora.com"]):
            print(f"Excluding result from: {link}")
            continue

        # Debug: Print the title, link, and snippet
        print(f"Found result - Title: {title}, Link: {link}, Snippet: {snippet}")

        # Add all results, don't filter by 'blog'
        results.append({'title': title, 'link': link, 'snippet': snippet})

    # Debug: Print the number of results found
    print(f"Total results found: {len(results)}")

    for result in results:
        print(f"Scraping content from: {result['link']}")
        response = requests.get(result['link'], headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve content from {result['link']} (Status Code: {response.status_code})")
            continue

        blog_soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract headings and paragraphs
        headings = [heading.text for heading in blog_soup.find_all(['h1', 'h2', 'h3'])]
        paragraphs = [p.text for p in blog_soup.find_all('p')]

        # Debug: Print number of headings and paragraphs found
        print(f"Headings found: {len(headings)}")
        print(f"Paragraphs found: {len(paragraphs)}")

        relevant_content = {
            "headings": headings,
            "paragraphs": paragraphs
        }
        
        result['relevant_content'] = relevant_content

    # Now save the content
    df = pd.DataFrame(results)
    df.to_json('filtered_hindi_to_english_learning_blogs.json', index=False)

    # Debug: Notify end of process
    print("Scraping and saving process completed.")
else:
    print(f"Failed to retrieve Google search results (Status Code: {response.status_code})")
