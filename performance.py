from sklearn.metrics import precision_score, recall_score, f1_score
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

def mean_average_precision_at_k(ground_truth, retrieved_docs, k=10):
    """
    Calculate Mean Average Precision at K (MAP@K).
    :param ground_truth: List of relevant documents.
    :param retrieved_docs: List of retrieved documents ranked by relevance.
    :param k: Number of top documents to consider.
    :return: MAP@K score.
    """
    relevant_count = 0
    score = 0.0

    for i, doc in enumerate(retrieved_docs[:k]):
        if doc in ground_truth:
            relevant_count += 1
            score += relevant_count / (i + 1)

    return score / min(len(ground_truth), k) if ground_truth else 0


def evaluate_metrics(ground_truth_file, processed_data, inverted_index):
    # Load ground truth
    with open(ground_truth_file, "r") as f:
        ground_truth = json.load(f)

    metrics_results = []
    k = 10  # Evaluate top 10 results

    for query, relevant_docs in ground_truth.items():
        # Parse and preprocess query
        parsed_query = parse_query(query)
        processed_terms = [term for _, terms in parsed_query for term in terms]

        # Rank documents using TF-IDF
        ranked_results = rank_documents(processed_terms, inverted_index, processed_data, range(len(processed_data)),
                                         ranking_function="TF-IDF")
        retrieved_docs = [processed_data[doc_id]["name"] for doc_id, _ in ranked_results][:k]

        # Align y_true and y_pred sizes
        y_true = [1 if doc in relevant_docs else 0 for doc in retrieved_docs]
        y_pred = [1] * len(retrieved_docs)  # Assumes all retrieved_docs are predicted as relevant

        # Calculate metrics
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        map_score = mean_average_precision_at_k(relevant_docs, retrieved_docs, k)

        metrics_results.append({
            "query": query,
            "precision@10": precision,
            "recall@10": recall,
            "f1_score@10": f1,
            "map@10": map_score
        })

    return metrics_results



def main():
    # Load processed data and inverted index
    with open("processed_hotel_data.json", "r") as f:
        processed_data = json.load(f)

    with open("inverted_index.json", "r") as f:
        inverted_index = json.load(f)

    # Evaluate metrics
    ground_truth_file = "ground_truth.json"
    metrics_results = evaluate_metrics(ground_truth_file, processed_data, inverted_index)

    # Print results
    print("\nEvaluation Metrics:")
    for result in metrics_results:
        print(f"Query: {result['query']}")
        print(f"Precision@10: {result['precision@10']:.4f}")
        print(f"Recall@10: {result['recall@10']:.4f}")
        print(f"F1 Score@10: {result['f1_score@10']:.4f}")
        print(f"MAP@10: {result['map@10']:.4f}")
        print("-" * 30)


if __name__ == "__main__":
    main()
