import json
from collections import defaultdict
from math import log

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# Initialize stemmer and stopwords
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))


def preprocess_query(query):
    """
    Preprocess the user query to match processed data terms.
    :param query: Raw query string.
    :return: List of preprocessed query terms.
    """
    tokens = word_tokenize(query.lower())
    tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    return [stemmer.stem(token) for token in tokens]


def parse_query(query):
    """
    Parse the query into terms and operators (AND, OR, NOT).
    :param query: Raw query string.
    :return: List of tuples (operator, terms).
    """
    operators = {"AND", "OR", "NOT"}
    tokens = query.split()
    parsed_query = []
    current_operator = "AND"  # Default operator

    for token in tokens:
        if token in operators:
            current_operator = token
        else:
            preprocessed_term = preprocess_query(token)
            if preprocessed_term:
                parsed_query.append((current_operator, preprocessed_term))

    return parsed_query


def boolean_search(parsed_query, inverted_index, total_docs):
    """
    Perform a Boolean search operation based on the parsed query.
    :param parsed_query: List of (operator, terms).
    :param inverted_index: The inverted index dictionary.
    :param total_docs: Total number of documents.
    :return: Set of document IDs matching the query.
    """
    result_set = set(range(total_docs))  # Start with all documents
    for operator, terms in parsed_query:
        term_docs = set.union(*(set(inverted_index.get(term, [])) for term in terms))

        if operator == "AND":
            result_set &= term_docs
        elif operator == "OR":
            result_set |= term_docs
        elif operator == "NOT":
            result_set -= term_docs
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    return result_set


def create_ground_truth(processed_data, inverted_index, queries, ground_truth_file):
    """
    Create a ground truth file for specific queries.
    :param processed_data: The processed data.
    :param inverted_index: The inverted index dictionary.
    :param queries: A list of queries to process.
    :param ground_truth_file: Path to save the ground truth file.
    """
    total_docs = len(processed_data)
    ground_truth = []

    for query in queries:
        parsed_query = parse_query(query)
        matching_docs = boolean_search(parsed_query, inverted_index, total_docs)

        # Map document IDs to names
        matching_doc_names = [processed_data[doc_id]["name"] for doc_id in matching_docs]

        ground_truth.append({
            "query": query,
            "relevant_documents": matching_doc_names
        })

    # Save the ground truth to a file
    with open(ground_truth_file, "w") as f:
        json.dump(ground_truth, f, indent=2)

    print(f"Ground truth saved to {ground_truth_file}")


def main():
    # Load processed data and inverted index
    with open("processed_hotel_data.json", "r") as f:
        processed_data = json.load(f)

    with open("inverted_index.json", "r") as f:
        inverted_index = json.load(f)

    # List of queries to include in ground truth
    queries = [
        "Non-smoking hotel AND Dry cleaning",
        "Air conditioning OR Free breakfast",
        "Taxi service NOT Airport transportation",
        "Rooftop terrace AND Hot tub"
    ]

    # Create ground truth file
    ground_truth_file = "ground_truth.json"
    create_ground_truth(processed_data, inverted_index, queries, ground_truth_file)


if __name__ == "__main__":
    main()
