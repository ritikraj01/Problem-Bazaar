import csv

filename = 'data/merged.csv'

lines = [] # list of documents
tags = [] # list of tags
with open(filename, 'r', encoding='utf-8') as f:
    csv_reader = csv.reader(f)
    # reading every document and appending it to lines
    for row in csv_reader:
        documentData = row[0] + " " + row[2].replace(",", " ")
        tagsData = row[2]
        lines.append(documentData)
        tags.append(tagsData)

def preprocess(document_text, separatingSymbol):
    # make everything lowercase and divide every document in tokens
    terms = [term.lower().strip() for term in document_text.strip().split(separatingSymbol)]
    # return a list having tokens for a document
    return terms

vocab = {} # (a dictionary)
documents = [] # (list of lists)
# read lines and ectract tokens from it and append along with the index
for index, line in enumerate(lines):
    tokens = preprocess(line, ' ')
    documents.append(tokens) # appends list of tokens to the documents list
    tokens = set(tokens) # creates set out of list of tokens
    # stores frequency (value) of particular token (key) from every document (line) in dictionary vocab
    for token in tokens:
        if token not in vocab:
            vocab[token] = 1
        else:
            vocab[token] += 1

tagsDocuments = [] # (list of lists)
# read lines and ectract tokens from it and append along with the index
for tag in tags:
    tokens = preprocess(tag, ',')
    tagsDocuments.append(tokens)

# sorts the vocab dictionary on the basis of values and stores back to vocab
vocab = dict(sorted(vocab.items(), key=lambda item: item[1], reverse=True))

def generate_inverted_index(documents):
    inverted_index = {} # dict to store indexes (values) of the documents where the particular token (key) exists
    for index, document in enumerate(documents):
        for token in document:
            if token not in inverted_index:
                inverted_index[token] = [index]
            else:
                inverted_index[token].append(index)
    return inverted_index

inverted_index = generate_inverted_index(documents)
tags_inverted_index = generate_inverted_index(tagsDocuments)

# save the vocab (only keys of vocab dictionary) in a text file
with open('processedData/vocab.txt', 'w', encoding='utf-8') as f:
    for key in vocab.keys():
        f.write("%s\n" % key)

# save the frequency (only values of vocab dictionary) of tokens in a text file
with open('processedData/frequencies.txt', 'w', encoding='utf-8') as f:
    for key in vocab.keys():
        f.write("%s\n" % vocab[key])

# save the documents in a text file
with open('processedData/documents.txt', 'w', encoding='utf-8') as f:
    for document in documents:
        f.write("%s\n" % ' '.join(document))

# save the inverted index in a text file
with open('processedData/inverted-index.txt', 'w', encoding='utf-8') as f:
    for key in inverted_index.keys():
        f.write("%s\n" % key)
        f.write("%s\n" % ' '.join([str(doc_id) for doc_id in inverted_index[key]]))

# save the inverted index of tags in a text file
with open('processedData/tags-inverted-index.txt', 'w', encoding='utf-8') as f:
    for key in tags_inverted_index.keys():
        f.write("%s\n" % key)
        f.write("%s\n" % ' '.join([str(doc_id) for doc_id in tags_inverted_index[key]]))