import math
import csv
from flask import Flask, render_template, request

app = Flask(__name__)

def renderProblemList(query_string, tags_query_list):
    try:
# creates a dictionary from 'vocab' file's tokens (keys) & from 'frequencies' file (values)
        def load_vocab():
            vocab = {}
            # opening files in read mode
            with open('processedData/vocab.txt', 'r', encoding='latin-1') as f:
                vocab_terms = f.readlines()
            with open('processedData/frequencies.txt', 'r', encoding='latin-1') as f:
                frequencies = f.readlines()

            # writing data from 'vocab' & 'frequencies' to vocab dictionary
            for (term, frequencies) in zip(vocab_terms, frequencies):
                vocab[term.strip()] = int(frequencies.strip())

            return vocab

        # loads whole documents file as list of lists in documents
        def load_documents():
            documents = []
            # opening documents file in read mode
            with open('processedData/documents.txt', 'r') as f:
                documents = f.readlines()
            # appending list of of tokens of a document to documents list (creating a list of lists)
            documents = [document.strip().split() for document in documents]
            return documents

        # loading inverted-index file as dictionary where token (key) and string of indexes (values)
        def load_inverted_index(fileName):
            inverted_index = {}
            # opening 'inverted-index' file in read mode
            with open(fileName, 'r') as f:
                inverted_index_terms = f.readlines()

            # separting token (key) and string of indexes as list of indexes (values)
            for row_num in range(0, len(inverted_index_terms), 2):
                term = inverted_index_terms[row_num].strip()
                documents = inverted_index_terms[row_num+1].strip().split()
                inverted_index[term] = documents

            return inverted_index

        # saving all reqired files as appropriate data-structure in these variables
        vocab_idf_values = load_vocab()
        documents = load_documents()
        inverted_index = load_inverted_index('processedData/inverted-index.txt')
        tags_inverted_index = load_inverted_index('processedData/tags-inverted-index.txt')

        # returns list of problems based on passed tags list
        def tagFilter(tags_query_list):
            tagsDocumentsList = None
            for index, tag in enumerate(tags_query_list):
                    if tag in tags_inverted_index:
                        if index == 0:
                            tagsDocumentsList = set(tags_inverted_index[tag])
                        else:
                            tagsDocumentsList &= set(tags_inverted_index[tag])
                    else:
                        tagsDocumentsList = []

            tagsDocumentsList = list(tagsDocumentsList) if tagsDocumentsList else []
            return tagsDocumentsList

        # function calculates tf value for every query term (token) which is passed to it
        def get_tf_dictionary(term, tags_query_list):
            tf_values = {}
            # calculations procceeds only if the query token already exists in inverted_index
            if term in inverted_index:
                for document in inverted_index[term]:
                    # frequecy of term is gettig calculated for every document in which it exists
                    if not tags_query_list:
                        if document not in tf_values:
                            tf_values[document] = 1
                        else:
                            tf_values[document] += 1
                    else:
                        if document in tags_query_list:
                            if document not in tf_values:
                                tf_values[document] = 1
                            else:
                                tf_values[document] += 1

            # tf values calculated for term in every document where it exists
            for document in tf_values:
                tf_values[document] /= len(documents[int(document)])

            return tf_values

        # returns idf value for every query term (token)
        def get_idf_value(term):
            return math.log(len(documents)/vocab_idf_values[term])

        # sorted order of found potential documents on the basis of tf-idf value
        def calculate_sorted_order_of_documents(query_terms, tags_query_list):
            potential_documents = {}

            for term in query_terms:
                if vocab_idf_values[term] == 0:
                    continue
                tf_values_by_document = get_tf_dictionary(term, tagFilter(tags_query_list))
                idf_value = get_idf_value(term)
                for document in tf_values_by_document:
                    if document not in potential_documents:
                        potential_documents[document] = tf_values_by_document[document] * idf_value
                    potential_documents[document] += tf_values_by_document[document] * idf_value

            # divide by the length of the query terms
            for document in potential_documents:
                potential_documents[document] /= len(query_terms)

            potential_documents = dict(
                sorted(potential_documents.items(), key=lambda item: item[1], reverse=True)) # it is a dictionary

            # as we will be needing indexes only so taking indexes
            potential_documents_list = []
            for document_index in potential_documents.keys():
                potential_documents_list.append(document_index)

            return potential_documents_list # returns list of problem index only
            # for document_index in potential_documents:
            #     print('Document: ', documents[int(document_index)], ' Score: ', potential_documents[document_index]) #------------------------

        query_terms = [term.lower() for term in query_string.strip().split()]

        return calculate_sorted_order_of_documents(query_terms, tags_query_list)
    except Exception as e:
        print(f"An error occurred while rendering the problem list: {str(e)}")
        return []


def get_problems(indices):
    try:
        results = []
        whole_list = []
        with open('data/merged.csv', 'r') as f:
            reader = csv.reader(f)
            whole_list = list(reader)
        for index in indices:
            results.append(whole_list[int(index)])
        return results
    except Exception as e:
        print(f"An error occurred while retrieving problems: {str(e)}")
        return []

@app.route('/', methods=['GET', 'POST'])

def index():
    if request.method == 'POST':
        search_query = request.form['search']
        index_list = renderProblemList(search_query, []) # at the place of empty array tags has to be passed
        results = get_problems(index_list)
        return render_template('index.html', results=results)
    else:
        results = []  # Initialize results as an empty list
        return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)