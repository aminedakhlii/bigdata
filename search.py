import elasticfuncs as ef
from iteration_utilities import unique_everseen
from multiprocessing import Pool, Manager
import threading, math, os

es = ef.es 
manager = Manager()

def search(index,body):
    hits = []
    body = buildQuery(body)
    res = es.search(index=index,body=body,size=10000000,scroll='1m')
    for hit in res['hits']['hits']:
        hits.append(hit['_source'])
    hits = [i for n, i in enumerate(hits) if i not in hits[n + 1:]]
    return len(hits), hits

def indexSearch(index,body,override=True):
    global hitsFromSlice
    if override:
        hitsFromSlice = manager.list()
    if index == 'all':
        return globalSearch(body,1000)    
    slicedScroll(index,1000,os.cpu_count()-1,body)
    return len(hitsFromSlice) , hitsFromSlice        

def processHits(hits):
    final = [] 
    for hit in hits:
        final.append(hit['_source'])
    return final    

hitsFromSlice = manager.list()

def indexListAll(index,override=True):
    global hitsFromSlice
    if override:
        hitsFromSlice = manager.list()
    slicedScroll(index,1000,os.cpu_count() - 1)
    return len(hitsFromSlice), hitsFromSlice      

def slicedScroll(index,size,maxt,query=None):
    pool = Pool(maxt)
    for i in range(maxt):
        if query == None:
            pool.apply_async(sliceSearch, (index,i,maxt,size))
        else:
            pool.apply_async(sliceSearch, (index,i,maxt,size,query))    
    pool.close()
    pool.join()       

def sliceSearch(index,id,maxt,size,query=None):
    global hitsFromSlice
    if query != None:
        query = buildSlicedQueryForSearch(id,maxt,query)
    else:
        query = buildSlicedQuery(id,maxt)    
    hits = []
    res = es.search(index=index,body=query,size=size,scroll='5m')
    sid = res['_scroll_id']
    scrollSize = len(res['hits']['hits'])
    while scrollSize:
        hits.extend(processHits(res['hits']['hits']))
        res = es.scroll(scroll_id=sid, scroll='5m')
        sid = res['_scroll_id']
        scrollSize = len(res['hits']['hits'])
    hitsFromSlice.extend(hits)    

def globalSearch(body,size=1000):
    global hitsFromSlice
    hitsFromSlice = manager.list()
    if body == 'FETCH':
        body = buildFetchQuery()
    indices = ef.getIndices()
    t = 0
    h = []
    for i in indices:
        if body == buildFetchQuery():
            print('fetching...' + i)
            tmp , htmp = indexListAll(i,override=False)
            print(tmp)
        else:
            tmp , htmp = indexSearch(i,body,override=False)
            t += tmp
    return len(hitsFromSlice), hitsFromSlice

def buildFetchQuery():
    return {
        "query": {
            "match_all": {}
        }
    }

def buildQuery(body):
    return {
            "query": {
                "bool": {
                    "must": body
                },
                
        },
    }

def buildSlicedQueryForSearch(id,maxt,body):
    return {
            "slice": {
                "id": id, 
                "max": maxt 
            },
            "query": {
                "bool": {
                    "must": body
                },
        },
    }    

def buildSlicedQuery(id,maxt):
    return {
        "slice": {
            "id": id, 
            "max": maxt 
        },
        "query": {
            "match_all": {}
        }
    }    