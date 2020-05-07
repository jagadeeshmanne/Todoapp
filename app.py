from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:laxman@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

# db.create_all()

@app.route('/')
def index():
    data = Todo.query.order_by('id').all()
    return render_template('index.html', data=data)


@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        # description = request.form.get('description', '')
        description = request.get_json()['description']
        new_todo = Todo(description=description)
        db.session.add(new_todo)
        db.session.commit()
        # return redirect(url_for('index'))
        body['description'] = new_todo.description
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify(body)

# @app.route('/todos/<todo_id>/set-completed', methods=['POST'])
# def set_completed(todo_id):
#     error = False
#     try: 
#         completed = request.get_json()['completed']
#         print('completed', completed)
#         todo_obj = Todo.query.get(todo_id)
#         todo_obj.completed = completed
#         db.session.commit()
#     except:
#         db.session.rollback()
#         error = True
#         print(sys.exc_info())
#     finally:
#         db.session.close()
#     if error:
#         abort(500)
#     else:
#         return redirect(url_for('index'))

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
  try:
    completed = request.get_json()['completed']
    print('completed', completed)
    todo = Todo.query.get(todo_id)
    todo.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=5000)