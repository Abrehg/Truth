from keras import layers as tfl
from genSeq import beamSearchGenerateSequenceBody, beamSearchGenerateSequenceHead
from encoder import Encoder
from formatText import formatInputText, formatOutputText
from decoder import transDecHead, transDecBody

encoder = Encoder()
headlineDecoder = transDecHead()
bodyDecoder = transDecBody()

encoder.load_weights('encoderWeights.h5')
headlineDecoder.load_weights('headlineDecoderWeights.h5')
bodyDecoder.load_weights('bodyDecoderWeights.h5')

#Wrap in function that can be called and generates output sequence for each set of articles passed in

compressedEncs = []
for _ in range(120):
    headline = formatInputText(headlineIn)
    body = formatInputText(bodyIn)
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