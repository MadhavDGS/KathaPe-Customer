"""
Customer Flask Application - Handles all customer-related operations
"""
from appwrite_utils import *
from appwrite_utils import get_ist_isoformat, get_ist_now, upload_bill_image, get_bill_image_url
import os
import json
import datetime
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_from_directory
import uuid
import logging

# Initialize Appwrite client at app startup
try:
    from appwrite_utils import appwrite_client, appwrite_db
    print("✓ Appwrite client initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize Appwrite client: {e}")
    print("Please check your Appwrite configuration in environment variables")
    
    # For development, continue without crashing
    if os.environ.get('FLASK_ENV') == 'development':
        appwrite_client, appwrite_db = None, None
    else:
        # For production, exit if Appwrite is not available
        raise

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File upload configuration
UPLOAD_FOLDER = 'static/uploads/bills'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create the customer Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
customer_app = app

def login_required(f):
    """Decorator to require login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    """Decorator to require customer user type"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'customer':
            flash('Access denied. Customer account required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def format_datetime(value, format='%d %b %Y, %I:%M %p'):
    """Format datetime string"""
    if not value:
        return ""
    try:
        if isinstance(value, str):
            # Parse ISO format datetime
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        else:
            dt = value
        return dt.strftime(format)
    except:
        return str(value)

@customer_app.template_filter('datetime')
def datetime_filter(value, format='%d %b %Y, %I:%M %p'):
    return format_datetime(value, format)

@customer_app.template_filter('currency')
def currency_filter(value):
    """Format a number as currency with proper decimal places"""
    if value is None:
        return "₹0.00"
    try:
        # Convert to float and format with 2 decimal places
        amount = float(value)
        return f"₹{amount:,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"

# Customer routes
@customer_app.route('/')
def index():
    try:
        logger.info("Customer app index route accessed")
        
        # If user is logged in as customer, redirect to dashboard
        if 'user_id' in session and session.get('user_type') == 'customer':
            return redirect(url_for('customer_dashboard'))
        
        # Otherwise redirect to login
        return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"Error in customer index route: {str(e)}")
        return redirect(url_for('login'))



@customer_app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            print(f"DEBUG: Customer login attempt")
            logger.info("Customer user attempting to login")
            phone = request.form.get('phone')
            password = request.form.get('password')
            
            if not phone or not password:
                flash('Please enter both phone number and password', 'error')
                return render_template('login.html')
            
            # Try Appwrite authentication
            try:
                logger.info("Authenticating with Appwrite")
                user_data = login_user(phone, password)
                
                if user_data:
                    # ONLY set session after successful password verification
                    user_id = user_data['$id']
                    user_name = user_data.get('name', f"Customer {phone[-4:]}" if phone and len(phone) > 4 else "Customer User")
                    
                    session['user_id'] = user_id
                    session['user_name'] = user_name
                    session['user_type'] = 'customer'
                    session['phone_number'] = phone
                    session.permanent = True
                    
                    # Get customer details
                    customer_data = get_customer_by_user_id(user_id)
                    
                    if customer_data:
                        session['customer_id'] = customer_data['$id']
                    else:
                        # Create customer record if it doesn't exist
                        customer_id = str(uuid.uuid4())
                        customer_data = {
                            'user_id': user_id,
                            'name': session['user_name'],
                            'phone_number': phone,
                            'created_at': get_ist_isoformat()
                        }
                        
                        customer_result = appwrite_db_instance.create_document(
                            CUSTOMERS_COLLECTION, customer_id, customer_data
                        )
                        
                        if customer_result:
                            session['customer_id'] = customer_id
                        else:
                            flash('Failed to create customer profile', 'error')
                            return render_template('login.html')
                    
                    flash('Successfully logged in!', 'success')
                    return redirect(url_for('customer_dashboard'))
                else:
                    flash('Invalid phone number or password', 'error')
                    return render_template('login.html')
                
            except Exception as e:
                logger.error(f"Appwrite error in customer login: {str(e)}")
                flash('Login service temporarily unavailable. Please try again.', 'error')
                return render_template('login.html')
        
        # GET request
        return render_template('login.html')
        
    except Exception as e:
        logger.critical(f"Critical error in customer login: {str(e)}")
        flash('Login error. Please try again.', 'error')
        return render_template('login.html')

@customer_app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password')
        name = request.form.get('name', f"Customer {phone[-4:]}" if phone and len(phone) >= 4 else "Customer User")
        
        if not phone or not password:
            flash('Please enter both phone number and password', 'error')
            return render_template('register.html')
        
        # Validate phone number - must be exactly 10 digits
        if not phone.isdigit() or len(phone) != 10:
            flash('Phone number must be exactly 10 digits', 'error')
            return render_template('register.html')
        
        try:
            print(f"🔍 Registration attempt - Phone: {phone}, Name: {name}")
            # Use Appwrite registration function
            result = register_user(name, phone, password)
            print(f"📋 Registration result: {result}")
            
            if 'error' in result:
                error_msg = result['error']
                print(f"❌ Registration error: {error_msg}")
                flash(error_msg, 'error')
                return render_template('register.html')
            
            if 'user' in result and 'customer' in result:
                user = result['user']
                customer = result['customer']
                
                print(f"✅ Registration successful! User ID: {user['$id']}, Customer ID: {customer['$id']}")
                
                # Auto-login the user after successful registration
                session['user_id'] = user['$id']
                session['customer_id'] = customer['$id']
                session['user_type'] = 'customer'
                session['phone_number'] = phone
                session['user_name'] = name
                session.permanent = True
                
                flash('Registration successful! Welcome to KhataPe!', 'success')
                return redirect(url_for('customer_dashboard'))
            else:
                error_msg = 'Registration failed. Please try again.'
                print(f"❌ Unexpected result structure: {result}")
                flash(error_msg, 'error')
                
        except Exception as e:
            error_msg = f"Registration error: {str(e)}"
            print(f"❌ Exception during registration: {error_msg}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            flash(f'Registration failed: {str(e)}', 'error')
    
    return render_template('register.html')

@customer_app.route('/dashboard')
@login_required
@customer_required
def customer_dashboard():
    try:
        customer_id = safe_uuid(session.get('customer_id'))
        print(f"DEBUG: Customer dashboard - customer_id from session: {customer_id}")
        
        # Get customer details from Appwrite
        customer = appwrite_db_instance.get_document(CUSTOMERS_COLLECTION, customer_id)
        
        if not customer:
            # Create mock customer object from session data
            customer = {
                '$id': customer_id,
                'name': session.get('user_name', 'Your Name'),
                'phone_number': session.get('phone_number', '0000000000')
            }
            print(f"DEBUG: Using mock customer data: {customer['name']}")
        else:
            print(f"DEBUG: Found customer in database: {customer.get('name', 'Unknown')}")
        
        # Get customer's credit relationships with businesses
        credit_relationships = []
        recent_transactions = []
        total_balance = 0
        
        try:
            # Get credit relationships
            credits_data = get_customer_credits(customer_id)
            print(f"DEBUG: Found {len(credits_data)} credit relationships for customer {customer_id}")
            
            for credit in credits_data:
                business_id = credit['business_id']
                
                # Get business details
                business = appwrite_db_instance.get_document(BUSINESSES_COLLECTION, business_id)
                business_name = business.get('name', 'Unknown Business') if business else 'Unknown Business'
                
                # Calculate actual balance from transactions
                transactions_data = get_customer_transactions(customer_id, business_id)
                credit_received = sum([float(tx.get('amount', 0)) for tx in transactions_data if tx.get('transaction_type') == 'credit'])
                payments_made = sum([float(tx.get('amount', 0)) for tx in transactions_data if tx.get('transaction_type') == 'payment'])
                actual_balance = credit_received - payments_made
                
                print(f"DEBUG: Credit relationship - Business: {business_name}, Actual Balance: {actual_balance}")
                credit_relationships.append({
                    'id': business_id,  # Template expects 'id' not 'business_id'
                    'business_id': business_id,
                    'name': business_name,  # Template expects 'name' not 'business_name'
                    'business_name': business_name,
                    'current_balance': actual_balance,
                    'updated_at': credit.get('updated_at', credit.get('$updatedAt', ''))
                })
                total_balance += actual_balance
            
            # Get recent transactions (last 10)
            all_transactions = get_customer_transactions(customer_id)
            # Sort by created_at, newest first
            all_transactions.sort(key=lambda x: x.get('created_at', x.get('$createdAt', '')), reverse=True)
            
            for tx in all_transactions[:10]:  # Limit to 10 most recent
                business_id = tx.get('business_id')
                business = appwrite_db_instance.get_document(BUSINESSES_COLLECTION, business_id) if business_id else None
                business_name = business.get('name', 'Unknown Business') if business else 'Unknown Business'
                
                recent_transactions.append({
                    'id': tx.get('$id', tx.get('id')),
                    'amount': float(tx.get('amount', 0)),
                    'transaction_type': tx.get('transaction_type'),
                    'notes': tx.get('notes', ''),
                    'created_at': tx.get('created_at', tx.get('$createdAt', '')),
                    'business_name': business_name
                })
            
        except Exception as e:
            print(f"Appwrite error in customer dashboard: {str(e)}")
            # Use fallback empty data
        
        summary = {
            'total_balance': total_balance,
            'business_count': len(credit_relationships)
        }
        
        return render_template('customer/dashboard.html',
                             customer=customer,
                             summary=summary,
                             businesses=credit_relationships,  # Pass as 'businesses' for template
                             credit_relationships=credit_relationships,
                             recent_transactions=recent_transactions)
                             
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('login'))

@customer_app.route('/businesses')
@login_required
@customer_required
def businesses():
    customer_id = safe_uuid(session.get('customer_id'))
    
    # Get all businesses where this customer has credit using Appwrite
    customer_credits = get_customer_credits(customer_id)
    
    # Gather business details
    businesses = []
    for credit in customer_credits:
        business_id = credit.get('business_id')
        if business_id:
            business = appwrite_db_instance.get_document(BUSINESSES_COLLECTION, business_id)
            if business:
                # Calculate actual balance from transactions
                transactions = get_customer_transactions(customer_id, business_id)
                credit_received = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'credit'])
                payments_made = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'payment'])
                actual_balance = credit_received - payments_made
                
                business['current_balance'] = actual_balance
                businesses.append(business)
    
    return render_template('customer/businesses.html', businesses=businesses)

@customer_app.route('/business/<business_id>')
@login_required
@customer_required
def business_view(business_id):
    customer_id = safe_uuid(session.get('customer_id'))
    business_id = safe_uuid(business_id)
    
    # Get business details from Appwrite
    business = appwrite_db_instance.get_document(BUSINESSES_COLLECTION, business_id)
    if not business:
        flash('Business not found', 'error')
        return redirect(url_for('customer_dashboard'))
    
    # Get credit relationship
    credits = appwrite_db_instance.list_documents(
        CUSTOMER_CREDITS_COLLECTION,
        [
            Query.equal('business_id', business_id),
            Query.equal('customer_id', customer_id)
        ]
    )
    credit = credits[0] if credits else {}
    
    # Get transaction history with this business
    transactions = get_customer_transactions(customer_id, business_id)
    
    # Sort transactions by date, newest first
    transactions.sort(key=lambda x: x.get('created_at', x.get('$createdAt', '')), reverse=True)
    
    # Calculate totals
    credit_received = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'credit'])
    payments_made = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'payment'])
    
    # Calculate current balance
    current_balance = credit_received - payments_made  # Positive means customer owes money
    
    return render_template('customer/business_view.html',
                         business=business,
                         credit=credit,
                         transactions=transactions,
                         credit_received=credit_received,
                         payments_made=payments_made,
                         current_balance=current_balance)

@customer_app.route('/select_business', methods=['GET', 'POST'])
@login_required
@customer_required
def select_business():
    if request.method == 'POST':
        access_pin = request.form.get('access_pin')
        
        if not access_pin:
            flash('Please enter the business access PIN', 'error')
            return render_template('customer/select_business.html')
        
        try:
            # Find business by access PIN using Appwrite
            business = get_business_by_access_pin(access_pin)
            
            if business:
                business_id = business['$id']
                customer_id = safe_uuid(session.get('customer_id'))
                
                # Check if credit relationship already exists
                existing_credits = appwrite_db_instance.list_documents(
                    CUSTOMER_CREDITS_COLLECTION,
                    [
                        Query.equal('business_id', business_id),
                        Query.equal('customer_id', customer_id)
                    ]
                )
                
                if not existing_credits:
                    # Create new credit relationship
                    credit_result = create_customer_credit_relationship(customer_id, business_id)
                    if credit_result:
                        flash(f'Successfully connected to {business["name"]}!', 'success')
                    else:
                        flash('Failed to create connection. Please try again.', 'error')
                        return render_template('customer/select_business.html')
                else:
                    flash(f'You are already connected to {business["name"]}', 'info')
                
                return redirect(url_for('business_view', business_id=business_id))
            else:
                flash('Invalid access PIN. Please check with the business.', 'error')
                
        except Exception as e:
            flash(f'Error connecting to business: {str(e)}', 'error')
    
    return render_template('customer/select_business.html')

@customer_app.route('/scan_qr')
@login_required
@customer_required
def scan_qr():
    # This would typically integrate with a QR code scanner
    # For now, redirect to manual business selection
    flash('QR code scanning feature coming soon! Please use PIN instead.', 'info')
    return redirect(url_for('select_business'))

@customer_app.route('/profile', methods=['GET', 'POST'])
@login_required
@customer_required
def customer_profile():
    customer_id = safe_uuid(session.get('customer_id'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        
        try:
            update_data = {}
            if name:
                update_data['name'] = name
                session['user_name'] = name
            if phone:
                update_data['phone_number'] = phone
                session['phone_number'] = phone
            if email:
                update_data['email'] = email
            
            if update_data:
                query_table('customers', query_type='update',
                           data=update_data, filters=[('id', 'eq', customer_id)])
                flash('Profile updated successfully!', 'success')
                
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')
    
    # Get current customer details
    customer_response = query_table('customers', filters=[('id', 'eq', customer_id)])
    customer = customer_response.data[0] if customer_response and customer_response.data else {
        'name': session.get('user_name', 'Your Name'),
        'phone_number': session.get('phone_number', '0000000000'),
        'email': ''
    }
    
    return render_template('customer/profile.html', customer=customer)

@customer_app.route('/transaction/<transaction_type>/<business_id>', methods=['GET', 'POST'])
@login_required
@customer_required
def customer_transaction(transaction_type, business_id):
    customer_id = safe_uuid(session.get('customer_id'))
    business_id = safe_uuid(business_id)
    
    print(f"DEBUG: Transaction route called with customer_id: {customer_id}, business_id: {business_id}")
    
    # Validate that customer exists using Appwrite
    customer_check = appwrite_db_instance.get_document(CUSTOMERS_COLLECTION, customer_id)
    if not customer_check:
        print(f"ERROR: Customer {customer_id} not found in database")
        flash('Customer account not found. Please log in again.', 'error')
        return redirect(url_for('login'))
    
    # Validate that business exists using Appwrite
    business_check = appwrite_db_instance.get_document(BUSINESSES_COLLECTION, business_id)
    if not business_check:
        print(f"ERROR: Business {business_id} not found in database")
        flash('Business not found', 'error')
        return redirect(url_for('customer_dashboard'))
    
    # Validate transaction type
    if transaction_type not in ['credit', 'payment']:
        flash('Invalid transaction type', 'error')
        return redirect(url_for('business_view', business_id=business_id))
    
    # Get business details
    business = business_check
    
    if not business:
        flash('Business not found', 'error')
        return redirect(url_for('customer_dashboard'))
    
    # Calculate current balance for pre-filling payment amount
    transactions = get_customer_transactions(customer_id, business_id)
    
    # Calculate current balance
    credit_received = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'credit'])
    payments_made = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'payment'])
    current_balance = credit_received - payments_made  # Positive means customer owes money
    
    if request.method == 'POST':
        amount = request.form.get('amount')
        notes = request.form.get('notes', '')
        
        # Handle file upload for bill photo  
        bill_file_id = None
        if 'bill_photo' in request.files:
            file = request.files['bill_photo']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    try:
                        # Read file data
                        file.seek(0)  # Reset file pointer
                        file_data = file.read()
                        
                        # Check file size (limit to 10MB)
                        if len(file_data) > 10 * 1024 * 1024:
                            flash('Image file too large. Please choose a file smaller than 10MB.', 'error')
                            return render_template('customer/transaction.html', 
                                                 business=business, 
                                                 transaction_type=transaction_type,
                                                 current_balance=current_balance)
                        
                        # Optional: Compress image for better storage efficiency
                        from PIL import Image
                        import io
                        
                        # Open and optimize the image
                        try:
                            original_image = Image.open(io.BytesIO(file_data))
                            
                            # Convert to RGB if necessary (for JPEG compatibility)
                            if original_image.mode in ('RGBA', 'LA', 'P'):
                                original_image = original_image.convert('RGB')
                            
                            # Resize if too large (max 1200px width/height)
                            max_size = 1200
                            if original_image.width > max_size or original_image.height > max_size:
                                original_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                            
                            # Compress and save as JPEG
                            output = io.BytesIO()
                            original_image.save(output, format='JPEG', quality=85, optimize=True)
                            file_data = output.getvalue()
                            filename = secure_filename(file.filename)
                            if not filename.lower().endswith('.jpg'):
                                filename = filename.rsplit('.', 1)[0] + '.jpg'
                            
                        except Exception as img_error:
                            filename = secure_filename(file.filename)
                        
                        # Generate a temporary transaction ID for the upload
                        temp_transaction_id = str(uuid.uuid4())
                        
                        # Upload to Cloudinary
                        bill_file_id = upload_bill_image(file_data, filename, temp_transaction_id)
                        
                        if bill_file_id:
                            flash('Bill photo uploaded successfully!', 'success')
                        else:
                            flash('Failed to upload bill photo, but transaction will continue', 'warning')
                        
                    except Exception as e:
                        print(f"ERROR: Failed to process bill photo: {e}")
                        flash('Failed to process bill photo, but transaction will continue', 'warning')
                else:
                    flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.', 'error')
                    return render_template('customer/transaction.html', 
                                         business=business, 
                                         transaction_type=transaction_type,
                                         current_balance=current_balance)
        
        try:
            amount = float(amount) if amount else 0
            if amount <= 0:
                flash('Please enter a valid amount', 'error')
                return render_template('customer/transaction.html', 
                                     business=business, 
                                     transaction_type=transaction_type,
                                     current_balance=current_balance)
            
            # Debug logging
            print(f"DEBUG: Creating transaction - customer_id: {customer_id}, business_id: {business_id}, type: {transaction_type}, amount: {amount}")
            
            # Create transaction record
            transaction_data = {
                'business_id': business_id,
                'customer_id': customer_id,
                'transaction_type': transaction_type,
                'amount': amount,
                'notes': notes,
                'created_at': get_ist_isoformat()
            }
            
            # Add bill photo file ID if available
            if bill_file_id:
                transaction_data['receipt_image_url'] = bill_file_id
            
            print(f"DEBUG: Transaction data: {transaction_data}")
            
            # Insert transaction using Appwrite
            result = create_transaction(transaction_data)
            
            print(f"DEBUG: Insert result: {result}")
            
            if result:
                # Calculate new balance
                transactions = get_customer_transactions(customer_id, business_id)
                credit_received = sum([float(tx.get('amount', 0)) for tx in transactions if tx.get('transaction_type') == 'credit'])
                payments_made = sum([float(tx.get('amount', 0)) for tx in transactions if tx.get('transaction_type') == 'payment'])
                new_balance = credit_received - payments_made
                
                # Update customer credits
                update_result = update_customer_credit(customer_id, business_id, new_balance)
                print(f"DEBUG: Credit update result: {update_result}")
                
                action = 'taken credit of' if transaction_type == 'credit' else 'made payment of'
                flash(f'Successfully {action} ₹{amount}', 'success')
                return redirect(url_for('business_view', business_id=business_id))
            else:
                print("ERROR: Failed to insert transaction")
                flash('Failed to record transaction. Please try again.', 'error')
                
        except ValueError:
            flash('Please enter a valid amount', 'error')
        except Exception as e:
            flash(f'Error processing transaction: {str(e)}', 'error')
    
    return render_template('customer/transaction.html', 
                         business=business, 
                         transaction_type=transaction_type,
                         current_balance=current_balance)

@customer_app.route('/phonepe_qr_payment/<business_id>', methods=['POST'])
@login_required
@customer_required
def phonepe_qr_payment(business_id):
    """Redirect to PhonePe QR scanner for payment"""
    try:
        amount = float(request.form.get('amount', 0))
        notes = request.form.get('notes', '')
        
        if amount <= 0:
            return jsonify({'success': False, 'error': 'Please enter a valid amount'}), 400
        
        # Get business details
        business_response = query_table('businesses', filters=[('id', 'eq', business_id)])
        business = business_response.data[0] if business_response and business_response.data else {}
        
        if not business:
            return jsonify({'success': False, 'error': 'Business not found'}), 400
        
        # Get customer details
        customer_id = safe_uuid(session.get('customer_id'))
        customer_response = query_table('customers', filters=[('id', 'eq', customer_id)])
        customer = customer_response.data[0] if customer_response and customer_response.data else {}
        
        # Create pending transaction record immediately
        transaction_id = str(uuid.uuid4())
        pending_transaction_data = {
            'id': transaction_id,
            'business_id': business_id,
            'customer_id': customer_id,
            'transaction_type': 'payment',
            'amount': amount,
            'notes': notes,
            'status': 'pending_business_approval',
            'created_at': get_ist_isoformat()
        }
        
        # Insert into pending_transactions table (we'll need to create this table)
        try:
            # For now, store in session and we'll create proper pending transactions handling
            session[f'pending_payment_{transaction_id}'] = {
                'transaction_id': transaction_id,
                'business_id': business_id,
                'business_name': business.get('name', 'Business'),
                'customer_id': customer_id,
                'customer_name': customer.get('name', session.get('user_name', 'Customer')),
                'amount': amount,
                'notes': notes,
                'created_at': get_ist_isoformat(),
                'status': 'pending_business_approval'
            }
        except Exception as e:
            print(f"Error storing pending transaction: {e}")
        
        # Create PhonePe QR scanner deep link
        phonepe_url = f"phonepe://scan?amount={amount}&merchantName={business.get('name', 'Business')}"
        
        return jsonify({
            'success': True,
            'phonepe_url': phonepe_url,
            'transaction_id': transaction_id,
            'amount': amount,
            'business_name': business.get('name', 'Business'),
            'message': f"Payment request sent! Waiting for {business.get('name', 'Business')} to confirm your ₹{amount} payment.",
            'status': 'pending_business_approval'
        })
        
    except Exception as e:
        print(f"Error initiating PhonePe QR payment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@customer_app.route('/complete_phonepe_payment/<transaction_id>', methods=['POST'])
@login_required
@customer_required
def complete_phonepe_payment(transaction_id):
    """Complete PhonePe payment and directly add to transactions"""
    try:
        # Get pending payment from session
        pending_payment = session.get(f'pending_payment_{transaction_id}')
        
        if not pending_payment:
            return jsonify({'success': False, 'error': 'Invalid transaction'}), 400
        
        # Directly add payment to transactions table
        transaction_data = {
            'id': str(uuid.uuid4()),
            'customer_id': pending_payment['customer_id'],
            'business_id': pending_payment['business_id'],
            'transaction_type': 'payment',
            'amount': pending_payment['amount'],
            'notes': pending_payment.get('notes', 'PhonePe QR Payment'),
            'created_at': get_ist_isoformat()
        }
        
        # Insert transaction into database
        insert_result = query_table('transactions', query_type='insert', data=transaction_data)
        
        if not insert_result:
            return jsonify({'success': False, 'error': 'Failed to add transaction'}), 500
        
        # Remove pending payment from session
        del session[f'pending_payment_{transaction_id}']
        
        return jsonify({
            'success': True,
            'message': f'Payment of ₹{pending_payment["amount"]} completed successfully!',
            'status': 'confirmed',
            'redirect_url': url_for('customer_dashboard')
        })
            
    except Exception as e:
        print(f"Error completing PhonePe payment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@customer_app.route('/pending_payments')
@login_required
@customer_required
def pending_payments():
    """Show customer's pending payments"""
    customer_id = safe_uuid(session.get('customer_id'))
    
    # Get all pending payments for this customer from session
    pending_payments = []
    for key, value in session.items():
        if key.startswith('pending_payment_') and isinstance(value, dict):
            if value.get('customer_id') == customer_id:
                pending_payments.append(value)
    
    # Sort by creation date, newest first
    pending_payments.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return render_template('customer/pending_payments.html', pending_payments=pending_payments)

@customer_app.route('/transaction_history')
@login_required
@customer_required
def transaction_history():
    customer_id = safe_uuid(session.get('customer_id'))
    
    # Get all transactions for this customer
    transactions_response = query_table('transactions', filters=[('customer_id', 'eq', customer_id)])
    transactions = transactions_response.data if transactions_response and transactions_response.data else []
    
    # Enrich transactions with business names
    for transaction in transactions:
        business_id = transaction.get('business_id')
        if business_id:
            business_response = query_table('businesses', filters=[('id', 'eq', business_id)])
            if business_response and business_response.data:
                transaction['business_name'] = business_response.data[0].get('name', 'Unknown Business')
            else:
                transaction['business_name'] = 'Unknown Business'
    
    # Sort by date, newest first
    transactions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return render_template('customer/transaction_history.html', transactions=transactions)

@customer_app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@customer_app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@customer_app.route('/health')
def health_check():
    """Health check endpoint for monitoring and load balancers"""
    try:
        # Simple health check - you can add database connectivity check here
        return jsonify({
            'status': 'healthy',
            'service': 'KathaPe Customer App',
            'timestamp': get_ist_isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': get_ist_isoformat()
        }), 500

@customer_app.route('/uploads/bills/<filename>')
@login_required
@customer_required
def uploaded_bill(filename):
    """Serve uploaded bill images (protected route) - DEPRECATED"""
    return "Image not found - please use new database storage", 404

@customer_app.route('/debug/bill/<transaction_id>')
@login_required
def debug_bill_info(transaction_id):
    """Debug route to check bill photo information"""
    try:
        # Get the transaction with bill photo data
        transaction_result = query_table('transactions', 
                                       filters=[('id', 'eq', transaction_id)])
        
        if not transaction_result or not transaction_result.data:
            return f"Transaction {transaction_id} not found in database", 404
            
        transaction = transaction_result.data[0]
        bill_photo_data = transaction.get('receipt_image_url')
        
        debug_info = {
            'transaction_id': transaction_id,
            'has_bill_photo': bool(bill_photo_data),
            'bill_data_length': len(bill_photo_data) if bill_photo_data else 0,
            'bill_data_preview': bill_photo_data[:50] + '...' if bill_photo_data and len(bill_photo_data) > 50 else bill_photo_data,
            'transaction_amount': transaction.get('amount'),
            'transaction_date': transaction.get('created_at')
        }
        
        return f"<pre>{json.dumps(debug_info, indent=2)}</pre>"
        
    except Exception as e:
        return f"Error: {str(e)}", 500

@customer_app.route('/debug/cloudinary')
def debug_cloudinary():
    """Debug Cloudinary configuration on Render"""
    import cloudinary
    import cloudinary.utils
    
    debug_info = {
        'environment_variables': {
            'CLOUDINARY_CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME', 'NOT_SET'),
            'CLOUDINARY_API_KEY': os.getenv('CLOUDINARY_API_KEY', 'NOT_SET'), 
            'CLOUDINARY_API_SECRET': 'SET' if os.getenv('CLOUDINARY_API_SECRET') else 'NOT_SET'
        },
        'test_url_generation': None
    }
    
    # Test URL generation
    try:
        test_url = cloudinary.utils.cloudinary_url("test_image")[0]
        debug_info['test_url_generation'] = test_url
    except Exception as e:
        debug_info['test_url_generation'] = f"ERROR: {str(e)}"
    
    return f"<pre>{json.dumps(debug_info, indent=2)}</pre>"

# API endpoints for mobile app integration
@customer_app.route('/api/businesses')
@login_required
@customer_required
def api_businesses():
    customer_id = safe_uuid(session.get('customer_id'))
    
    try:
        # Get businesses with credit relationships
        credits_response = query_table('customer_credits', filters=[('customer_id', 'eq', customer_id)])
        customer_credits = credits_response.data if credits_response and credits_response.data else []
        
        businesses = []
        for credit in customer_credits:
            business_id = credit.get('business_id')
            if business_id:
                business_detail = query_table('businesses', filters=[('id', 'eq', business_id)])
                if business_detail and business_detail.data:
                    business = business_detail.data[0]
                    businesses.append({
                        'id': business['id'],
                        'name': business['name'],
                        'description': business.get('description', ''),
                        'current_balance': float(credit.get('current_balance', 0))
                    })
        
        return jsonify({'success': True, 'businesses': businesses})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@customer_app.route('/api/transactions/<business_id>')
@login_required
@customer_required
def api_transactions(business_id):
    customer_id = safe_uuid(session.get('customer_id'))
    business_id = safe_uuid(business_id)
    
    try:
        transactions_response = query_table('transactions',
                                          filters=[('business_id', 'eq', business_id),
                                                  ('customer_id', 'eq', customer_id)])
        transactions = transactions_response.data if transactions_response and transactions_response.data else []
        
        # Format transactions for API response
        api_transactions = []
        for tx in transactions:
            api_transactions.append({
                'id': tx['id'],
                'amount': float(tx['amount']) if tx['amount'] else 0,
                'type': tx['transaction_type'],
                'notes': tx.get('notes', ''),
                'date': tx['created_at']
            })
        
        return jsonify({'success': True, 'transactions': api_transactions})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@customer_app.route('/transaction/bill/<transaction_id>')
@login_required
def serve_bill_image(transaction_id):
    """Serve bill images from Cloudinary"""
    try:
        # Get the transaction to find the Cloudinary public_id
        db = AppwriteDB()
        transaction = db.get_document(TRANSACTIONS_COLLECTION, transaction_id)
        
        if not transaction:
            return "Transaction not found", 404
            
        # Check if user has permission to view this transaction
        customer_id = session.get('customer_id')
        if transaction.get('customer_id') != customer_id:
            return "Unauthorized", 403
            
        # Get the Cloudinary public_id from receipt_image_url field
        public_id = transaction.get('receipt_image_url')
        if not public_id:
            return "No bill image found for this transaction", 404
            
        # Generate Cloudinary URL
        bill_url = get_bill_image_url(public_id)
        if not bill_url:
            return "Failed to generate bill image URL", 500
            
        # Redirect to Cloudinary URL
        return redirect(bill_url)
        
    except Exception as e:
        print(f"ERROR: Failed to serve bill image: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return f"Error serving bill image: {str(e)}", 500

# Run the application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))  # Render uses PORT env var
    customer_app.run(debug=False, host='0.0.0.0', port=port)
