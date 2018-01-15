import tensorflow as tf
import numpy as np
import glob #this will be useful when reading reviews from file
import os
import tarfile
import string
import re

batch_size = 50
review_length = 40
glove_arr_dims = 50     
num_classes = 2         # Output (Label) Classes - pos, neg
hidden_size = 4
number_of_layers = 5    # Number of layers of stacked LSTM Cells

def load_data(glove_dict):
    """
    Take reviews from text files, vectorize them, and load them into a
    numpy array. Any preprocessing of the reviews should occur here. The first
    12500 reviews in the array should be the positive reviews, the 2nd 12500
    reviews should be the negative reviews.
    RETURN: numpy array of data with each row being a review in vectorized
    form"""

    pos = []
    neg = []

    with tarfile.open('reviews.tar.gz', "r") as tarball:
        for index, member in enumerate(tarball.getmembers()):
            file = tarball.extractfile(member)
            try:
                review = file.read()
                words = normalise_review(review)
                truncated_review = words[:review_length]
                translated_review = translate_review(truncated_review, glove_dict)
            except:
                continue

            # Pad out the array to the specified review_length
            if len(translated_review) < review_length:
                translated_review.extend([0] * (review_length - len(translated_review)))

            if 'pos' in str(member):
                pos.append( translated_review)
            elif 'neg' in str(member):
                neg.append( translated_review)

    tarball.close()
    data = np.asarray(pos + neg)
    return data


def normalise_review(review):
    """
    Takes a bytestream of characters from a tarball and processes them into
    words, removing all casing, punctuation, numbers.
    """
    review = review.lower().decode('UTF-8')
    review = review.replace("-"," ").replace("/", " ")
    translator = str.maketrans('', '', string.punctuation)      # Remove all punctuation - using a translation
    review = review.translate(translator)                       # table is the fastest option
    normalised_words = review.split()
    return normalised_words


def translate_review(review, glove_dict):
    """
    Takes in a review (array of strings) and replaces each element with its 
    associated value in the glove_dict dictionary. 
    """
    translated_review = []
    for index, word in enumerate(review):
        if word in glove_dict.keys():
            translated_review.append(glove_dict[word])
        else:
            translated_review.append(0)
    return translated_review


def load_glove_embeddings():
    """
    Load the glove embeddings into a array and a dictionary with words as
    keys and their associated index as the value. Assumes the glove
    embeddings are located in the same directory and named "glove.6B.50d.txt"
    RETURN: embeddings: the array containing word vectors
            word_index_dict: a dictionary matching a word in string form to
            its index in the embeddings array. e.g. {"apple": 119"}

    #if you are running on the CSE machines, you can load the glove data from here
    #data = open("/home/cs9444/public_html/17s2/hw2/glove.6B.50d.txt",'r',encoding="utf-8")
    """
    data = open("glove.6B.50d.txt",'r',encoding="utf-8")

    embeddings = [[0]*50]
    embeddings_index = 1        # Index of the current word's vector in the array
    word_index_dict = {'UNK':0}

    for line in data:
        words = line.split()
        # Remove casing
        word = words[0].lower()
        # Get rid of all punctuation
        translator = str.maketrans('', '', string.punctuation)      # Remove all punctuation - using a translation
        word = word.translate(translator)                       # table is the fastest option
        if word == "":
            continue
        values = [float(i) for i in words[1:]]
        embeddings.append(values)
        word_index_dict[word] = embeddings_index
        embeddings_index += 1

    embeddings = np.asarray(embeddings, dtype='float32')
    return embeddings, word_index_dict


def define_graph(glove_embeddings_arr):
    """
    Define the tensorflow graph that forms your model. You must use at least
    one recurrent unit. The input placeholder should be of size [batch_size,
    40] as we are restricting each review to it's first 40 words. The
    following naming convention must be used:
        Input placeholder: name="input_data"
        labels placeholder: name="labels"
        accuracy tensor: name="accuracy"
        loss tensor: name="loss"

    RETURN: input placeholder, labels placeholder, dropout_keep_prob, optimizer, 
    accuracy and loss tensors"""
    dropout_keep_prob = tf.placeholder_with_default(0.5, shape=())

    # Input data placeholder & Labels
    input_data = tf.placeholder(dtype=tf.int32, shape=[batch_size, review_length], name="input_data")
    labels = tf.placeholder(dtype=tf.int32, shape=[batch_size, num_classes], name="labels")

    # Get word vectors from glove embedding array
    data = tf.Variable(tf.zeros([batch_size, review_length, glove_arr_dims]), dtype=tf.float32)
    data = tf.nn.embedding_lookup(glove_embeddings_arr, input_data)

    # Stacked LSTM Cells with a final dynamic RNN layer
    def lstm_cell():
        lstmCell = tf.contrib.rnn.LSTMCell(hidden_size)
        return tf.contrib.rnn.DropoutWrapper(cell=lstmCell, output_keep_prob=dropout_keep_prob)

    stacked_lstm = tf.contrib.rnn.MultiRNNCell(
        [lstm_cell() for _ in range(number_of_layers)])

    output, state = tf.nn.dynamic_rnn(stacked_lstm, data, dtype=tf.float32)
    
    # Weights and bias
    weight = tf.Variable(tf.truncated_normal([hidden_size, num_classes]))
    bias = tf.Variable(tf.constant(0.1, shape=[num_classes]))

    # Make the predictions
    output = tf.transpose(output, [1, 0, 2])
    final_output = tf.gather(output, int(output.get_shape()[0]) - 1)
    prediction = (tf.matmul(final_output, weight) + bias)

    # Prediction accuracy
    correct_prediction = tf.equal(tf.argmax(prediction, 1), tf.argmax(labels, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32), name="accuracy")

    # Loss & optimizer
    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=labels), name="loss")
    optimizer = tf.train.AdamOptimizer().minimize(loss)

    return input_data, labels, dropout_keep_prob, optimizer, accuracy, loss
