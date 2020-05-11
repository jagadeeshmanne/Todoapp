from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:laxman@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)


class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    child = db.relationship('Todo', backref='list', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TodoList {self.id} {self.name}>'


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

# db.create_all()

@app.route('/')
def index():
    return redirect(url_for('get_todo_lists', list_id=1))

@app.route('/lists/<list_id>')
def get_todo_lists(list_id):
    return render_template('index.html', 
    todolists=TodoList.query.all(),
    active_list=TodoList.query.get(list_id),
    todos=Todo.query.filter(Todo.list_id==list_id).order_by('id').all())


@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        # description = request.form.get('description', '')
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['id'] = todo.id
        body['completed'] = todo.completed
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(500)
    else:
        return jsonify(body)


@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed(todo_id):
    error = False
    try: 
        completed = request.get_json()['completed']
        print('completed', completed)
        todo_obj = Todo.query.get(todo_id)
        todo_obj.completed = completed
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return redirect(url_for('index'))


@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete(todo_id):
    error = False
    try:
        todo_item = Todo.query.get(todo_id)
        print('Todo object to be deleted:', todo_item)
        db.session.delete(todo_item)
        db.session.commit()
        print('Todo object deleted.')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    
    if error:
        abort(500)
    else:
        return jsonify({'success': True})

if __name__ == '__main__':
    app.run(port=5000)