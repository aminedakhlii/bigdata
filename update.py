#import elasticfuncs as ef
#import search 
from multiprocessing import Pool, Manager
import os, math

manager = Manager()
data_ = manager.list()

def updatePartial(data,element):
    global data_
    data_ = manager.list()
    nproc = os.cpu_count() - 1
    chunk = math.ceil(len(data)/nproc)
    last = math.floor(len(data)/nproc)
    pool = Pool(nproc)
    for i in range(nproc):
        if i == nproc - 1:
            pool.apply_async(removeEmpty, (element,data[i*chunk:]))
        else:
            pool.apply_async(removeEmpty, (element,data[i*chunk:i*chunk + chunk]))
    pool.close()
    pool.join()
    return data_     

def removeEmpty(element,data):
    global data_
    for d in data[:]:
        if d[element] in ['','None',None,' ']:
            data.remove(d)  
    data_.extend(data)

def replaceExistant(old,new,indices,es,sk,index=None):
    non_existant = ['','None',None]
    shared_items = {k: old[k] for k in old if k in new and old[k] == new[k]}
    if indices == [None]:
        return old
    changes = ''
    for k,v in old.items():
        if k not in new.keys():
            new[k] = ''
        if k not in shared_items.keys() and k in new.keys():
            if new[k] not in non_existant and old[k] != new[k]:
                old[k] = new[k]
                changes += 'ctx._source.' + k + " = '" + (new[k]) +"';"
    key = ''
    for k in sk:
        if k in shared_items.keys():
            key = k
            break   
    if key == '':
        return
    if changes != '':
        oldQuery = {
            "query": {
                    "term": {
                        key: old[key]
                    }
            },
            "script": {
                "inline": changes,
                "lang": "painless"
            }
        }
        for ix in indices:
            try:
                es.indices.refresh(index = ix)
                p = es.update_by_query(index=ix,body=oldQuery)
            except Exception as e:
                print('replacing' + e)
                continue
    replaceExistant(old=new,new=old,indices=[index],es=es,sk=sk)        
    return old