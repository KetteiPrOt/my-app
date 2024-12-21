from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine, insert, String, select, text
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker

app = Flask(__name__)

# Set Up Database
engine = create_engine("mysql+pymysql://root:@localhost/my_app")

class Base(DeclarativeBase): pass

class Product(Base):
    __tablename__ = "products"

    def __init__(self, id, name):
        self.id = id; self.name = name

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r},)"

    def all():
        conn = engine.connect()
        conn.begin()
        products = conn.execute(select(Product)).all()
        conn.commit()
        conn.close()
        return products
    
    def find(id):
        conn = engine.connect()
        conn.begin()
        product = conn.execute(select(Product).where(text(f'id = {id}'))).first()
        conn.commit()
        conn.close()
        return product
    
    def insert(name):
        conn = engine.connect()
        conn.begin()
        conn.execute(
            insert(Product),
            [{"id": 'DEFAULT', "name": name}],
        )
        conn.commit()
        conn.close()
    
    def update(id, name):
        conn = engine.connect()
        conn.begin()
        conn.execute(text(f"UPDATE products SET name = '{name}' WHERE id = {id}"))
        conn.commit()
        conn.close()

    def destroy(id):
        conn = engine.connect()
        conn.begin()
        conn.execute(text(f"DELETE FROM products WHERE id = {id}"))
        conn.commit()
        conn.close()

Base.metadata.create_all(engine)

# App Routes
@app.get('/')
def home():
    return render_template('home.html')

@app.get('/productos')
def index():
    return render_template('index.html', products=Product.all())

@app.get('/productos/crear')
def create():
    return render_template('create.html')

@app.post('/productos')
def store():
    Product.insert(request.form['name'])
    return redirect(url_for('index'))

@app.get('/productos/<int:product_id>/editar')
def edit(product_id):
    return render_template('edit.html', product=Product.find(product_id))

@app.post('/productos/<int:product_id>')
def update(product_id):
    Product.update(product_id, request.form['name'])
    return redirect(url_for('index'))

@app.post('/productos/<int:product_id>/eliminar')
def destroy(product_id):
    Product.destroy(product_id)
    return redirect(url_for('index'))