from elasticsearch import Elasticsearch, helpers
import csv,sys,math,json
from server import db
from models import Fields
import time

ALLOWED_EXTENSIONS = {'txt', 'csv'}
csv.field_size_limit(sys.maxsize)

es = Elasticsearch(host = "localhost", port = 9200)

def getIndices():
    tmp = es.indices.get_alias("*")
    return [i for i in tmp if i[0] != '.']

def getFields():
    fields = Fields.query.all()
    return [f.name for f in fields]

def stdFields():
    ret = []
    res = getInitialData(1)
    for k,v in res[0].items():
        ret.append(k)
    return ret

def importCSV(filePath,index):
    with open(filePath, encoding="utf8") as f:
        reader = csv.DictReader(f)
        #writer = csv.writer(open('tmp.csv','w'),delimiter=',')
        fields = reader.fieldnames
        if index not in getIndices():
            es.indices.create(index=index)
        """"notExistant = []
        header = []
        for row in reader:
            for k,v in row.items():
                header.append(k)
            break
        for field in stdFields():
            if field not in fields:
                notExistant.append(field)
        writer.writerow(stdFields())
        for row in reader:
            for e in notExistant:
                row[e] = ''

            items = []
            for x in stdFields():
                items.append(row[x])
            writer.writerow(items)


    with open('tmp.csv','r') as fp:
        rdr = csv.DictReader(fp)
        for row in rdr:
            pass"""
        for success, info in helpers.parallel_bulk(es, actions=reader, index=index, chunk_size=10000, thread_count=16):
            if not success:
                print('A document failed:', info)
    with open(filePath) as f:
        exists = checkExistant(reader=csv.DictReader(f),index=index)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def addField(name):
    try:
        f = Fields(name=name)
        db.session.add(f)
        db.session.commit()
        return True
    except:
        return False

def modifyField(old,new):
    try:
        f = Fields.query.filter_by(name=old).first()
        print(f)
        f.name = new
        db.session.commit()
        return True
    except:
        return False

def checkExistant(reader,index='all'):
    found = False
    try:
        for row in reader:
            body = []
            for r in row:
                if row[r] == '' or row[r] == None or row[r] == 'None':
                    pass
                elif r == 'facebook_UID' or r == 'first_name_FB' or r == 'last_name_FB':# or 'phone_FB' in r:
                    body.append({'term' : {r:row[r].lower()}})
            total, data = searchData(body,must=True)
            if len(data) > len([]):
                if found is False:
                    found = True
                for d in data:
                    if 'null' in d.keys():
                        del d["null"]
                    new = replaceExistant(d,row)
            else:
                continue
        return found
    except Exception as e:
        print(e)
        return False


def replaceExistant(old,new):
    non_existant = ['','None',None]
    shared_items = {k: old[k] for k in old if k in new and old[k] == new[k]}
    changes = ''
    for k,v in old.items():
        if k not in shared_items.keys():
            if 'phone_FB' in k:
                tmp = 'phone_FB'
                if new[tmp] not in non_existant and new[tmp] != old[k]:
                    old[k] = new[tmp]
                    changes += 'ctx._source.' + k + " = '" + new[tmp] + "'; "
            else:
                if new[k] not in non_existant:
                    old[k] = new[k]
                    changes += 'ctx._source.' + k + " = '" + new[k] +"';"
    key = ''
    if 'facebook_UID' in shared_items.keys():
        key = 'facebook_UID'
    elif 'mail_FB' in shared_items.keys():
        key = 'mail_FB'
    elif 'phone_FB' in shared_items.keys():
        key = 'phone_FB'
    query = {
        "query": {
                "term": {
                    key: old[key],
                },
        },
        "script": {
            "inline": changes,
            "lang": "painless"
          },
    }
    if changes != '':
        for i in getIndices():
            es.indices.refresh(index = i)
            try:
                p = es.update_by_query(index=i,body=query)
            except Exception as e:
                print(e)
                continue
    return old

def searchData(body,must=True,index='all'):
    query = {}
    if must:
        query = {
            "query": {
                "bool": {
                    "must": body
                },
            },
        }
    else:
        query = {
            "query": {
                "bool": {
                    "should": body
                },
            },
        }
    print(query)
    hits = []
    try:
        total = 0
        indicies = getIndices()
        if index == 'all':
            for i in indicies:
                res = ''
                try:
                    res = es.search(index=i,size=10000, body=query)
                except:
                    continue
                total +=  res['hits']['total']['value']
                for hit in res['hits']['hits']:
                    hits.append(hit["_source"])
        else:
            res = es.search(index=index,size=10000, body=query)
            total += res['hits']['total']['value']
            for hit in res['hits']['hits']:
                hits.append(hit["_source"])
        hits = [i for n, i in enumerate(hits) if i not in hits[n + 1:]]
        return total, hits
    except Exception as e:
        print(e)
        return []



def getInitialData(size,index='all'):
    hits = []
    res = ''
    body = {
        "from" : 0, "size": size,
        "query": {
            "match_all": {}
        },
        "collapse": {
                "field": "facebook_UID.keyword"
              }
    }
    indicies = getIndices()
    if index == 'all':
        for i in indicies:
            try:
                res = es.search(index=i, body=body)
            except Exception as e:
                print(e)
                continue
            for hit in res['hits']['hits']:
                hits.append(hit["_source"])
    else:
        res = es.search(index=index, body=body)
        for hit in res['hits']['hits']:
            hits.append(hit["_source"])

    return [i for n, i in enumerate(hits) if i not in hits[n + 1:]]

def export(data):
    try:
        finalData = []
        for d in data:
            d = d.replace(" \'", " \"")
            d = d.replace("\',", "\",")
            d = d.replace("{\'", "{\"")
            d = d.replace("[\'", "[\"")
            d = d.replace("\']", "\"]")
            d = d.replace("\':", "\":")
            d = d.replace("None", '""')
            print(d)
            d = json.loads(d)
            if 'null' in d.keys():
                print('yes')
                del d["null"]
            finalData.append(d)
        #data = json.loads(data)
        header = finalData[0].keys()
        with open('exported.csv', 'w') as f:
             writer = csv.writer(f, delimiter=',')
             writer.writerow(header)
             for d in finalData:
                 writer.writerow(d.values())
        return True
    except:
        return False
