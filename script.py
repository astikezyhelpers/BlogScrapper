import requests
import time

# Replace this with your API key
API_KEY = "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"
# API_URL = "https://api-inference.huggingface.co/models/eugenesiow/bart-paraphrase"

API_URL = "https://api-inference.huggingface.co/models/ai4bharat/airavata"
headers = {
    "Authorization": f"Bearer {API_KEY}"
}

def paraphrase_with_huggingface(text):
    payload = {
        "inputs": f"paraphrase this hindi input: {text}",
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

# Example usage
text_to_paraphrase = "जल्दी भूरा लोमड़ी आलसी कुत्ते के ऊपर कूदता है।"
paraphrased_text = paraphrase_with_huggingface(text_to_paraphrase)
print("Paraphrased text:", paraphrased_text)
