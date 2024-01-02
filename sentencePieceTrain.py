import sentencepiece as spm

#add a processing stage to add lines to inputData.txt for preprocessing (ask chatGPT)

#Train actual text-vec conversion
spm.SentencePieceTrainer.train('--input=inputData.txt --model_prefix=m --vocab_size=50000')
