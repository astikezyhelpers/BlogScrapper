# import pandas as pd
# from transformers import MT5ForConditionalGeneration, MT5Tokenizer

# # Load the scraped data
# input_file = 'reformatted_hindi_to_english_learning_blogs.json'
# df = pd.read_json(input_file)

# # Initialize the mT5 small model and tokenizer
# model_name = "google/mt5-small"
# tokenizer = MT5Tokenizer.from_pretrained(model_name)
# model = MT5ForConditionalGeneration.from_pretrained(model_name)

# def generate_content(input_text):
#     # Prepare the input for the model
#     input_ids = tokenizer.encode(input_text, return_tensors='pt', truncation=True, max_length=512)

#     # Generate output using the model
#     outputs = model.generate(input_ids, max_length=512, num_beams=5, early_stopping=True)

#     # Decode the output
#     decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)

#     return decoded_output

# # Process each relevant content item
# recreated_content = []
# for index, row in df.iterrows():
#     # Combine headings and paragraphs into a single input string
#     combined_content = " ".join(row['relevant_content']['headings'] + row['relevant_content']['paragraphs'])

#     # Generate new content based on the combined content
#     new_content = generate_content(combined_content)

#     # Store the new content in the list
#     recreated_content.append(new_content)

# # Create a new DataFrame to save the recreated content
# output_df = pd.DataFrame({
#     'title': df['title'],
#     'link': df['link'],
#     'recreated_content': recreated_content
# })

# # Save the new content to a JSON file
# output_df.to_json('recreated_hindi_to_english_learning_blogs.json', index=False, force_ascii=False)

# print("Content generation completed and saved to 'recreated_hindi_to_english_learning_blogs.json'")



import json
from transformers import MT5ForConditionalGeneration, T5Tokenizer
from collections import Counter

# Initialize the mT5-mini model and tokenizer
model_name = "google/mt5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = MT5ForConditionalGeneration.from_pretrained(model_name)

# Function to rephrase text
def rephrase_text(text):
    inputs = tokenizer.encode("paraphrase: " + text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs, max_length=512, num_beams=4, early_stopping=True)
    rephrased_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return rephrased_text

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
        rephrased_headings = [rephrase_text(heading) for heading in best_match['relevant_content']['headings']]
        rephrased_paragraphs = [rephrase_text(paragraph) for paragraph in best_match['relevant_content']['paragraphs']]

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
