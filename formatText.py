import numpy as np
import sentencepiece as spm
import tensorflow as tf

sp = spm.SentencePieceProcessor()
sp.load('m.model')

def formatInputText(text):
    embeddings = sp.encode_as_ids(text)
    newEmbed = []
    for i in range(0, len(embeddings)):
        tempCell = embeddings[i]
        newEmbed.append([tempCell])
    embeddings = np.array(newEmbed)
    return embeddings

def formatOutputText(output):
    tempList = []
    for i in range(0, len(output)):
        tempList.append(int(output[i][0]))
    output = sp.decode_ids(tempList)
    return output

#ids = formatInputText("This is a test!")
#out = formatOutputText(ids)
#print(out)
#print('eos=', sp.eos_id())