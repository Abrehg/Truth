import tensorflow as tf
from keras import layers as tfl
import keras

#positional encoding function
def positional_encoding(inputs):
    seq_len, d_model = tf.shape(inputs)[1], inputs.shape[-1]
    position = tf.range(start=0, limit=seq_len, delta=1, dtype=tf.float32)
    position = tf.expand_dims(position, axis=0)
    div_term = tf.pow(10000.0, 2 * tf.range(d_model // 2, dtype=tf.float32) / d_model)
    div_term = tf.expand_dims(div_term, axis=0)
    angles = position / div_term

    angle_rads = tf.concat([tf.sin(angles), tf.cos(angles)], axis=-1)
    angle_rads = tf.expand_dims(angle_rads, axis=0)
    return angle_rads

#Single decoder layer for input headline (typical layer used for chat GPT, BERT, and more)
def transDecHead(inputs, enc_output):
    pos_encodings = positional_encoding(inputs)
    vec = tf.add(inputs, pos_encodings)
    X = tfl.MultiHeadAttention(num_heads=16, key_dim=100, dropout=0.3)(vec, vec)
    add1 = tf.add(X, vec)
    norm1 = tfl.LayerNormalization()(add1)
    enc = tfl.MultiHeadAttention(num_heads=16, key_dim=100, dropout=0.3)(enc_output, enc_output, norm1)
    add2 = tf.add(enc, norm1)
    norm2 = tfl.LayerNormalization()(add2)
    ffn1 = tfl.Dense(512, activation='relu')(norm2)
    ffn2 = tfl.Dense(100, activation='relu')(ffn1)
    add3 = tf.add(ffn2, norm2)
    norm3 = tfl.LayerNormalization()(add3)
    outputs = tfl.Dense(50, 'linear')(norm3)
    outputs = tfl.Dense(1, 'linear')(norm3)
    model = keras.Model(inputs=[inputs, enc_output], outputs=outputs)
    return model

#Single decoder layer for input body (typical layer used for chat GPT, BERT, and more)
def transDecBody(inputs, enc_output):
    pos_encodings = positional_encoding(inputs)
    vec = tf.add(inputs, pos_encodings)
    X = tfl.MultiHeadAttention(num_heads=16, key_dim=100, dropout=0.3)(vec, vec)
    add1 = tf.add(X, vec)
    norm1 = tfl.LayerNormalization()(add1)
    enc = tfl.MultiHeadAttention(num_heads=16, key_dim=100, dropout=0.3)(enc_output, enc_output, norm1)
    add2 = tf.add(enc, norm1)
    norm2 = tfl.LayerNormalization()(add2)
    ffn1 = tfl.Dense(512, activation='relu')(norm2)
    ffn2 = tfl.Dense(100, activation='relu')(ffn1)
    add3 = tf.add(ffn2, norm2)
    norm3 = tfl.LayerNormalization()(add3)
    outputs = tfl.Dense(50, 'linear')(norm3)
    outputs = tfl.Dense(1, 'linear')(norm3)
    model = keras.Model(inputs=[inputs, enc_output], outputs=outputs)
    return model