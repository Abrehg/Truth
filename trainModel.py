import tensorflow as tf
import keras
from keras import layers as tfl
from genSeq import beamSearchGenerateSequence, custom_loss
from encoder import Encoder
from formatText import formatInputText, formatOutputText

optimizer = keras.optimizers.Adam()
encoder = Encoder()

epochs = 100
for epoch in range(epochs):
    with tf.GradientTape() as tape:
        # Forward pass
        # add multiple text functionality
        compressedEncs = []
        for _ in range(120):
            headline = formatInputText(headlineIn)
            body = formatInputText(bodyIn)
            encoding = encoder([headline, body])
            X = tfl.GlobalAveragePooling1D()(encoding)
            compressedEncs.append(X)
        startToken = tfl.Dense(100, 'relu')(compressedEncs)
        predictions = beamSearchGenerateSequence(encoding, startToken)
        output = formatOutputText(predictions)
        # Compute the loss
        loss = custom_loss(y_train, output)

    # Backward pass
    gradients = tape.gradient(loss, encoder.trainable_variables)
    # Update the model parameters
    optimizer.apply_gradients(zip(gradients, encoder.trainable_variables))