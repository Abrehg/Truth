import tensorflow as tf
import keras
from keras import layers as tfl
from genSeq import beamSearchGenerateSequenceBody, beamSearchGenerateSequenceHead, customLossBody, customLossHead
from encoder import Encoder
from formatText import formatInputText, formatOutputText
from decoder import transDecHead, transDecBody
import os

#Input instances of Encoders, Decoders, and optimizer
optimizer = keras.optimizers.Adam()
encoder = Encoder()
headlineDecoder = transDecHead()
bodyDecoder = transDecBody()

#Load in weights from files (if they exist)
if os.path.exists('encoderWeights.h5'):
    encoder.load_weights('encoderWeights.h5')
if os.path.exists('headlineDecoderWeights.h5'):
    headlineDecoder.load_weights('headlineDecoderWeights.h5')
if os.path.exists('bodyDecoderWeights.h5'):
    bodyDecoder.load_weights('bodyDecoderWeights.h5')

# also replace the 120 with number of related articles

#content,link,provider,publish_date,title

inputData = [[]]

#General variables
epochs = 100
batch_size = 32
num_batches = len(inputData) // batch_size

# Training steps
for epoch in range(epochs):
    for batch_index in range(num_batches):
        start_index = batch_index * batch_size
        end_index = (batch_index + 1) * batch_size

        # Accumulate losses over the batch
        total_head_loss = 0.0
        total_body_loss = 0.0

        with tf.GradientTape(persistent=True) as tape:
            for i in range(start_index, end_index):
                # Process data row by row within the batch
                compressedEncs = []
                for j in range(0, len(inputData[i])):
                    headline = formatInputText(inputData[i][j][4])
                    body = formatInputText(inputData[i][j][0])
                    encoding = encoder([headline, body])
                    X = tfl.GlobalAveragePooling1D()(encoding)
                    compressedEncs.append(X)

                startToken = tfl.GlobalAveragePooling1D()(encoding)

                # Forward pass for headline generation
                headline_out = beamSearchGenerateSequenceHead(encoding, startToken)
                headline_final = formatOutputText(headline_out)
                # Compute the headline loss
                head_loss = customLossHead(inputData[i], headline_final)
                total_head_loss += head_loss

                # Forward pass for body generation using the same encoding
                body_out = beamSearchGenerateSequenceBody(encoding, startToken)
                body_final = formatOutputText(body_out)
                # Compute the body loss
                body_loss = customLossBody(inputData[i], body_final)
                total_body_loss += body_loss

                if(i == (len(inputData) - 1)):
                    break

        # Calculate mean loss over the batch
        mean_head_loss = total_head_loss / batch_size
        mean_body_loss = total_body_loss / batch_size

        # Backward pass
        head_gradients = tape.gradient(mean_head_loss, encoder.trainable_variables + headlineDecoder.trainable_variables)
        body_gradients = tape.gradient(mean_body_loss, encoder.trainable_variables + bodyDecoder.trainable_variables)

        # Update the model parameters after processing the entire batch
        optimizer.apply_gradients(zip(head_gradients, encoder.trainable_variables + headlineDecoder.trainable_variables))
        optimizer.apply_gradients(zip(body_gradients, encoder.trainable_variables + bodyDecoder.trainable_variables))

        del tape  # Release the persistent tape