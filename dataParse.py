from collections import Counter
import numpy as np
import csv
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, TIMESTAMP, JSON, Sequence, text
from sqlalchemy.orm import sessionmaker
import requests
import os

db_params = {
    'host': 'localhost',
    'port' : 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'Sur27776',
}

engine = create_engine(f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}/{db_params['database']}")

# Define a table
metadata = MetaData()

your_table = Table('newsData', metadata,
    Column('id', Integer, Sequence('myseq'), primary_key=True),
    Column('headline', String),
    Column('body', String),
    Column('timestamp', TIMESTAMP),
    Column('sources', JSON),
    Column('images', JSON)
)
"""
Session = sessionmaker(bind=engine)
session = Session()

select_query = your_table.select().order_by(your_table.c.timestamp.desc())
result = session.execute(select_query)
rows = result.fetchall()

for row in rows:
    #print(row)
    print(row[0])
    #print(row[1])
    #print(row[2])
    #print(row[3])
    #print(row[4])
    #data = row[4]
    #for i in range(len(row[4])):
    #    print(data[i]["provider"])
    #print(row[4][0]["link"])

# Commit the changes
session.commit()

# Close the session
session.close()
"""

#0 -> id
#1 -> headline
#2 -> body
#3 -> timestamp
#4 -> sources (acts like array of JSONs)
    #link, provider, title, body
#5 -> images (thumbnails)
    #resolution, path

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

dataDir = "/Users/adityaasuratkal/Downloads/Thumbnails"

def addToDatabase(title, link, content, provider, publish_date, image_urls):
    Session = sessionmaker(bind=engine)
    session = Session()
    
    #Develop new Source object (JSON Format)
    obj = {"link":link, "provider":provider, "title":title, "body":content}
    added = False

    #Search query for all rows in Database
    select_query = your_table.select().order_by(your_table.c.timestamp.desc())
    result = session.execute(select_query)
    rows = result.fetchall()

    for row in rows:
        #initialize data
        data = row[4]
        totScoreHead = 0
        totScoreBody = 0
        totScoreDate = 0

        #Find date score (difference in time by scale of 6 hours)
        date1 = row[3]
        date2 = datetime.strptime(publish_date, "%Y-%m-%d %H:%M:%S")
        deltaTime = date1 - date2
        deltaTime = deltaTime.total_seconds()/3600
        totScoreDate = (deltaTime/6)

        #Find average BLEU Score for all articles in sources cell
        for i in range(len(data)):
            totScoreBody += bleu_loss(content, data[i]["body"])
            totScoreHead += bleu_loss(title, data[i]["title"])
        totScoreBody = totScoreBody/len(data)
        totScoreHead = totScoreHead/len(data)

        #Add new sources if scores are below threshold
        if totScoreBody <= 0.5 and totScoreHead <= 0.5 and abs(totScoreDate) <= 1:
            #Append new object to sources and add update query
            data.append(obj)
            added = True
            update_query = (
                your_table.update()
                .where(your_table.c.id == row[0])
                .values(sources = data)
            )
            session.execute(update_query)
            if date1 > date2:
                #Update date if the new date is earlier than the previous date used
                update_query = (
                    your_table.update()
                    .where(your_table.c.id == row[0])
                    .values(timestamp = publish_date, images = data)
                )
                session.execute(update_query)
            if row[5] == [] or date1 > date2:
                img_data = downloadImgFromLinks(image_urls, dataDir + f"/{row[0]}")
                update_query = (
                    your_table.update()
                    .where(your_table.c.id == row[0])
                    .values(images = img_data)
                )
                session.execute(update_query)
            
            session.commit()
            break

    if not added:
        #If added flag not used, then add as a new entry in the database
        
        #Make directory for new image thumbnails and add new data
        current_value_query = text("SELECT last_value FROM myseq")
        with engine.connect() as connection:
            result = connection.execute(current_value_query)
            id = result.scalar()
        os.mkdir(dataDir + f"/{id}")
        data = downloadImgFromLinks(image_urls, dataDir + f"/{id}")

        #Create new entry in database (with or without img data)
        insert_query = your_table.insert().values(
            headline='', 
            body='',
            timestamp = publish_date,
            sources =[obj],
            images = data
        )
        session.execute(insert_query)
        session.commit()
    
    session.close()

def downloadImgFromLinks(img_links, folderPath):
    data = []
    for row in img_links:
        obj = row.split(" ")
        name = f"img_{obj[1]}.jpg"
        output = download_image(obj[0], folderPath, name)
        if output != False:
            data.append({"resolution" : obj[1], "path" : output})
    return data

def download_image(url, folder_path, filename):
    response = requests.get(url)
    
    if response.status_code == 200:
        file_path = os.path.join(folder_path, filename)
        
        with open(file_path, 'wb') as file:
            file.write(response.content)
        
        print(f"Image downloaded and saved at: {file_path}")
        return file_path
    else:
        print(f"Failed to download image from {url}")
    return False

"""
for filename in os.listdir(csv_directory):
    if filename.endswith(".csv"):
        file_path = os.path.join(csv_directory, filename)
"""

#Add new data from CSV filepath
def addCSVsOld(filePath):
    with open(filePath, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            addToDatabase(row["title"], row["link"], row["content"], row["provider"], row["publish_date"], [])

def addCSVs(filePath):
    with open(filePath, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            result_list = [item.strip() for item in row["image_urls"].split(',')]
            addToDatabase(row["title"], row["link"], row["content"], row["provider"], row["publish_date"], result_list)

addCSVs("/Users/adityaasuratkal/Downloads/GitHub/Truth/newsScrape/washPost4.csv")