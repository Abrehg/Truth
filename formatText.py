import numpy as np
import sentencepiece as spm
import tensorflow as tf

#Load in local model for text to vec
sp = spm.SentencePieceProcessor()
sp.load('m.model')

#Convert Input string into vector of ints
def formatInputText(text):
    embeddings = sp.encode_as_ids(text)
    newEmbed = []
    for i in range(0, len(embeddings)):
        tempCell = embeddings[i]
        newEmbed.append([tempCell])
    embeddings = np.array(newEmbed)
    return embeddings

#Convert Input vector of ints into string
def formatOutputText(output):
    tempList = []
    for i in range(0, len(output)):
        tempList.append(int(output[i][0]))
    output = sp.decode_ids(tempList)
    return output

#Defining EOS token for future use
eos_token = sp.eos_id()
