import json
import requests
import time
from collections import Counter

# Replace this with your API key
API_KEY = "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"
API_URL = "https://api-inference.huggingface.co/models/Vamsi/T5_Paraphrase_Paws "

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# Function to rephrase text
def rephrase_text(text):
    payload = {
        "inputs": f"paraphrase: {text}",
    }

    while True:
        response = requests.post(API_URL, headers=headers, json=payload)
        response_json = response.json()
        
        # Print the full API response
        print("API Response:", response_json)
        
        # Check if the model is still loading
        if "error" in response_json and "currently loading" in response_json["error"]:
            print(f"Model is loading. Waiting for {response_json.get('estimated_time', 20)} seconds...")
            time.sleep(response_json.get('estimated_time', 20))
        else:
            try:
                # Extract generated text and remove the input text from it
                generated_text = response_json[0]["generated_text"]
                
                # Remove the prefix "paraphrase:" and the original text
                # This assumes the input text is concatenated in the output, so we split it and take the second part.
                if "paraphrase:" in generated_text:
                    generated_text = generated_text.replace(f"paraphrase: {text}", "").strip()
                return generated_text
            except KeyError:
                print("Error: 'generated_text' not found in the response.")
                return None

# Function to match keywords in the title
def match_keywords(title, keywords):
    title_words = title.lower().split()
    keyword_matches = Counter(title_words) & Counter(keywords)
    return sum(keyword_matches.values())

# Function to process the JSON and generate rephrased content
def process_json(input_file, output_file, keywords):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    best_match = None
    highest_match_count = 0

    # Find the object with the highest keyword match
    for item in data:
        match_count = match_keywords(item['title'], keywords)
        if match_count > highest_match_count:
            highest_match_count = match_count
            best_match = item

    if best_match:
        # Rephrase headings and paragraphs
        rephrased_headings = [rephrase_text(heading) for heading in best_match['relevant_content']['headings'] if heading.strip()]
        rephrased_paragraphs = [rephrase_text(paragraph) for paragraph in best_match['relevant_content']['paragraphs'] if paragraph.strip()]

        # Prepare the rephrased content
        rephrased_content = {
            "title": best_match["title"],
            "link": best_match["link"],
            "snippet": best_match["snippet"],
            "relevant_content": {
                "headings": rephrased_headings,
                "paragraphs": rephrased_paragraphs
            }
        }

        # Save the rephrased content to a new JSON file
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump([rephrased_content], file, ensure_ascii=False, indent=4)

        print(f"Rephrased content saved to {output_file}")
    else:
        print("No matching content found.")

def main():
    input_file = 'reformatted_hindi_to_english_learning_blogs.json'
    output_file = 'rephrased_output.json'
    keywords = ['english', 'learning', 'blog', 'hindi']

    process_json(input_file, output_file, keywords)

if __name__ == "__main__":
    main()