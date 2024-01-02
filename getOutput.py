from keras import layers as tfl
from genSeq import beamSearchGenerateSequenceBody, beamSearchGenerateSequenceHead
from encoder import Encoder
from formatText import formatInputText, formatOutputText
from decoder import transDecHead, transDecBody
import os

#Create instances for Encoders and Decoders
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

#Output generation function (to be used by VM)
def generateOutput(inputData):

    compressedEncs = []
    for i in range(0, len(inputData)):
        headline = formatInputText(inputData[i][4])
        body = formatInputText(inputData[i][0])
        encoding = encoder([headline, body])
        X = tfl.GlobalAveragePooling1D()(encoding)
        compressedEncs.append(X)

    startToken = tfl.GlobalAveragePooling1D()(compressedEncs)

    # Forward pass for headline generation
    headline_out = beamSearchGenerateSequenceHead(encoding, startToken)
    headline_final = formatOutputText(headline_out)

    # Forward pass for body generation using the same encoding
    body_out = beamSearchGenerateSequenceBody(encoding, startToken)
    body_final = formatOutputText(body_out)

    #Use for creating each object in dataset, plus add topic tagging used LDA
    return headline_final, body_final