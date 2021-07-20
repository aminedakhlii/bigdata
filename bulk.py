from elasticsearch import Elasticsearch, helpers
import csv,sys,math,json,time,os,threading
from multiprocessing import Pool

PATH = '/home/data/online/split_ae.csv'
DIR = '/home/data/online/asma/chunks/'
es = Elasticsearch(host = "localhost", port = 9200)
csv.field_size_limit(sys.maxsize)

def ingestFile(file,i):
    with open(file, encoding="utf-8-sig") as fp:
        reader = csv.DictReader(fp)
        print(reader.fieldnames)
        #helpers.bulk(es,reader,index='testbeta')
        for success, info in helpers.parallel_bulk(es, actions=reader, index=i,thread_count=5,chunk_size=1000):
            pass


def bulk(file=DIR):
    threads = []
    files = os.listdir(file)
    for f in files:
        threads.append(threading.Thread(target=ingestFile, args=(f,files.index(f))))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def ingest(index):
    start_time = time.time()
    files = os.listdir(DIR)
    pool = Pool(40)
    for f in files:
        pool.apply_async(ingestFile, (DIR+f,index))
    pool.close()
    pool.join()
    print("--- %s seconds ---" % (time.time() - start_time))
