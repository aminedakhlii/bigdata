from elasticsearch import Elasticsearch, helpers
import csv,sys,math,json,time,os,threading
from multiprocessing import Pool
import pathlib

PATH = '/home/data/online/split_ae.csv'
DIR = '/home/data/online/asma/chunks/'
es = Elasticsearch(host = "localhost", port = 9200)
csv.field_size_limit(sys.maxsize)

def ingestFile(file,i):
    with open(file, encoding="utf-8-sig") as fp:
        reader = csv.DictReader(fp)
        for success, info in helpers.parallel_bulk(es, actions=reader, index=i,thread_count=5,chunk_size=1000):
            pass

def ingest(index):
    start_time = time.time()
    files = os.listdir(DIR)
    shards = 0
    print(len(files))
    if len(files) > os.cpu_count():
        shards = os.cpu_count() - 1
    else:
        shards = len(files)//os.cpu_count()
        if shards < 1:
            shards = 1    
    es.indices.create(index=index, body={
        'settings' : {
            'index' : {
                  'number_of_shards': shards
             }
        }
    })
    procs = 0
    if len(files) > os.cpu_count():
        procs = os.cpu_count() - 1
    else:
         procs = len(files)
    pool = Pool(procs)
    for f in files:
        pool.apply_async(ingestFile, (DIR+f,index))
    pool.close()
    pool.join()
    es.indices.put_settings(index=index,
                            body= {"index" : {
                                    "max_result_window" : 100000
                             }})
    print("--- %s seconds ---" % (time.time() - start_time))
    return
