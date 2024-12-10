import json
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# Initialize stemmer and stopwords
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    """Preprocess text: tokenize, remove stopwords, and stem words"""
    if text is None:
        return []
    tokens = word_tokenize(text.lower())  # Tokenize and convert to lowercase
    tokens = [re.sub(r'\W+', '', token) for token in tokens if token.isalpha()]  # Remove non-alphabetic characters
    tokens = [word for word in tokens if word not in stop_words]  # Remove stopwords
    tokens = [stemmer.stem(word) for word in tokens]  # Apply stemming
    return tokens

def preprocess_json(input_file, output_file):
    """Process hotel data and save the cleaned data to a new JSON file"""
    with open(input_file, 'r') as f:
        hotel_data = json.load(f)

    processed_data = []
    for hotel in hotel_data:
        basic_data = hotel.get("basic_data", {})
        description = hotel.get("description", "")
        features = hotel.get("features", [])

        # Preprocess description and features
        processed_description = preprocess_text(description)
        processed_features = [preprocess_text(feature) for feature in features]

        # Organize processed data
        processed_data.append({
            "name": basic_data.get("name"),
            "rating": basic_data.get("aggregateRating", {}).get("ratingValue"),
            "reviewCount": basic_data.get("aggregateRating", {}).get("reviewCount"),
            "address": basic_data.get("address", {}).get("streetAddress"),
            "country": basic_data.get("address", {}).get("addressCountry", {}).get("name"),
            "description": processed_description,
            "features": processed_features,
            "image": basic_data.get("image")
        })

    # Save the processed data to a new JSON file
    with open(output_file, 'w') as f:
        json.dump(processed_data, f, indent=2)

if __name__ == "__main__":
    # Input and output file paths
    input_json = "hotel_data.json"
    output_json = "processed_hotel_data.json"

    preprocess_json(input_json, output_json)
    print(f"Processed data saved to {output_json}")
