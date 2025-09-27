# Create templates directory and save the notification system templates

import os

os.makedirs('templates', exist_ok=True)

# Updated base.html template with notification system
base_html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Inventory Management System{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .notification-badge {
            position: absolute;
            top: -5px;
            right: -10px;
            background: #dc3545;
            color: white;
            border-radius: 50%;
            padding: 2px 6px;
            font-size: 11px;
            font-weight: bold;
        }
        .notification-item {
            border-left: 4px solid transparent;
            transition: all 0.3s ease;
        }
        .notification-item.danger {
            border-left-color: #dc3545;
            background-color: rgba(220, 53, 69, 0.1);
        }
        .notification-item.warning {
            border-left-color: #ffc107;
            background-color: rgba(255, 193, 7, 0.1);
        }
        .notification-item:hover {
            background-color: rgba(0, 0, 0, 0.05);
        }
        .notification-dropdown {
            width: 350px;
            max-height: 400px;
            overflow-y: auto;
        }
        @media (max-width: 768px) {
            .notification-dropdown {
                width: 300px;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                <i class="fas fa-warehouse me-2"></i>Inventory Management
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('dashboard') }}">
                            <i class="fas fa-tachometer-alt me-1"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="productsDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-box me-1"></i>Products
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('products') }}">View All</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('add_product') }}">Add New</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="locationsDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-map-marker-alt me-1"></i>Locations
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('locations') }}">View All</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('add_location') }}">Add New</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="movementsDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-exchange-alt me-1"></i>Movements
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('movements') }}">View All</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('add_movement') }}">Add New</a></li>
                        </ul>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('balance_report') }}">
                            <i class="fas fa-chart-bar me-1"></i>Balance Report
                        </a>
                    </li>
                </ul>
                
                <!-- Notifications Dropdown -->
                <ul class="navbar-nav">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle position-relative" href="#" id="notificationsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-bell"></i>
                            {% if stock_notifications.count > 0 %}
                                <span class="notification-badge">{{ stock_notifications.count }}</span>
                            {% endif %}
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end notification-dropdown" aria-labelledby="notificationsDropdown">
                            <li>
                                <h6 class="dropdown-header">
                                    <i class="fas fa-exclamation-triangle me-1"></i>Stock Alerts
                                    {% if stock_notifications.count > 0 %}
                                        <span class="badge bg-danger ms-2">{{ stock_notifications.count }}</span>
                                    {% endif %}
                                </h6>
                            </li>
                            {% if stock_notifications.count > 0 %}
                                <!-- Out of Stock Notifications -->
                                {% for notification in stock_notifications.out_of_stock %}
                                <li>
                                    <div class="dropdown-item-text notification-item danger">
                                        <div class="d-flex align-items-start">
                                            <i class="fas fa-times-circle text-danger me-2 mt-1"></i>
                                            <div class="flex-grow-1">
                                                <strong class="text-danger">Out of Stock!</strong><br>
                                                <small>{{ notification.product_name }}</small><br>
                                                <small class="text-muted">Current: {{ notification.in_hand }} units</small>
                                            </div>
                                        </div>
                                    </div>
                                </li>
                                {% endfor %}
                                
                                <!-- Low Stock Notifications -->
                                {% for notification in stock_notifications.low_stock %}
                                <li>
                                    <div class="dropdown-item-text notification-item warning">
                                        <div class="d-flex align-items-start">
                                            <i class="fas fa-exclamation-triangle text-warning me-2 mt-1"></i>
                                            <div class="flex-grow-1">
                                                <strong class="text-warning">Low Stock!</strong><br>
                                                <small>{{ notification.product_name }}</small><br>
                                                <small class="text-muted">Only {{ notification.in_hand }} units left</small>
                                            </div>
                                        </div>
                                    </div>
                                </li>
                                {% endfor %}
                                
                                <li><hr class="dropdown-divider"></li>
                                <li>
                                    <a class="dropdown-item text-center" href="{{ url_for('notifications') }}">
                                        <i class="fas fa-eye me-1"></i>View All Notifications
                                    </a>
                                </li>
                                <li>
                                    <a class="dropdown-item text-center" href="{{ url_for('add_movement') }}">
                                        <i class="fas fa-plus me-1"></i>Add Stock
                                    </a>
                                </li>
                            {% else %}
                                <li>
                                    <div class="dropdown-item-text text-center py-3">
                                        <i class="fas fa-check-circle text-success fa-2x mb-2"></i><br>
                                        <small class="text-muted">All products are well stocked!</small>
                                    </div>
                                </li>
                            {% endif %}
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <main class="container-fluid mt-4">
        <!-- Stock Alert Banner -->
        {% if stock_notifications.count > 0 %}
            <div class="alert alert-warning alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Stock Alert!</strong> 
                {% if stock_notifications.out_of_stock|length > 0 %}
                    {{ stock_notifications.out_of_stock|length }} product(s) are out of stock.
                {% endif %}
                {% if stock_notifications.low_stock|length > 0 %}
                    {{ stock_notifications.low_stock|length }} product(s) are running low.
                {% endif %}
                <a href="{{ url_for('notifications') }}" class="alert-link">View details</a> or 
                <a href="{{ url_for('add_movement') }}" class="alert-link">restock now</a>.
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        {% endif %}

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
    
    <script>
    // Auto-refresh notifications every 30 seconds
    setInterval(function() {
        fetch('/api/notifications')
            .then(response => response.json())
            .then(data => {
                // Update notification badge
                const badge = document.querySelector('.notification-badge');
                if (data.count > 0) {
                    if (badge) {
                        badge.textContent = data.count;
                    } else {
                        // Create badge if it doesn't exist
                        const bellIcon = document.querySelector('#notificationsDropdown');
                        const newBadge = document.createElement('span');
                        newBadge.className = 'notification-badge';
                        newBadge.textContent = data.count;
                        bellIcon.appendChild(newBadge);
                    }
                } else if (badge) {
                    badge.remove();
                }
            })
            .catch(error => console.log('Notification refresh error:', error));
    }, 30000); // 30 seconds
    </script>
</body>
</html>
'''

# Create notifications.html template
notifications_html_content = '''{% extends "base.html" %}

{% block title %}Stock Notifications - Inventory Management{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1><i class="fas fa-bell me-2"></i>Stock Notifications</h1>
        <p class="lead">Monitor your inventory levels and get alerts for products that need restocking.</p>
    </div>
</div>

<div class="row">
    <!-- Notification Summary Cards -->
    <div class="col-md-4 mb-4">
        <div class="card text-white bg-danger">
            <div class="card-body text-center">
                <i class="fas fa-times-circle fa-3x mb-2"></i>
                <h3>{{ notifications.out_of_stock|length }}</h3>
                <h6>Out of Stock</h6>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-4">
        <div class="card text-white bg-warning">
            <div class="card-body text-center">
                <i class="fas fa-exclamation-triangle fa-3x mb-2"></i>
                <h3>{{ notifications.low_stock|length }}</h3>
                <h6>Low Stock</h6>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-4">
        <div class="card text-white bg-success">
            <div class="card-body text-center">
                <i class="fas fa-check-circle fa-3x mb-2"></i>
                <h3>{{ notifications.count }}</h3>
                <h6>Total Alerts</h6>
            </div>
        </div>
    </div>
</div>

{% if notifications.count > 0 %}
    <!-- Out of Stock Section -->
    {% if notifications.out_of_stock|length > 0 %}
    <div class="row mb-4">
        <div class="col-12">
            <div class="card border-danger">
                <div class="card-header bg-danger text-white">
                    <h5 class="mb-0">
                        <i class="fas fa-times-circle me-2"></i>Out of Stock Products - Immediate Action Required!
                        <span class="badge bg-light text-danger ms-2">{{ notifications.out_of_stock|length }}</span>
                    </h5>
                </div>
                <div class="card-body">
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        <strong>Critical Alert:</strong> These products have 0 or negative stock. Consider buying or restocking immediately!
                    </div>
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Product</th>
                                    <th class="text-center">Current Stock</th>
                                    <th class="text-center">Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for item in notifications.out_of_stock %}
                                <tr class="table-danger">
                                    <td>
                                        <strong>{{ item.product_name }}</strong><br>
                                        <small class="text-muted">{{ item.product_id }}</small>
                                    </td>
                                    <td class="text-center">
                                        <span class="badge bg-danger fs-6">{{ item.in_hand }}</span>
                                    </td>
                                    <td class="text-center">
                                        <span class="badge bg-danger">
                                            <i class="fas fa-times-circle me-1"></i>OUT OF STOCK
                                        </span>
                                    </td>
                                    <td>
                                        <a href="{{ url_for('add_movement') }}" 
                                           class="btn btn-sm btn-danger">
                                            <i class="fas fa-plus me-1"></i>Buy/Restock Now
                                        </a>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endif %}

    <!-- Low Stock Section -->
    {% if notifications.low_stock|length > 0 %}
    <div class="row mb-4">
        <div class="col-12">
            <div class="card border-warning">
                <div class="card-header bg-warning text-dark">
                    <h5 class="mb-0">
                        <i class="fas fa-exclamation-triangle me-2"></i>Low Stock Products - Action Needed Soon
                        <span class="badge bg-dark ms-2">{{ notifications.low_stock|length }}</span>
                    </h5>
                </div>
                <div class="card-body">
                    <div class="alert alert-warning">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Warning:</strong> These products are running low. Consider restocking soon to avoid running out.
                    </div>
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Product</th>
                                    <th class="text-center">Current Stock</th>
                                    <th class="text-center">Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for item in notifications.low_stock %}
                                <tr class="table-warning">
                                    <td>
                                        <strong>{{ item.product_name }}</strong><br>
                                        <small class="text-muted">{{ item.product_id }}</small>
                                    </td>
                                    <td class="text-center">
                                        <span class="badge bg-warning fs-6">{{ item.in_hand }}</span>
                                    </td>
                                    <td class="text-center">
                                        <span class="badge bg-warning text-dark">
                                            <i class="fas fa-exclamation-triangle me-1"></i>LOW STOCK
                                        </span>
                                    </td>
                                    <td>
                                        <a href="{{ url_for('add_movement') }}" 
                                           class="btn btn-sm btn-warning">
                                            <i class="fas fa-plus me-1"></i>Restock Soon
                                        </a>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endif %}

    <!-- Quick Actions -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5><i class="fas fa-tools me-2"></i>Quick Actions</h5>
                </div>
                <div class="card-body">
                    <div class="d-flex gap-2 flex-wrap">
                        <a href="{{ url_for('add_movement') }}" class="btn btn-primary">
                            <i class="fas fa-plus me-1"></i>Add Stock Movement
                        </a>
                        <a href="{{ url_for('add_product') }}" class="btn btn-outline-primary">
                            <i class="fas fa-box me-1"></i>Add New Product
                        </a>
                        <a href="{{ url_for('balance_report') }}" class="btn btn-outline-info">
                            <i class="fas fa-chart-bar me-1"></i>View Balance Report
                        </a>
                        <a href="{{ url_for('products') }}" class="btn btn-outline-secondary">
                            <i class="fas fa-list me-1"></i>View All Products
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>

{% else %}
    <!-- No Notifications -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-body text-center py-5">
                    <i class="fas fa-check-circle text-success fa-5x mb-3"></i>
                    <h3 class="text-success">All Products Well Stocked!</h3>
                    <p class="lead text-muted">No stock alerts at this time. All your products have sufficient inventory.</p>
                    <div class="mt-4">
                        <a href="{{ url_for('products') }}" class="btn btn-outline-primary me-2">
                            <i class="fas fa-list me-1"></i>View Products
                        </a>
                        <a href="{{ url_for('balance_report') }}" class="btn btn-primary">
                            <i class="fas fa-chart-bar me-1"></i>View Balance Report
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
{% endif %}
{% endblock %}

{% block scripts %}
<script>
// Auto-refresh page every 60 seconds to show latest notifications
setTimeout(function() {
    window.location.reload();
}, 60000); // 60 seconds

// Add visual feedback for restocking actions
document.addEventListener('DOMContentLoaded', function() {
    const restockButtons = document.querySelectorAll('a[href*="add_movement"]');
    restockButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Redirecting...';
            this.classList.remove('btn-danger', 'btn-warning');
            this.classList.add('btn-secondary');
        });
    });
});
</script>
{% endblock %}
'''

# Save the templates
templates = {
    'templates/base.html': base_html_content,
    'templates/notifications.html': notifications_html_content
}

for filepath, content in templates.items():
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("✅ Updated base.html with comprehensive notification system!")
print("✅ Created notifications.html template with detailed stock alerts!")
print("\nNew Features Added:")
print("🔔 Bell icon in navbar with notification badge")
print("🚨 Stock alert banner on all pages")
print("📱 Dropdown menu showing out-of-stock and low-stock products")
print("⚠️ Dedicated notifications page with actionable alerts")
print("🔄 Auto-refresh notifications every 30 seconds")
print("💡 Clear messaging: 'Consider buying or not have' for out-of-stock products")