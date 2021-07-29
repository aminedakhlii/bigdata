from flask import Flask,  render_template , url_for , redirect , flash, request, abort , jsonify, send_file
from server import app
import elasticfuncs
import search as s
import update as u
from wtforms import StringField
from forms import SearchForm
from werkzeug.utils import secure_filename
import os, time, json
import ast

UPLOAD_FOLDER = app.root_path + app.static_url_path + '/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

data = []

@app.context_processor
def headers():
    return dict(headers = elasticfuncs.getFields())

@app.route('/')
def home():
    global data
    data = []
    try:
        data = elasticfuncs.getInitialData(15)  
    except:
        data = []    
    fmap = elasticfuncs.convertFields()
    fields = elasticfuncs.getFieldsForView()    
    return render_template('index.html',data=data,fields=fields,fmap=fmap,elements=[])

@app.route('/partial', methods=['POST','GET'])
def partialShow():
    global data
    #data = request.form.getlist('data')
    element = request.form.get('element')
    #data = [ast.literal_eval(d) for d in data]
    fmap = elasticfuncs.convertFields()
    data = u.updatePartial(data,element)
    total = len(data)        
    viewSample = data[:100]        
    return render_template('index.html',data=viewSample,fmap=fmap,fields=elasticfuncs.getFieldsForView(),total=total,result=True) 

@app.route('/upload', methods=['POST','GET'])
def upload():
    start_time = time.time()
    indices = elasticfuncs.getIndices()
    if request.method == 'POST':
        index = ''
        if request.form.get('indexChoice') != 'other':
            index = request.form.get('indexChoice').lower()
        else:
            index = request.form.get('index').lower()
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and elasticfuncs.allowed_file(file.filename):
            index = index.replace(" ","")
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            elasticfuncs.upload(app.root_path,UPLOAD_FOLDER + '/' + filename,index)
            print("--- %s seconds ---" % (time.time() - start_time))
            return redirect(url_for('home'))
    return render_template('upload.html',indices=indices)

@app.route('/export', methods=['GET','POST'])
def export():
    global data
    #data = request.form.getlist('data')
    #data = [ast.literal_eval(d) for d in data]
    exported = elasticfuncs.export(data,app.root_path)
    if exported:
        return send_file(app.root_path + '/exported.csv', as_attachment=True,mimetype='text/csv')
    return redirect(url_for('home'))

@app.route('/status')
def status():
    status = elasticfuncs.getStatus()
    return render_template('status.html',status=status)

@app.route('/settings' , methods=['GET','POST'])
def settings():
    allowedFields = elasticfuncs.getFields()
    allowedFields = [f for f in allowedFields if f != 'facebook_UID']
    delete = request.args.get('delete')
    modify = request.args.get('modify')
    if request.method == 'POST':
        if modify:
            old = request.form.get('field')
            new = request.form.get('new')
            if elasticfuncs.modifyField(old,new):
                return redirect(url_for('home'))
        elif delete:
            target = request.form.get('index')
            elasticfuncs.deleteIndex(target)
            return redirect(url_for('home'))       
        else:
            name = request.form.get('name')
            if elasticfuncs.addField(name):
                return redirect(url_for('home'))
    return render_template('add.html',allowedFields=allowedFields,indices=elasticfuncs.getIndices())

@app.route('/search')
def search():
    global data
    data = []
    fmap = elasticfuncs.convertFields()
    if 'phone_FB' in request.args.get('options'):
        key = 'phone_FB'
    else:
        key = request.args.get('options')     
    body = {'term': {key:request.args.get('search').lower()}}
    total, data = s.indexSearch('all', body=body)
    return render_template('index.html',fmap=fmap,data=data,result=True,total=total,fields=elasticfuncs.getFieldsForView(),elements=[])

@app.route('/searchForm', methods=['POST','GET'])
def searchForm():
    global data
    data = []
    fmap = elasticfuncs.convertFields()
    body = []
    if request.method == 'POST':
        options = request.form.getlist('options')
        choices = request.form.getlist('choice')
        if len(choices) == len([]) or choices == ['']:
            if request.form.get('index') == 'all':
                total,data = s.indexSearch(request.form.get('index'),'FETCH')
            else:
                total,data = s.indexListAll(request.form.get('index'))
        else:    
            for o in options:
                body.append({ 'term' : { o : choices[options.index(o)].lower() }})
            total, data = s.indexSearch(body=body,index=request.form.get('index'))
        viewSample = data[:100]    
        return render_template('index.html',fmap=fmap,data=viewSample,result=True,
        total=total,fields=elasticfuncs.getFieldsForView(),elements=[])
    #data = elasticfuncs.searchData(request.args.get('options'),request.args.get('search'))
    return render_template('searchForm.html',indices=elasticfuncs.getIndices())

@app.route('/keys', methods=['POST','GET'])
def keys():
    fields = elasticfuncs.getFieldsForView()
    if request.method == 'POST':
        choices = request.form.getlist('chosen')
        elasticfuncs.setKeys(choices)
        redirect(url_for('settings'))
    return render_template('keys.html',fields=fields)

@app.route('/seckeys', methods=['POST','GET'])
def seckeys():
    checked = elasticfuncs.getSecKeys()
    fields = elasticfuncs.getFieldsForView()
    if request.method == 'POST':
        choices = request.form.getlist('chosen')
        elasticfuncs.setSecKeys(choices)
        redirect(url_for('settings'))
    return render_template('keys.html',fields=fields,checked=checked)   

@app.route('/priority', methods=['POST','GET'])
def priority():
    if request.method == 'POST':
        fs = elasticfuncs.getFieldsForView()
        fmap = elasticfuncs.convertFields()
        priorityList = []
        for f in fs:
            p = request.form.get(f['field'])
            if p == '':
                p = 0
            else:
                p = int(p)  
            priorityList.append({fmap[fs.index(f)][f['field']]:p})    
        elasticfuncs.setPriorities(priorityList)      
    return render_template('priority.html',fields=elasticfuncs.getFieldsForView())    