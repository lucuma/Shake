# -*- coding: utf-8 -*-
"""
    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.
"""
import os
import unittest
from datetime import datetime

import shake

from shakext.sqlalchemy import SQLAlchemy


def make_todo_model(db):
    class Todo(db.Model):
        __tablename__ = 'todo'
        id = db.Column('todo_id', db.Integer, primary_key=True)
        title = db.Column(db.String(60))
        text = db.Column(db.String)
        done = db.Column(db.Boolean, default=False)
        pub_date = db.Column(db.DateTime, default=datetime.utcnow)

        def __init__(self, title, text):
            self.title = title
            self.text = text

    return Todo


class TestDatabases(unittest.TestCase):

    def setUp(self):
        app = shake.Shake()
        db = SQLAlchemy()
        db.init_app(app)

        def index(request):
            return '\n'.join(x.title for x in self.Todo.query.all())

        def add(request):
            form = request.form
            todo = self.Todo(form['title'], form['text'])
            db.session.add(todo)
            db.session.commit()
            return 'added'

        app.add_url('/', index),
        app.add_url('/add', add, methods=['POST'])
        self.Todo = make_todo_model(db)
        db.create_all()

        self.app = app
        self.db = db

    def tearDown(self):
        self.db.drop_all()

    def test_basic_insert(self):
        c = self.app.test_client()
        c.post('/add', data=dict(title='First Item', text='The text'))
        c.post('/add', data=dict(title='2nd Item', text='The text'))
        rv = c.get('/')
        assert rv.data == 'First Item\n2nd Item'

    def test_request_context(self):
        assert len(self.Todo.query.all()) == 0
        todo = self.Todo('Test', 'test')
        self.db.session.add(todo)
        self.db.session.commit()
        assert len(self.Todo.query.all()) == 1

    def test_helper_api(self):
        assert self.db.metadata == self.db.Model.metadata


class TestMultipleDatabases(unittest.TestCase):
    file1 = 'db1.sqlite'
    file2 = 'db2.sqlite'

    def test_multiple_databases(self):
        uri1 = 'sqlite:///' + self.file1
        uri2 = 'sqlite:///' + self.file2
        app = shake.Shake()
        db1 = SQLAlchemy(uri1)
        db2 = SQLAlchemy(uri2)
        db1.init_app(app)
        db2.init_app(app)

        def add1(request):
            print 'add1'
            form = request.form
            todo1 = self.Todo1(form['title'], form['text'])
            db1.session.add(todo1)
            db1.session.commit()

        def add2(request):
            print 'add2'
            form = request.form
            todo2 = self.Todo2(form['title'], form['text'])
            db2.session.add(todo2)
            db2.session.commit()

        def count1(request):
            return str(self.Todo1.query.count())

        def count2(request):
            return str(self.Todo2.query.count())

        app.add_url('/add1/', add1, methods=['POST'])
        app.add_url('/add2/', add2, methods=['POST'])
        app.add_url('/count1/', count1)
        app.add_url('/count2/', count2)

        self.Todo1 = make_todo_model(db1)
        self.Todo2 = make_todo_model(db2)
        db1.create_all()
        db2.create_all()

        c = app.test_client()
        c.post('/add1/', data={'title': 'A', 'text': 'A'})
        c.post('/add1/', data={'title': 'B', 'text': 'B'})
        c.post('/add1/', data={'title': 'C', 'text': 'C'})

        c.post('/add2/', data={'title': 'D', 'text': 'D'})

        self.assertEqual(c.get('/count1/').data, '3')
        self.assertEqual(c.get('/count2/').data, '1')

    def tearDown(self):
        os.remove(self.file1)
        os.remove(self.file2)


if __name__ == '__main__':
    unittest.main()
