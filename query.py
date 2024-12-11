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


def calculate_tf_idf(term, doc_id, inverted_index, processed_data):
    """
    Calculate TF-IDF score for a term in a specific document.
    """
    term_frequency = processed_data[doc_id]["description"].count(term) + \
                     sum(feature.count(term) for feature in processed_data[doc_id]["features"])
    doc_count_containing_term = len(inverted_index.get(term, []))
    total_docs = len(processed_data)
    if term_frequency > 0:
        tf = 1 + log(term_frequency)
        idf = log(total_docs / (1 + doc_count_containing_term))
        return tf * idf
    return 0


def calculate_bm25(term, doc_id, inverted_index, processed_data, k1=1.5, b=0.75):
    """
    Calculate BM25 score for a term in a specific document.
    """
    term_frequency = processed_data[doc_id]["description"].count(term) + \
                     sum(feature.count(term) for feature in processed_data[doc_id]["features"])
    doc_count_containing_term = len(inverted_index.get(term, []))
    total_docs = len(processed_data)
    avg_doc_length = sum(len(doc["description"]) + sum(len(feature) for feature in doc["features"])
                         for doc in processed_data) / total_docs
    doc_length = len(processed_data[doc_id]["description"]) + sum(
        len(feature) for feature in processed_data[doc_id]["features"])

    idf = log((total_docs - doc_count_containing_term + 0.5) / (doc_count_containing_term + 0.5) + 1)
    tf_norm = (term_frequency * (k1 + 1)) / (term_frequency + k1 * (1 - b + b * (doc_length / avg_doc_length)))
    return idf * tf_norm


def rank_documents(query_terms, inverted_index, processed_data, doc_ids, ranking_function="TF-IDF"):
    """
    Rank documents based on the query using the specified ranking function.
    """
    scores = defaultdict(float)

    for term in query_terms:
        for doc_id in doc_ids:
            if ranking_function == "TF-IDF":
                scores[doc_id] += calculate_tf_idf(term, doc_id, inverted_index, processed_data)
            elif ranking_function == "BM25":
                scores[doc_id] += calculate_bm25(term, doc_id, inverted_index, processed_data)
            else:
                raise ValueError(f"Unsupported ranking function: {ranking_function}")

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def main():
    # Load processed data and inverted index
    with open("processed_hotel_data.json", "r") as f:
        processed_data = json.load(f)

    with open("inverted_index.json", "r") as f:
        inverted_index = json.load(f)

    total_docs = len(processed_data)

    # User query
    raw_query = "Taxi service And Entrance"
    print(f"Raw query: {raw_query}")

    # Parse and preprocess query
    parsed_query = parse_query(raw_query)
    processed_terms = [term for _, terms in parsed_query for term in terms]

    # Boolean Search (Optional: only for strict matching)
    matching_docs = boolean_search(parsed_query, inverted_index, total_docs)
    print("\nBoolean Search Results (100% match):")
    for doc_id in matching_docs:
        print(f"Document {doc_id}: {processed_data[doc_id]['name']}")

    # Rank documents using TF-IDF
    print("\nRanking with TF-IDF (all documents):")
    ranked_tf_idf = rank_documents(processed_terms, inverted_index, processed_data, range(total_docs),
                                   ranking_function="TF-IDF")
    for doc_id, score in ranked_tf_idf:
        print(f"Document {doc_id}: {processed_data[doc_id]['name']} (Score: {score})")

    # Rank documents using BM25
    print("\nRanking with BM25 (all documents):")
    ranked_bm25 = rank_documents(processed_terms, inverted_index, processed_data, range(total_docs),
                                 ranking_function="BM25")
    for doc_id, score in ranked_bm25:
        print(f"Document {doc_id}: {processed_data[doc_id]['name']} (Score: {score})")

if __name__ == "__main__":
    main()