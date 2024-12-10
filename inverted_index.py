import json
from collections import defaultdict

def build_inverted_index(processed_data):
    """
    Build an inverted index from the processed data.
    :param processed_data: List of processed hotel data.
    :return: Inverted index as a dictionary.
    """
    inverted_index = defaultdict(list)  # Term-to-docID mapping

    for doc_id, hotel in enumerate(processed_data):
        # Combine terms from description and features
        terms = hotel.get("description", [])
        for feature_list in hotel.get("features", []):
            terms.extend(feature_list)

        # Add terms to the inverted index
        for term in set(terms):  # Use set to avoid duplicates
            inverted_index[term].append(doc_id)

    # Convert defaultdict to a regular dict
    return dict(inverted_index)

def save_inverted_index(index, output_file):
    """
    Save the inverted index to a JSON file.
    :param index: Inverted index dictionary.
    :param output_file: File path to save the index.
    """
    with open(output_file, "w") as f:
        json.dump(index, f, indent=2)

def main():
    # Input processed data file
    processed_data_file = "processed_hotel_data.json"
    output_index_file = "inverted_index.json"

    # Load the processed data
    with open(processed_data_file, "r") as f:
        processed_data = json.load(f)

    # Build the inverted index
    inverted_index = build_inverted_index(processed_data)

    # Save the inverted index
    save_inverted_index(inverted_index, output_index_file)
    print(f"Inverted index saved to {output_index_file}")

if __name__ == "__main__":
    main()
