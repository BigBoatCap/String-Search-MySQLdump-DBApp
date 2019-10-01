from flask import Flask, render_template, redirect, url_for, request, flash
import os, subprocess


app = Flask(__name__)
app.config.from_pyfile("config.py")
app.secret_key = app.config['SECRET_KEY']


@app.route('/')
@app.route('/home')
def hello_world():
    return render_template("/index.html")

@app.route('/badext')
def fallback():
    return render_template("/badext.html")

@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        print(request.form.get('thetable'))
        print(request.form.get('thestring'))
        thetable = request.form.get('thetable')
        thestring = request.form.get('thestring')

        db_query = 'USE TEST; SELECT table_name FROM information_schema.tables where table_schema="TEST";'

#        db_query = 'USE TEST; SELECT * FROM %s where %s like %s limit 100;";' % (thetable, thestring)
        command = ['mysql', '-sN', '-u%s' % app.config['DBUSER'], '-p%s' % app.config['DBPASSWORD'],
                   '-h%s' % app.config['DBHOST'], '-e%s' % db_query]
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
#        print('#######################################  %s' % out)
        tables = out.decode().split()
        print(tables)
        for table in tables:
            print(table)
            db_query = 'SELECT column_name from information_schema.columns where information_schema.table_name = %s;' % (table)
            command = ['mysql', '-sN', '-u%s' % app.config['DBUSER'], '-p%s' % app.config['DBPASSWORD'],
                       '-h%s' % app.config['DBHOST'], '-e%s' % db_query]
            proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            print(out, err)
            print('======>>> NEXT TABLE: \n')
            ####
            ####
            ####   exec user information_schema; select * from columns where table_name = 'user';
            ####
            ####
            #for column in columns
            #db_query = 'SELECT column_name from information_schema.columns where table_name like %s;' % (table)
            #command = ['mysql', '-sN', '-u%s' % app.config['DBUSER'], '-p%s' % app.config['DBPASSWORD'],
            #           '-h%s' % app.config['DBHOST'], '-e%s' % db_query]
            #proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #out, err = proc.communicate()
            #print(out.decode())

        return render_template("searchresult.html", contentlen=len(out), content=out.decode())


@app.route('/exec_import/<string:filename>')
def exec_import(filename, path=app.config['UPLOAD_FOLDER']):

    dump_filename = path + filename
    print(dump_filename)
    with open(dump_filename, 'r') as f:

        db_query = 'DROP DATABASE if exists TEST'
        print(app.config['DBUSER'], app.config['DBPASSWORD'], app.config['DBHOST'])
        command = ['mysql', '-u%s' % app.config['DBUSER'], '-p%s' % app.config['DBPASSWORD'], '-h%s' % app.config['DBHOST'], '-e%s' % db_query]
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        print(out, err)

        db_query = 'CREATE DATABASE TEST'
        command = ['mysql', '-u%s' % app.config['DBUSER'], '-p%s' % app.config['DBPASSWORD'], '-h%s' % app.config['DBHOST'], '-e%s' % db_query]
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()

        command = ['mysql', '-u%s' % app.config['DBUSER'], '-p%s' % app.config['DBPASSWORD'], '-h%s' % app.config['DBHOST'], 'TEST']
        proc = subprocess.Popen(command, stdin=f, shell=True)
        out, err = proc.communicate()


        db_query = 'SELECT table_name FROM information_schema.tables where table_schema="TEST";'
        command = ['mysql', '-sN', '-u%s' % app.config['DBUSER'], '-p%s' % app.config['DBPASSWORD'], '-h%s' % app.config['DBHOST'], '-e%s' % db_query]
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        print('#######################################')
        print(out.decode())
        print(len(out))
        return render_template("search.html", contentlen=len(out), content=out.decode())


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print("LABEL POST <<< =============================== ")

        # check if the post request has the file part
        if 'thefile' not in request.files:
            error = 'No file part'
            return redirect(request.url)
        file = request.files['thefile']
        # if DBUSER does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            error = 'No selected file'
            return redirect(request.url)
        if file and file.filename.rsplit('.', 1)[1].lower() == app.config['ALLOWED_EXTENSIONS']:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print('Successfully uploaded dump ' + filename)
            print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            return redirect(url_for('exec_import', filename=filename))

        if file and file.filename.rsplit('.', 1)[1].lower() != app.config['ALLOWED_EXTENSIONS']:
            return render_template("badext.html")
    return render_template("index.html")


@app.route('/tselection/<string:tbl_name>/<string:search_patt>')
def exec_tselection(tbl_name, search_patt):
    print(search_patt, tbl_name)
    db_query = 'USE TEST; SELECT * FROM %s where number like %s limit 100;";' % (tbl_name, search_patt)
    command = ['mysql', '-sN', '-u%s' % app.config['DBUSER'], '-p%s' % app.config['DBPASSWORD'],
               '-h%s' % app.config['DBHOST'], '-e%s' % db_query]
    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    print('#######################################  %s' % out)
    print(out.decode())
    return render_template("tselect.html", contentlen=len(out), content=out.decode())



if __name__ == '__main__':
    app.run()
