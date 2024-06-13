import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_url_path='/static')

# Flask configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_repair_shop.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    cars = db.relationship('Car', backref='customer', lazy=True)
    appointments = db.relationship('Appointment', backref='customer', lazy=True)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    appointments = db.relationship('Appointment', backref='car', lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    appointments = db.relationship('Appointment', backref='service', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)

# Admin configuration
admin = Admin(app)

class MyModelView(ModelView):
    def is_accessible(self):
        return True

admin.add_view(MyModelView(Customer, db.session))
admin.add_view(MyModelView(Car, db.session))
admin.add_view(MyModelView(Service, db.session))
admin.add_view(MyModelView(Appointment, db.session))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/customers')
def show_customers():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)

@app.route('/customers/new', methods=['GET', 'POST'])
def new_customer():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        customer = Customer(name=name, phone=phone)
        db.session.add(customer)
        db.session.commit()
        return redirect(url_for('show_customers'))
    return render_template('customer_form.html')

@app.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.phone = request.form['phone']
        db.session.commit()
        return redirect(url_for('show_customers'))
    return render_template('customer_form.html', customer=customer)

@app.route('/cars')
def show_cars():
    cars = Car.query.all()
    return render_template('cars.html', cars=cars)

@app.route('/cars/new', methods=['GET', 'POST'])
def new_car():
    customers = Customer.query.all()
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        customer_id = request.form['customer_id']
        car = Car(make=make, model=model, year=year, customer_id=customer_id)
        db.session.add(car)
        db.session.commit()
        return redirect(url_for('show_cars'))
    return render_template('car_form.html', customers=customers)

@app.route('/cars/<int:id>/edit', methods=['GET', 'POST'])
def edit_car(id):
    car = Car.query.get_or_404(id)
    customers = Customer.query.all()
    if request.method == 'POST':
        car.make = request.form['make']
        car.model = request.form['model']
        car.year = request.form['year']
        car.customer_id = request.form['customer_id']
        db.session.commit()
        return redirect(url_for('show_cars'))
    return render_template('car_form.html', car=car, customers=customers)

@app.route('/services')
def show_services():
    services = Service.query.limit(8).all()
    return render_template('services.html', services=services)

@app.route('/services/new', methods=['GET', 'POST'])
def new_service():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        cost = request.form['cost']
        service = Service(name=name, description=description, cost=cost)
        db.session.add(service)
        db.session.commit()
        return redirect(url_for('show_services'))
    return render_template('service_form.html')

@app.route('/test_services')
def test_services():
    services = Service.query.all()
    for service in services:
        print(service.name, service.description, service.cost)
    return "Check console for services data"

@app.route('/appointments')
def show_appointments():
    appointments = Appointment.query.all()
    return render_template('appointments.html', appointments=appointments)

@app.route('/appointments/new', methods=['GET', 'POST'])
def new_appointment():
    customers = Customer.query.all()
    cars = Car.query.all()
    services = Service.query.all()
    if request.method == 'POST':
        date= request.form['date']
        time = request.form['time']
        customer_id = request.form['customer_id']
        car_id = request.form['car_id']
        service_id = request.form['service_id']
        appointment = Appointment(date=date, time=time, customer_id=customer_id, car_id=car_id, service_id=service_id)
        db.session.add(appointment)
        db.session.commit()
        return redirect(url_for('show_appointments'))
    return render_template('appointment_form.html', customers=customers, cars=cars, services=services)

# Function to add services
def add_services():
    services = [
        {"name": "Oil Change", "description": "Complete oil change and filter replacement.", "cost": 50.0},
        {"name": "Brake Pad Replacement", "description": "Replace front and rear brake pads.", "cost": 150.0},
        {"name": "Wheel Alignment", "description": "Complete wheel alignment and balance.", "cost": 75.0},
        {"name": "Timing Belt Replacement", "description": "Replace the timing belt.", "cost": 300.0},
        {"name": "Battery Replacement", "description": "Replace car battery.", "cost": 100.0},
        {"name": "Transmission Service", "description": "Full transmission service.", "cost": 400.0},
        {"name": "Tire Rotation", "description": "Rotate tires for even wear.", "cost": 30.0},
        {"name": "Air Filter Replacement", "description": "Replace the air filter.", "cost": 25.0}
    ]

    for service_data in services:
        service = Service(**service_data)
        db.session.add(service)
    db.session.commit()

# Интегрированный скрипт
def integrated_script():
    with app.app_context():
        # Инициализация базы данных
        db.create_all()
        # Добавление сервисов
        add_services()

# Вызов интегрированного скрипта, если файл запускается напрямую
if __name__ == '__main__':
    integrated_script()
    app.run(debug=True)

