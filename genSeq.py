import tensorflow as tf
from keras import layers as tfl
from decoder import transDecBody, transDecHead
from formatText import eos_token
from keras import backend as K
import numpy as np
from collections import Counter

def beamSearchGenerateSequenceBody(encoder_output, start_token):
    max_length = 200
    beam_size = 5
    sequences = [(start_token, 0.0)]  # Initialize with the start token and its initial score

    for _ in range(max_length):
        all_candidates = []

        for seq, score in sequences:
            if seq[-1] == eos_token:
                all_candidates.append((seq, score))
                continue

            sequence_tensor = tf.expand_dims(seq, axis=0)
            decoder_output = transDecBody(sequence_tensor, encoder_output)

            # Use probabilities directly from the last position in the sequence
            candidate_token_probs = tf.nn.softmax(decoder_output[:, -1, :])

            # Get top-k candidates based on probabilities
            top_k_indices = tf.argsort(candidate_token_probs, direction='DESCENDING')[:beam_size]

            for index in top_k_indices.numpy():
                candidate_token = index.numpy()
                candidate_prob = candidate_token_probs[0, candidate_token].numpy()
                candidate_seq = seq + [candidate_token]
                candidate_score = score + tf.math.log(candidate_prob)  # Use log probability to avoid vanishing gradients
                all_candidates.append((candidate_seq, candidate_score))

        ordered = sorted(all_candidates, key=lambda tup: tup[1], reverse=True)
        sequences = ordered[:beam_size]

    # Select the sequence with the highest score
    best_sequence = sequences[0][0]
    
    # Remove the <eos> token if present
    if best_sequence[-1] == eos_token:
        best_sequence = best_sequence[:-1]

    # Remove the start token
    return best_sequence[1:]

def beamSearchGenerateSequenceHead(encoder_output, start_token):
    max_length = 25
    beam_size = 5
    sequences = [(start_token, 0.0)]

    for _ in range(max_length):
        all_candidates = []

        for seq, score in sequences:
            if seq[-1] == eos_token:
                all_candidates.append((seq, score))
                continue

            sequence_tensor = tf.expand_dims(seq, axis=0)
            decoder_output = transDecHead(sequence_tensor, encoder_output)

            # Use probabilities directly from the last position in the sequence
            candidate_token_probs = tf.nn.softmax(decoder_output[:, -1, :])

            # Get top-k candidates based on probabilities
            top_k_indices = tf.argsort(candidate_token_probs, direction='DESCENDING')[:beam_size]

            for index in top_k_indices.numpy():
                candidate_token = index.numpy()
                candidate_prob = candidate_token_probs[0, candidate_token].numpy()
                candidate_seq = seq + [candidate_token]
                candidate_score = score + tf.math.log(candidate_prob)  # Use log probability to avoid vanishing gradients
                all_candidates.append((candidate_seq, candidate_score))

        ordered = sorted(all_candidates, key=lambda tup: tup[1], reverse=True)
        sequences = ordered[:beam_size]

    # Select the sequence with the highest score
    best_sequence = sequences[0][0]
    
    # Remove the <eos> token if present
    if best_sequence[-1] == eos_token:
        best_sequence = best_sequence[:-1]

    # Remove the start token
    return best_sequence[1:]

def bleu_score(reference, candidate, weights=(0.25, 0.25, 0.25, 0.25)):
    """
    Calculate BLEU score between a reference and a candidate.

    :param reference: List of reference strings.
    :param candidate: Candidate string to be evaluated.
    :param weights: Weights for 1-gram, 2-gram, 3-gram, and 4-gram, default is equal weights.
    :return: BLEU score.
    """
    candidate_len = len(candidate.split())
    reference_len = [len(ref.split()) for ref in reference]

    clipped_counts = [0] * 4
    candidate_ngrams = [candidate.split()[i:i + n] for n in range(1, 5) for i in range(len(candidate.split()) - n + 1)]

    for n in range(1, 5):
        candidate_ngram_counts = Counter(candidate_ngrams)
        clipped_ngram_counts = {}

        for ref in reference:
            reference_ngrams = [ref.split()[i:i + n] for i in range(len(ref.split()) - n + 1)]
            reference_ngram_counts = Counter(reference_ngrams)

            for ngram, count in candidate_ngram_counts.items():
                clipped_ngram_counts[ngram] = min(count, reference_ngram_counts.get(ngram, 0))

        clipped_counts[n - 1] = sum(clipped_ngram_counts.values())

    precision = [clipped / max(candidate_len, 1) for clipped in clipped_counts]
    geometric_mean = np.exp(np.sum(weights * np.log(precision)))

    brevity_penalty = min(1, np.exp(1 - (min(reference_len, key=lambda x: abs(x - candidate_len)) / candidate_len)))

    bleu = brevity_penalty * geometric_mean
    return bleu

def bleu_loss(y_true, y_pred):
    total_bleu = 0.0

    for reference in y_true:
        total_bleu += bleu_score(reference, y_pred)

    avg_bleu = total_bleu / len(y_true)
    return 1 - avg_bleu

def customLossBody(y_true, y_pred):
    bleuLoss = bleu_loss(y_true, y_pred)
    
    max_length = 200
    sequence_length = K.shape(y_pred)[1]
    length_penalty = K.maximum(0.0, sequence_length / max_length - 1.0)
    
    total_loss = bleuLoss + 0.25 * length_penalty
    
    return total_loss

def customLossHead(y_true, y_pred):
    bleuLoss = bleu_loss(y_true, y_pred)
    
    max_length = 25
    sequence_length = K.shape(y_pred)[1]
    length_penalty = K.maximum(0.0, sequence_length / max_length - 1.0)
    
    total_loss = bleuLoss + 0.25 * length_penalty
    
    return total_loss


"""
#text summarization training
dataset_name = 'multi_news'
(train_data, val_data, test_data), info = tfds.load(dataset_name, split=['train', 'validation', 'test'], shuffle_files=True, with_info=True)
print(info)

def process_dataset(data, key):
    vectors = [formatText(entry[key].numpy().decode("utf-8")) for entry in data]
    return vectors

print("processing started")

x_train = process_dataset(train_data, 'document')
y_train = process_dataset(train_data, 'summary')
print("train processed")

x_val = process_dataset(val_data, 'document')
y_val = process_dataset(val_data, 'summary')
print("val processed")

x_test = process_dataset(test_data, 'document')
y_test = process_dataset(test_data, 'summary')
print("test processed")

batch_size = 512
num_epochs = 10

#train dataset
combined_model.fit(x=x_train, y=y_train, batch_size=batch_size, epochs=num_epochs)
print("train fitted")

combined_model.fit(x=x_val, y=y_val, batch_size=batch_size, epochs=num_epochs)
print("val fitted")

combined_model.test_on_batch(x=x_test, y=y_test)
print("test set implemented")

#save desired weights
textEnc.save_weights('./text_encoder_weights.h5')
print("process finished")
"""