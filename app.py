from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, DateTimeField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models code
class Product(db.Model):
    product_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Product {self.product_id}: {self.name}>'

class Location(db.Model):
    location_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Location {self.location_id}: {self.name}>'

class ProductMovement(db.Model):
    movement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    from_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    to_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    product_id = db.Column(db.String(50), db.ForeignKey('product.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    # Relationships
    product = db.relationship('Product', backref=db.backref('movements', lazy=True))
    from_loc = db.relationship('Location', foreign_keys=[from_location], backref=db.backref('outgoing_movements', lazy=True))
    to_loc = db.relationship('Location', foreign_keys=[to_location], backref=db.backref('incoming_movements', lazy=True))

    def __repr__(self):
        return f'<Movement {self.movement_id}: {self.product_id} qty={self.qty}>'

# Helper Functions
def get_current_stock(product_id, location_id):
    """Calculate current stock of a product at a specific location"""
    # Sum incoming quantities (to this location)
    incoming = db.session.query(db.func.sum(ProductMovement.qty)).filter(
        ProductMovement.product_id == product_id,
        ProductMovement.to_location == location_id
    ).scalar() or 0

    # Sum outgoing quantities (from this location)
    outgoing = db.session.query(db.func.sum(ProductMovement.qty)).filter(
        ProductMovement.product_id == product_id,
        ProductMovement.from_location == location_id
    ).scalar() or 0

    return incoming - outgoing

def get_product_summary():
    """Get total in-hand and sold quantities for all products"""
    products = Product.query.all()
    summary = {}

    for product in products:
        # Total imported (all incoming movements)
        total_imported = db.session.query(db.func.sum(ProductMovement.qty)).filter(
            ProductMovement.product_id == product.product_id,
            ProductMovement.to_location.isnot(None)
        ).scalar() or 0

        # Total sold/exported (all outgoing movements where to_location is NULL)
        total_sold = db.session.query(db.func.sum(ProductMovement.qty)).filter(
            ProductMovement.product_id == product.product_id,
            ProductMovement.to_location.is_(None)
        ).scalar() or 0

        # Current in-hand = imported - sold (details about stock)
        in_hand = total_imported - total_sold

        summary[product.product_id] = {
            'in_hand': in_hand,
            'sold': total_sold,
            'imported': total_imported
        }

    return summary

def get_location_stock_summary():
    """Get stock summary by location for each product"""
    balance_data = {}
    movements = ProductMovement.query.all()

    for movement in movements:
        product_id = movement.product_id

        # Handle incoming movements (to_location)
        if movement.to_location:
            key = (product_id, movement.to_location)
            if key not in balance_data:
                balance_data[key] = 0
            balance_data[key] += movement.qty

        # Handle outgoing movements (from_location)
        if movement.from_location:
            key = (product_id, movement.from_location)
            if key not in balance_data:
                balance_data[key] = 0
            balance_data[key] -= movement.qty

    return balance_data

def get_stock_notifications():
    """Get notifications for out of stock and low stock products"""
    notifications = {
        'out_of_stock': [],
        'low_stock': [],
        'count': 0
    }

    product_summary = get_product_summary()

    for product_id, data in product_summary.items():
        product = Product.query.get(product_id)
        if not product:
            continue

        in_hand = data['in_hand']

        if in_hand <= 0:
            notifications['out_of_stock'].append({
                'product_id': product_id,
                'product_name': product.name,
                'in_hand': in_hand,
                'message': f'{product.name} is out of stock! Consider restocking immediately.',
                'urgency': 'danger'
            })
        elif in_hand <= 5:  # Low stock threshold
            notifications['low_stock'].append({
                'product_id': product_id,
                'product_name': product.name,
                'in_hand': in_hand,
                'message': f'{product.name} is running low (Only {in_hand} left). Consider restocking soon.',
                'urgency': 'warning'
            })

    notifications['count'] = len(notifications['out_of_stock']) + len(notifications['low_stock'])
    return notifications

# Forms
class ProductForm(FlaskForm):
    product_id = StringField('Product ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')

class LocationForm(FlaskForm):
    location_id = StringField('Location ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')

class MovementForm(FlaskForm):
    product_id = SelectField('Product', validators=[DataRequired()])
    from_location = SelectField('From Location', choices=[('', 'None (New Stock)')])
    to_location = SelectField('To Location', choices=[('', 'None (Outgoing)')])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])

# Context processor to make notifications available to all templates
@app.context_processor
def inject_notifications():
    return {'stock_notifications': get_stock_notifications()}

# Routes
@app.route('/')
def dashboard():
    total_products = Product.query.count()
    total_locations = Location.query.count()
    total_movements = ProductMovement.query.count()

    # Recent movements
    recent_movements = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).limit(5).all()

    # Get stock notifications for dashboard alerts
    notifications = get_stock_notifications()

    return render_template('dashboard.html', 
                         total_products=total_products,
                         total_locations=total_locations,
                         total_movements=total_movements,
                         recent_movements=recent_movements,
                         notifications=notifications)

@app.route('/notifications')
def notifications():
    """Dedicated notifications page"""
    notifications = get_stock_notifications()
    return render_template('notifications.html', notifications=notifications)

@app.route('/api/notifications')
def api_notifications():
    """API endpoint for getting notifications"""
    notifications = get_stock_notifications()
    return jsonify(notifications)

@app.route('/products')
def products():
    products = Product.query.all()
    # Get summary data for all products
    summary = get_product_summary()

    return render_template('products.html', products=products, summary=summary)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        # Check if product already exists
        existing = Product.query.get(form.product_id.data)
        if existing:
            flash('Product with this ID already exists!', 'error')
            return render_template('add_product.html', form=form)

        product = Product(
            product_id=form.product_id.data,
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))

    return render_template('add_product.html', form=form)

@app.route('/products/edit/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    form.product_id.render_kw = {'readonly': True}  # Make ID readonly

    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products'))

    return render_template('edit_product.html', form=form, product=product)

@app.route('/locations')
def locations():
    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

@app.route('/locations/add', methods=['GET', 'POST'])
def add_location():
    form = LocationForm()
    if form.validate_on_submit():
        # Check if location already exists
        existing = Location.query.get(form.location_id.data)
        if existing:
            flash('Location with this ID already exists!', 'error')
            return render_template('add_location.html', form=form)

        location = Location(
            location_id=form.location_id.data,
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(location)
        db.session.commit()
        flash('Location added successfully!', 'success')
        return redirect(url_for('locations'))

    return render_template('add_location.html', form=form)

@app.route('/locations/edit/<location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    form = LocationForm(obj=location)
    form.location_id.render_kw = {'readonly': True}  # Make ID readonly

    if form.validate_on_submit():
        location.name = form.name.data
        location.description = form.description.data
        db.session.commit()
        flash('Location updated successfully!', 'success')
        return redirect(url_for('locations'))

    return render_template('edit_location.html', form=form, location=location)

@app.route('/movements')
def movements():
    page = request.args.get('page', 1, type=int)
    movements = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('movements.html', movements=movements)

@app.route('/movements/add', methods=['GET', 'POST'])
def add_movement():
    form = MovementForm()

    # Populate choices
    products = Product.query.all()
    locations = Location.query.all()

    form.product_id.choices = [(p.product_id, f"{p.product_id} - {p.name}") for p in products]
    form.from_location.choices = [('', 'None (New Stock)')] + [(l.location_id, f"{l.location_id} - {l.name}") for l in locations]
    form.to_location.choices = [('', 'None (Outgoing)')] + [(l.location_id, f"{l.location_id} - {l.name}") for l in locations]

    if form.validate_on_submit():
        from_loc = form.from_location.data if form.from_location.data else None
        to_loc = form.to_location.data if form.to_location.data else None

        # Validate movement logic
        if not from_loc and not to_loc:
            flash('Either from_location or to_location must be specified!', 'error')
            return render_template('add_movement.html', form=form)

        if from_loc == to_loc and from_loc:
            flash('From and To locations cannot be the same!', 'error')
            return render_template('add_movement.html', form=form)

        # **Stock validation for outgoing/transfer movements**
        if from_loc:
            current_stock = get_current_stock(form.product_id.data, from_loc)
            if form.qty.data > current_stock:
                product = Product.query.get(form.product_id.data)
                location = Location.query.get(from_loc)
                flash(f'Insufficient stock! Available quantity of {product.name} at {location.name}: {current_stock}. You tried to move: {form.qty.data}', 'error')
                return render_template('add_movement.html', form=form)

        movement = ProductMovement(
            product_id=form.product_id.data,
            from_location=from_loc,
            to_location=to_loc,
            qty=form.qty.data
        )

        db.session.add(movement)
        db.session.commit()
        flash('Movement added successfully!', 'success')
        return redirect(url_for('movements'))

    return render_template('add_movement.html', form=form)

@app.route('/balance')
def balance_report():
    # Get location-wise balance data
    balance_data = get_location_stock_summary()

    # Format data for display
    balance_list = []
    for (product_id, location_id), qty in balance_data.items():
        if qty > 0:  # Only show positive balances
            product = Product.query.get(product_id)
            location = Location.query.get(location_id)
            balance_list.append({
                'product_name': product.name if product else product_id,
                'product_id': product_id,
                'location_name': location.name if location else location_id,
                'location_id': location_id,
                'qty': qty
            })

    # Sort by product name then location name
    balance_list.sort(key=lambda x: (x['product_name'], x['location_name']))

    # **Product summary for total imports and exports**
    product_summary = get_product_summary()

    # Convert to list for template
    product_summary_list = []
    for product_id, data in product_summary.items():
        product = Product.query.get(product_id)
        if product:
            product_summary_list.append({
                'product_name': product.name,
                'product_id': product_id,
                'total_imported': data['imported'],
                'total_sold': data['sold'],
                'in_hand': data['in_hand']
            })

    product_summary_list.sort(key=lambda x: x['product_name'])

    return render_template('balance.html', 
                         balance_list=balance_list, 
                         product_summary=product_summary_list)

def create_sample_data():
    """Create sample data for testing"""
    # Check if data already exists
    if Product.query.first():
        return

    # Add sample products
    products = [
        Product(product_id='LAPTOP001', name='Dell Laptop', description='High-performance laptop for business use'),
        Product(product_id='MOUSE001', name='Wireless Mouse', description='Ergonomic wireless mouse with USB receiver'),
        Product(product_id='KEYBOARD001', name='Mechanical Keyboard', description='RGB mechanical keyboard with tactile switches'),
        Product(product_id='MONITOR001', name='24-inch Monitor', description='Full HD LED monitor with adjustable stand')
    ]

    # Add sample locations
    locations = [
        Location(location_id='WAREHOUSE', name='Main Warehouse', description='Primary storage facility'),
        Location(location_id='STOREFRONT', name='Store Front', description='Retail display area'),
        Location(location_id='STORAGE', name='Storage Room', description='Secondary storage for overflow inventory'),
        Location(location_id='SHIPPING', name='Shipping Dock', description='Area for outbound shipments')
    ]

    for product in products:
        db.session.add(product)
    for location in locations:
        db.session.add(location)

    db.session.commit()

    # Add sample movements - including some that will result in low/out of stock
    movements = [
        # Initial stock to warehouse
        ProductMovement(from_location=None, to_location='WAREHOUSE', product_id='LAPTOP001', qty=50),
        ProductMovement(from_location=None, to_location='WAREHOUSE', product_id='MOUSE001', qty=10),  # Low initial stock
        ProductMovement(from_location=None, to_location='WAREHOUSE', product_id='KEYBOARD001', qty=5),   # Very low stock
        ProductMovement(from_location=None, to_location='WAREHOUSE', product_id='MONITOR001', qty=30),

        # Move to storefront
        ProductMovement(from_location='WAREHOUSE', to_location='STOREFRONT', product_id='LAPTOP001', qty=10),
        ProductMovement(from_location='WAREHOUSE', to_location='STOREFRONT', product_id='MOUSE001', qty=8),
        ProductMovement(from_location='WAREHOUSE', to_location='STOREFRONT', product_id='KEYBOARD001', qty=3),
        ProductMovement(from_location='WAREHOUSE', to_location='STOREFRONT', product_id='MONITOR001', qty=8),

        # Heavy sales - this will create out of stock situations
        ProductMovement(from_location='STOREFRONT', to_location=None, product_id='MOUSE001', qty=8),      # All sold from storefront
        ProductMovement(from_location='WAREHOUSE', to_location=None, product_id='MOUSE001', qty=2),       # Most sold from warehouse
        ProductMovement(from_location='STOREFRONT', to_location=None, product_id='KEYBOARD001', qty=3),   # All sold from storefront  
        ProductMovement(from_location='WAREHOUSE', to_location=None, product_id='KEYBOARD001', qty=2),    # Most sold from warehouse

        # Some laptop sales
        ProductMovement(from_location='STOREFRONT', to_location=None, product_id='LAPTOP001', qty=5),
        ProductMovement(from_location='WAREHOUSE', to_location=None, product_id='LAPTOP001', qty=20),

        # Monitor sales
        ProductMovement(from_location='STOREFRONT', to_location=None, product_id='MONITOR001', qty=3),
    ]

    for movement in movements:
        db.session.add(movement)

    db.session.commit()
    print("Sample data created successfully with low stock scenarios!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    app.run(debug=True)
