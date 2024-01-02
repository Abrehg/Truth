import tensorflow as tf
from decoder import transDecBody, transDecHead
from formatText import eos_token
from keras import backend as K
import numpy as np
from collections import Counter

#Implement Beam Search in order to generate output sequence (For body)
def beamSearchGenerateSequenceBody(encoder_output, start_token):
    #General variables
    max_length = 200
    beam_size = 5
    sequences = [(start_token, 0.0)]

    #Generate output within max length
    for _ in range(max_length):
        all_candidates = []

        for seq, score in sequences:
            #Stop sequence if EOS token is detected
            if seq[-1] == eos_token:
                all_candidates.append((seq, score))
                continue

            #Generate possible output tokens and their corresponding probabilities
            sequence_tensor = tf.expand_dims(seq, axis=0)
            decoder_output = transDecBody(sequence_tensor, encoder_output)

            candidate_token_probs = tf.nn.softmax(decoder_output[:, -1, :])

            # Get top-k candidates based on probabilities
            top_k_indices = tf.argsort(candidate_token_probs, direction='DESCENDING')[:beam_size]

            for index in top_k_indices.numpy():
                #Generating and adding probabilities of each sequence
                candidate_token = index.numpy()
                candidate_prob = candidate_token_probs[0, candidate_token].numpy()
                candidate_seq = seq + [candidate_token]
                candidate_score = score + tf.math.log(candidate_prob)
                all_candidates.append((candidate_seq, candidate_score))

        #Output candidates in order of probability
        ordered = sorted(all_candidates, key=lambda tup: tup[1], reverse=True)
        sequences = ordered[:beam_size]

    # Select the sequence with the highest score
    best_sequence = sequences[0][0]
    
    # Remove the EOS token if present
    if best_sequence[-1] == eos_token:
        best_sequence = best_sequence[:-1]

    # Remove the start token
    return best_sequence[1:]

#Implement Beam Search in order to generate output sequence (For body)
def beamSearchGenerateSequenceHead(encoder_output, start_token):
    #General variables
    max_length = 25
    beam_size = 5
    sequences = [(start_token, 0.0)]

    #Generate output within max length
    for _ in range(max_length):
        all_candidates = []

        for seq, score in sequences:
            #Stop sequence if EOS token is detected
            if seq[-1] == eos_token:
                all_candidates.append((seq, score))
                continue

            #Generate possible output tokens and their corresponding probabilities
            sequence_tensor = tf.expand_dims(seq, axis=0)
            decoder_output = transDecHead(sequence_tensor, encoder_output)

            candidate_token_probs = tf.nn.softmax(decoder_output[:, -1, :])

            # Get top-k candidates based on probabilities
            top_k_indices = tf.argsort(candidate_token_probs, direction='DESCENDING')[:beam_size]

            for index in top_k_indices.numpy():
                #Generating and adding probabilities of each sequence
                candidate_token = index.numpy()
                candidate_prob = candidate_token_probs[0, candidate_token].numpy()
                candidate_seq = seq + [candidate_token]
                candidate_score = score + tf.math.log(candidate_prob)  # Use log probability to avoid vanishing gradients
                all_candidates.append((candidate_seq, candidate_score))

        #Output candidates in order of probability
        ordered = sorted(all_candidates, key=lambda tup: tup[1], reverse=True)
        sequences = ordered[:beam_size]

    # Select the sequence with the highest score
    best_sequence = sequences[0][0]
    
    # Remove the EOS token if present
    if best_sequence[-1] == eos_token:
        best_sequence = best_sequence[:-1]

    # Remove the start token
    return best_sequence[1:]

#Define BLEU score as loss 
def bleu_score(reference, candidate, weights=(0.25, 0.125, 0.25, 0.375)):
    #Find reference and candidate length
    candidate_len = len(candidate.split())
    reference_len = [len(ref.split()) for ref in reference]

    clipped_counts = [0] * 4
    candidate_ngrams = [candidate.split()[i:i + n] for n in range(1, 5) for i in range(len(candidate.split()) - n + 1)]

    #Find frequency values for each N-Gram sequence present in both candidate and reference
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

    #Combind brevity and geometric mean into final output
    bleu = brevity_penalty * geometric_mean
    return bleu

#Use BLEU score to create loss between 0 and 1
def bleu_loss(y_true, y_pred):
    total_bleu = 0.0

    for reference in y_true:
        total_bleu += bleu_score(reference, y_pred)

    avg_bleu = total_bleu / len(y_true)
    return 1 - avg_bleu

#Custom loss for Body using BLEU Score (Adds length penalty)
def customLossBody(y_true, y_pred):
    total_loss = 0
    max_length = 200

    for i in range(0, len(y_true)):
        bleuLoss = bleu_loss(y_true[i][0], y_pred)
    
        sequence_length = K.shape(y_pred)[1]
        length_penalty = K.maximum(0.0, sequence_length / max_length - 1.0)
    
        total_loss = bleuLoss + 0.25 * length_penalty
    
    return total_loss/len(y_true)

#Custom loss for Headline using BLEU Score (Adds length penalty)
def customLossHead(y_true, y_pred):
    max_length = 25
    total_loss = 0

    for i in range(0, len(y_true)):
        bleuLoss = bleu_loss(y_true[i][4], y_pred)
    
        sequence_length = K.shape(y_pred)[1]
        length_penalty = K.maximum(0.0, sequence_length / max_length - 1.0)
    
        total_loss = bleuLoss + 0.25 * length_penalty
    
    return total_loss/len(y_true)