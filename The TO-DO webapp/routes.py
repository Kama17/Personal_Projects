from app import app
from flask import render_template, redirect, url_for, flash, get_flashed_messages
import forms 
from  models import Task
from app import db
from datetime import datetime

@app.route('/')
@app.route('/index')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks = tasks)


@app.route('/add', methods = ['GET', 'POST'])
def add():
    form = forms.AddTaskForm()
    if form.validate_on_submit():
        t = Task(title =form.title.data, date = datetime.utcnow())
        db.session.add(t)
        db.session.commit()
        flash('Task submited')
        return redirect(url_for('index'))
    return render_template('add.html', form = form)


@app.route('/edit/<int:task_id>', methods = ['Get', 'POST'])
def edit(task_id):
    task = Task.query.get(task_id)
    form = forms.AddTaskForm()

    if task:
        
        if form.validate_on_submit():
            task.title = form.title.data
            task.data = datetime.utcnow()
            db.session.commit()
            flash('Task Updated')
            return redirect(url_for('index'))
       
        form.title.data = task.title
        return render_template('edit.html', form = form, task_id = task_id)
        
    return redirect(url_for('index'))
    
@app.route('/home')
def home():
    return redirect(url_for('about', name='World'))

@app.route('/about/<name>')
def about(name):
    return f'Hello {name}'
