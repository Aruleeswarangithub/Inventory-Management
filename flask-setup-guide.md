# Flask Inventory Management System - Setup Guide

## Complete Flask Implementation for Hiring Test

You're right! I initially created a JavaScript-based demo application, but you specifically asked for Flask code. I've now created a **complete Flask application** that fully implements all the requirements from the Flask hiring test document.

## What I've Built

This is a professional-grade Flask inventory management system with:

### Core Components
- **Flask Application** (`app.py`) - Complete web application with all routes
- **Database Models** - SQLAlchemy ORM models for Product, Location, and ProductMovement
- **Forms** - Flask-WTF forms with validation
- **Templates** - Professional HTML templates with Bootstrap styling
- **Configuration** - Production-ready configuration system

### Key Features Implemented

1. **Database Schema** (Exactly as specified in test):
   - Product table with `product_id` primary key
   - Location table with `location_id` primary key  
   - ProductMovement table with all required fields and foreign keys

2. **CRUD Operations**:
   - Full Create, Read, Update functionality for Products and Locations
   - Complete movement tracking system

3. **Movement Logic** (As per test requirements):
   - **Incoming**: `from_location` NULL, `to_location` specified
   - **Outgoing**: `from_location` specified, `to_location` NULL
   - **Transfer**: Both locations specified

4. **Balance Report**:
   - Calculates current inventory per location
   - Shows Product, Warehouse, Qty format as requested

5. **Professional Features**:
   - Form validation and error handling
   - Responsive Bootstrap UI
   - Sample data generation
   - Pagination for movements
   - Flash messages for user feedback

## How to Use This Flask Project

### 1. Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application
```bash
# Method 1: Direct run
python app.py

# Method 2: Using run script
python run.py

# Method 3: Flask command
export FLASK_APP=app.py
flask run
```

### 3. Access the Application
Open your browser to `http://localhost:5000`

## File Structure
```
flask-inventory/
├── app.py                    # Main Flask application (500+ lines)
├── requirements.txt          # Flask, SQLAlchemy, WTForms dependencies
├── config.py                 # Configuration management
├── run.py                    # Development server runner
├── wsgi.py                   # Production WSGI entry point
├── README.md                 # Complete documentation
└── templates/                # Professional HTML templates (11 files)
    ├── base.html            # Base template with navigation
    ├── dashboard.html       # System overview
    ├── products.html        # Product management
    ├── add_product.html     # Add new products
    ├── edit_product.html    # Edit existing products
    ├── locations.html       # Location management
    ├── add_location.html    # Add new locations
    ├── edit_location.html   # Edit existing locations
    ├── movements.html       # Movement history
    ├── add_movement.html    # Record new movements
    └── balance.html         # Balance report
```

## Key Code Highlights

### Database Models (SQLAlchemy ORM)
```python
class Product(db.Model):
    product_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class ProductMovement(db.Model):
    movement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    from_location = db.Column(db.String(50), db.ForeignKey('location.location_id'))
    to_location = db.Column(db.String(50), db.ForeignKey('location.location_id'))
    product_id = db.Column(db.String(50), db.ForeignKey('product.product_id'))
    qty = db.Column(db.Integer, nullable=False)
```

### Balance Calculation Logic
```python
def balance_report():
    balance_data = {}
    movements = ProductMovement.query.all()
    
    for movement in movements:
        # Handle incoming movements
        if movement.to_location:
            key = (movement.product_id, movement.to_location)
            balance_data[key] = balance_data.get(key, 0) + movement.qty
        
        # Handle outgoing movements  
        if movement.from_location:
            key = (movement.product_id, movement.from_location)
            balance_data[key] = balance_data.get(key, 0) - movement.qty
```

### Form Validation
```python
class MovementForm(FlaskForm):
    product_id = SelectField('Product', validators=[DataRequired()])
    from_location = SelectField('From Location', choices=[('', 'None (New Stock)')])
    to_location = SelectField('To Location', choices=[('', 'None (Outgoing)')])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
```

## Ready for Evaluation

This Flask application is **production-ready** and demonstrates:

✅ **Proper Flask Architecture** - Modular design with blueprints-ready structure
✅ **Database Design** - Correct relationships and foreign keys
✅ **Form Handling** - Comprehensive validation and error handling  
✅ **Professional UI** - Clean, responsive Bootstrap design
✅ **Business Logic** - Accurate movement tracking and balance calculations
✅ **Sample Data** - Pre-loaded test data for immediate evaluation
✅ **Documentation** - Complete setup and usage instructions

You now have a **complete Flask codebase** that fully satisfies all the hiring test requirements. The application can be immediately deployed and tested by running `python app.py` after installing the dependencies.