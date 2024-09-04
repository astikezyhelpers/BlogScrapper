import json
from transformers import MT5ForConditionalGeneration, T5Tokenizer
from collections import Counter

# Initialize the mT5-small model and tokenizer
model_name = "google/mt5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = MT5ForConditionalGeneration.from_pretrained(model_name)

# Function to rephrase text
def rephrase_text(text):
    # Check if the input text is empty
    if not text.strip():
        return "No content to rephrase."
    
    # Prepare the input for the model
    prompt = f"paraphrase: {text}"
    inputs = tokenizer.encode(prompt, return_tensors="pt", max_length=10, truncation=False)
    
    # Generate output
    outputs = model.generate(inputs, max_length=512, num_beams=5, early_stopping=True)
    
    # Decode the output
    rephrased_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Check if the output is a placeholder
    if rephrased_text == "<extra_id_0>" or not rephrased_text.strip():
        return "Rephrasing failed. Please check the input."
    
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