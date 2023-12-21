import tensorflow as tf
import keras
from keras import layers as tfl
from genSeq import beamSearchGenerateSequenceBody, beamSearchGenerateSequenceHead, customLossBody, customLossHead
from encoder import Encoder
from formatText import formatInputText, formatOutputText
from decoder import transDecHead, transDecBody

optimizer = keras.optimizers.Adam()
encoder = Encoder()

headlineDecoder = transDecHead()
bodyDecoder = transDecBody()

# modify headlineIn and bodyIn after setting up Azure VM
# also replace the 120 with number of related articles

epochs = 100
batch_size = 32
num_batches = len(headlinesIn) // batch_size


for epoch in range(epochs):
    for batch_index in range(num_batches):
        start_index = batch_index * batch_size
        end_index = (batch_index + 1) * batch_size

        with tf.GradientTape(persistent=True) as tape:
            compressedEncs = []
            for _ in range(120):
                batch_headlines = formatInputText(headlinesIn[start_index:end_index])
                batch_bodys = formatInputText(bodysIn[start_index:end_index])
                encoding = encoder([batch_headlines, batch_bodys])
                compressedEncs.append(encoding)

            startToken = tfl.GlobalAveragePooling1D()(compressedEncs)

            # Forward pass for headline generation
            batch_headlines_out = beamSearchGenerateSequenceHead(encoding, startToken)
            headline_final = formatOutputText(batch_headlines_out)
            # Compute the headline loss
            head_loss = customLossHead(headlinesIn[start_index:end_index], headline_final)

            # Forward pass for body generation using the same encoding
            batch_bodys_out = beamSearchGenerateSequenceBody(encoding, startToken)
            body_final = formatOutputText(batch_bodys_out)
            # Compute the body loss
            body_loss = customLossBody(bodysIn[start_index:end_index], body_final)

        # Backward pass
        head_gradients = tape.gradient(head_loss, encoder.trainable_variables + headlineDecoder.trainable_variables)
        body_gradients = tape.gradient(body_loss, encoder.trainable_variables + bodyDecoder.trainable_variables)

        # Update the model parameters
        optimizer.apply_gradients(zip(head_gradients, encoder.trainable_variables + headlineDecoder.trainable_variables))
        optimizer.apply_gradients(zip(body_gradients, encoder.trainable_variables + bodyDecoder.trainable_variables))

        del tape  # Release the persistent tape

encoder.save_weights('encoderWeights.h5')
headlineDecoder.save_weights('headlineDecoderWeights.h5')
bodyDecoder.save_weights('bodyDecoderWeights.h5')