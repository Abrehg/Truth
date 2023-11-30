import sentencepiece as spm

txt_file_path = 'inputData.txt'

#add a processing stage to add lines to inputData.txt for preprocessing (ask chatGPT)

spm.SentencePieceTrainer.train('--input=inputData.txt --model_prefix=m --vocab_size=50000')
