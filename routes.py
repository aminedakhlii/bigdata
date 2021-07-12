from flask import Flask,  render_template , url_for , redirect , flash, request, abort , jsonify, send_file
from server import app
import elasticfuncs
from wtforms import StringField
from forms import SearchForm
from werkzeug.utils import secure_filename
import os, time

UPLOAD_FOLDER = app.root_path + app.static_url_path + '/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    data = elasticfuncs.getInitialData(15)
    return render_template('index.html',data=data,fields=elasticfuncs.getFields())

@app.route('/upload', methods=['POST','GET'])
def upload():
    start_time = time.time()
    indices = elasticfuncs.getIndices()
    if request.method == 'POST':
        index = ''
        if request.form.get('indexChoice') != 'other':
            index = request.form.get('indexChoice')
        else:
            index = request.form.get('index')
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and elasticfuncs.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            elasticfuncs.importCSV(UPLOAD_FOLDER + '/' + filename,index)
            print("--- %s seconds ---" % (time.time() - start_time))
            return redirect(url_for('home'))
    return render_template('upload.html',indices=indices)

@app.route('/export')
def export():
    data = request.args.getlist('data')
    exported = elasticfuncs.export(data)
    if exported:
        return send_file(app.root_path + '/exported.csv', as_attachment=True)
    return redirect(url_for('home'))

@app.route('/settings' , methods=['GET','POST'])
def settings(modify=True):
    allowedFields = elasticfuncs.getFields()
    allowedFields = [f for f in allowedFields if f is not 'facebook_UID']
    if request.method == 'POST':
        if modify:
            print(request.form)
            old = request.form.get('field')
            new = request.form.get('new')
            if elasticfuncs.modifyField(old,new):
                return redirect(url_for('home'))
        else:
            name = request.form.get('name')
            if elasticfuncs.addField(name):
                return redirect(url_for('home'))
    return render_template('add.html',allowedFields=allowedFields)

@app.route('/search')
def search():
    total, data = elasticfuncs.searchData({'term': {request.args.get('options'):request.args.get('search').lower()}})
    return render_template('index.html',data=data,result=True,total=total,fields=elasticfuncs.getFields())

@app.route('/searchForm', methods=['POST','GET'])
def searchForm():
    form = SearchForm()
    for f in elasticfuncs.getFields():
       setattr(SearchForm,f,StringField(f))
    if form.validate_on_submit():
        body = []
        for field in form:
            if field.data != '' and field.name != 'submit' and field.name != 'csrf_token' and field.name != 'index':
                choices = field.data.lower()
                choices = choices.split(",")
                print(choices)
                body.append({ 'terms' : { field.name : choices }})
        total, data = elasticfuncs.searchData(body,index=form.index.data)
        return render_template('index.html',data=data,result=True,total=total,fields=elasticfuncs.getFields())
    #data = elasticfuncs.searchData(request.args.get('options'),request.args.get('search'))
    return render_template('searchForm.html',form=form)
