import csv
import os
import openai
import loaddef qnainit():    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.api_base = os.getenv("OPENAI_ENDPOINT")
    openai.api_type = os.getenv("OPENAI_TYPE")
    openai.api_version = os.getenv("OPENAI_VERSION")    with open('./data/qna.csv', newline='\r\n') as srccsvfile:
        datareader = csv.reader(srccsvfile, delimiter=';')        with open('./embeddings/embeddings.csv', 'a', newline='\r\n') as dstcsvfile:
            tmpwriter = csv.writer(dstcsvfile, delimiter=';',
                                quotechar='', quoting=csv.QUOTE_NONE)            for row in datareader:
                question = row[0]
                answer = row[1]                response = openai.Embedding.create(
                    input=question,
                    engine=os.getenv("OPENAI_DEPLOYMENT")
                )
                embeddings = response['data'][0]['embedding']
                tmpwriter.writerow([question,answer,embeddings])
    return 'success'

