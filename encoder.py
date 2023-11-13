import tensorflow as tf
from tensorflow import keras as keras
from keras import layers as tfl

#Modify to process subject, sender, and body at the same time and then combine
#use GloVe for subject and body, then use ASCII characters for sender

def Encoder():
    NNLayers = 3
    units = 300

    def feedForwardNN(baseInput):
        X = baseInput
        for k in range(0, NNLayers):
            X = tfl.Dense(activation='relu', units=units)(X)
        return X

    #generating input tensors
    input_body = keras.Input(shape=(None, units))
    input_headline = keras.Input(shape = (None, units))

    #Process body
    body = add_positional_encodings(input_body)
    body = tfl.MultiHeadAttention(num_heads=16, key_dim=units, dropout=0.3)(body, body)

    #Process subject
    headline = add_positional_encodings(input_headline)
    headline = tfl.MultiHeadAttention(num_heads=16, key_dim=units, dropout=0.3)(headline, headline)

    #Combine all tensors
    combined = tf.matmul(body, headline, transpose_b=True)
    combined_features = tf.matmul(combined, body)
    input2 = tfl.LayerNormalization()(combined_features)

    #Rest of first encoder layer
    X = feedForwardNN(input2)
    X = tf.cast(X, dtype=tf.float32)
    input2 = tf.cast(input2, dtype=tf.float32)
    X = tf.add(X, input2)
    input = tfl.LayerNormalization()(X)

    #Encoder layer 2
    X = tfl.MultiHeadAttention(num_heads=16, key_dim=units, dropout=0.3)(input, input)
    X = tf.cast(X, dtype=tf.float32)
    input = tf.cast(input, dtype=tf.float32)
    X = tf.add(X, input)
    input2 = tfl.LayerNormalization()(X)
    X = feedForwardNN(input2)
    X = tf.cast(X, dtype=tf.float32)
    input2 = tf.cast(input2, dtype=tf.float32)
    X = tf.add(X, input2)
    output = tfl.LayerNormalization()(X)

    model = keras.Model(inputs=[input_headline, input_body], outputs=output)
    return model

def positional_encoding(seq_len, d_model):

    position = tf.range(seq_len, dtype=tf.float32)
    i = tf.range(d_model, dtype=tf.float32)
    
    angles = 1 / tf.pow(10000.0, (2 * (i // 2)) / tf.cast(d_model, dtype=tf.float32))
    angles = tf.reshape(angles, (1, -1))
    
    angles = tf.multiply(position[:, tf.newaxis], angles)
    
    angles = tf.concat([tf.sin(angles[:, 0::2]), tf.cos(angles[:, 1::2])], axis=-1)
    encodings = tf.expand_dims(angles, axis=0)

    return encodings

def add_positional_encodings(word_vectors):
    seq_length = tf.shape(word_vectors)[1]
    d_model = tf.shape(word_vectors)[2]
    positional_encodings = positional_encoding(seq_length, d_model)
    word_vectors_with_position = word_vectors + positional_encodings
    return word_vectors_with_position