from collections import Counter
import numpy as np
import csv
from datetime import datetime

fullData = []

"""
for filename in os.listdir(csv_directory):
    if filename.endswith(".csv"):
        file_path = os.path.join(csv_directory, filename)
"""

def addCSVToData(filePath):
    with open(filePath, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        #content,link,provider,publish_date,title

        if fullData == []:
            # Process each row in the CSV file
            for row in csv_reader:
                # Customize this part based on your processing needs
                # For example, you can append the row to the master dataset
                obj = [row[0], row[1], row[2], row[3], row[5]]
                fullData.append([obj])
        
        else:
            for row in csv_reader:
                # Customize this part based on your processing needs
                # For example, you can append the row to the master dataset
                obj = [row[0], row[1], row[2], row[3], row[5]]
                for i in range(0, len(fullData)):
                    totScoreHead = 0
                    totScoreBody = 0
                    totScoreDate = 0
                    for j in range(0, len(fullData[i])):
                        totScoreBody += bleu_loss(obj[0], fullData[i][j][0])
                        totScoreHead += bleu_loss(obj[4], fullData[i][j][4])
                        date1 = datetime.strptime(fullData[i][j][3], "%Y-%m-%d %H:%M:%S")
                        date2 = datetime.strptime(obj[3], "%Y-%m-%d %H:%M:%S")
                        deltaTime = date1 - date2
                        deltaTime = deltaTime.total_seconds()/3600
                        totScoreDate += (deltaTime/6)
                    
                    totScoreBody = totScoreBody/len(fullData[i])
                    totScoreHead = totScoreHead/len(fullData[i])
                    totScoreDate = totScoreDate/len(fullData[i])

                    if(totScoreBody + totScoreDate + totScoreHead) <= 3:
                        fullData[i].append(obj)
                        break

#Define BLEU score as loss 
def bleu_score(reference, candidate, weights=(0.375, 0.25, 0.125, 0.25)):
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