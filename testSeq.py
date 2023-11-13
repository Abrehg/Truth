import tensorflow as tf
from tensorflow import keras
from keras import layers as tfl

eos_token = tf.zeros((1, 300))

inputTens = tfl.Input([None, None, 300])

def transformer_decoder_layer(input_tensor):
    zeros = tf.zeros_like(input_tensor)
    out = tfl.Add()([input_tensor, zeros])
    return out

def beam_search_generate_sequence(input_tensor):
    max_length = 200
    sequence = [tf.ones((1,300))]

    for i in range(max_length):
        if sequence[-1] is eos_token:
            break
        decoder_output = transformer_decoder_layer(input_tensor[0][i])
        print(tf.shape(decoder_output))
        sequence.append(decoder_output)

    return tfl.Concatenate(axis=0)(sequence)

genSeq = beam_search_generate_sequence(inputTens)

testModel = keras.Model(inputs = inputTens, outputs = genSeq)
print(testModel.summary())

testInput = tf.ones((99,300))
testInput = tf.concat([testInput, eos_token], axis = 0)
testInput = tf.concat([testInput, tf.ones((100, 300))], axis = 0)
#testInput = tf.expand_dims(testInput, axis=0)

testOut = testModel.predict(testInput)

print(tf.shape(testOut))