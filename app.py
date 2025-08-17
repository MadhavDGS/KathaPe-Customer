"""
Customer Flask Application - Handles all customer-related operations
"""
from common_utils import *
from common_utils import get_ist_isoformat, get_ist_now
import os
import json
import datetime
from werkzeug.utils import secure_filename

# File upload configuration
UPLOAD_FOLDER = 'static/uploads/bills'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create the customer Flask app
customer_app = create_app('KhataPe-Customer')

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
            
            # Emergency login disabled for security - all logins must authenticate with database
            # Do NOT set session data before authentication!
            
            # Try database authentication
            try:
                logger.info("Testing database connection for customer login")
                conn = psycopg2.connect(EXTERNAL_DATABASE_URL, connect_timeout=5)
                
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    # Query customer user
                    cursor.execute("SELECT id, name, password FROM users WHERE phone_number = %s AND user_type = 'customer' LIMIT 1", [phone])
                    user_data = cursor.fetchone()
                    
                    if user_data and user_data['password'] == password:
                        # ONLY set session after successful password verification
                        user_id = user_data['id']
                        user_name = user_data.get('name', f"Customer {phone[-4:]}" if phone and len(phone) > 4 else "Customer User")
                        
                        session['user_id'] = user_id
                        session['user_name'] = user_name
                        session['user_type'] = 'customer'
                        session['phone_number'] = phone
                        session.permanent = True
                        
                        # Get customer details
                        cursor.execute("SELECT id FROM customers WHERE user_id = %s LIMIT 1", [user_id])
                        customer_data = cursor.fetchone()
                        
                        if customer_data:
                            session['customer_id'] = customer_data['id']
                        else:
                            # Create customer record if it doesn't exist
                            customer_id = str(uuid.uuid4())
                            cursor.execute("""
                                INSERT INTO customers (id, user_id, name, phone_number, created_at)
                                VALUES (%s, %s, %s, %s, %s)
                            """, [customer_id, user_id, session['user_name'], phone, get_ist_isoformat()])
                            conn.commit()
                            session['customer_id'] = customer_id
                        
                        conn.close()
                        flash('Successfully logged in!', 'success')
                        return redirect(url_for('customer_dashboard'))
                    else:
                        conn.close()
                        flash('Invalid phone number or password', 'error')
                        return render_template('login.html')
                
            except Exception as e:
                logger.error(f"Database error in customer login: {str(e)}")
                # Don't allow fallback login - database authentication required
                flash('Login service temporarily unavailable. Please try again.', 'error')
                return render_template('login.html')
        
        # GET request
        return render_template('login.html')
        
    except Exception as e:
        logger.critical(f"Critical error in customer login: {str(e)}")
        # Don't allow emergency fallback - require proper authentication
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
            # Check if phone number already exists
            check_query = "SELECT id FROM users WHERE phone_number = %s"
            existing_user = execute_query(check_query, [phone], fetch_one=True)
            
            if existing_user:
                flash('Phone number already registered', 'error')
                return render_template('register.html')
            
            # Create user and customer records
            user_id = str(uuid.uuid4())
            customer_id = str(uuid.uuid4())
            
            # Create user record
            user_query = """
                INSERT INTO users (id, name, phone_number, user_type, password, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            user_result = execute_query(user_query, [user_id, name, phone, 'customer', password, get_ist_isoformat()], fetch_one=True)
            
            if user_result:
                # Create customer record
                customer_query = """
                    INSERT INTO customers (id, user_id, name, phone_number, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """
                execute_query(customer_query, [customer_id, user_id, name, phone, get_ist_isoformat()])
                
                # Auto-login the user after successful registration
                session['user_id'] = user_id
                session['customer_id'] = customer_id  # Add this line!
                session['user_type'] = 'customer'
                session['phone_number'] = phone
                session['name'] = name
                
                flash('Registration successful! Welcome to KhataPe!', 'success')
                return redirect(url_for('customer_dashboard'))
            else:
                flash('Registration failed. Please try again.', 'error')
                
        except Exception as e:
            print(f"Registration error: {str(e)}")
            flash(f'Registration failed: {str(e)}', 'error')
    
    return render_template('register.html')

@customer_app.route('/dashboard')
@login_required
@customer_required
def customer_dashboard():
    try:
        customer_id = safe_uuid(session.get('customer_id'))
        print(f"DEBUG: Customer dashboard - customer_id from session: {customer_id}")
        
        # Get customer details
        customer_response = query_table('customers', filters=[('id', 'eq', customer_id)])
        
        if customer_response and customer_response.data:
            customer = customer_response.data[0]
            print(f"DEBUG: Found customer in database: {customer.get('name', 'Unknown')}")
        else:
            # Create mock customer object from session data
            customer = {
                'id': customer_id,
                'name': session.get('user_name', 'Your Name'),
                'phone_number': session.get('phone_number', '0000000000')
            }
            print(f"DEBUG: Using mock customer data: {customer['name']}")
        
        # Get customer's credit relationships with businesses
        credit_relationships = []
        recent_transactions = []
        total_balance = 0
        
        try:
            # Connect directly to database
            conn = psycopg2.connect(EXTERNAL_DATABASE_URL)
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # Get credit relationships with businesses
                cursor.execute("""
                    SELECT cc.*, b.name as business_name, b.access_pin
                    FROM customer_credits cc
                    JOIN businesses b ON cc.business_id = b.id
                    WHERE cc.customer_id = %s
                    ORDER BY cc.updated_at DESC
                """, [customer_id])
                
                credits_data = cursor.fetchall()
                print(f"DEBUG: Found {len(credits_data)} credit relationships for customer {customer_id}")
                for credit in credits_data:
                    business_id = credit['business_id']
                    
                    # Calculate actual balance from transactions (same method as business view)
                    cursor.execute("""
                        SELECT amount, transaction_type 
                        FROM transactions 
                        WHERE business_id = %s AND customer_id = %s
                    """, [business_id, customer_id])
                    
                    transactions_data = cursor.fetchall()
                    credit_received = sum([float(tx['amount']) for tx in transactions_data if tx['transaction_type'] == 'credit'])
                    payments_made = sum([float(tx['amount']) for tx in transactions_data if tx['transaction_type'] == 'payment'])
                    actual_balance = credit_received - payments_made
                    
                    print(f"DEBUG: Credit relationship - Business: {credit['business_name']}, Actual Balance: {actual_balance}")
                    credit_relationships.append({
                        'id': credit['business_id'],  # Template expects 'id' not 'business_id'
                        'business_id': credit['business_id'],
                        'name': credit['business_name'],  # Template expects 'name' not 'business_name'
                        'business_name': credit['business_name'],
                        'current_balance': actual_balance,
                        'updated_at': credit['updated_at']
                    })
                    total_balance += actual_balance
                
                # Get recent transactions
                cursor.execute("""
                    SELECT t.*, b.name as business_name
                    FROM transactions t
                    JOIN businesses b ON t.business_id = b.id
                    WHERE t.customer_id = %s
                    ORDER BY t.created_at DESC
                    LIMIT 10
                """, [customer_id])
                
                transactions_data = cursor.fetchall()
                for tx in transactions_data:
                    recent_transactions.append({
                        'id': tx['id'],
                        'amount': float(tx['amount']) if tx['amount'] else 0,
                        'transaction_type': tx['transaction_type'],
                        'notes': tx.get('notes', ''),
                        'created_at': tx['created_at'],
                        'business_name': tx.get('business_name', 'Unknown Business')
                    })
            
            conn.close()
            
        except Exception as e:
            print(f"Database error in customer dashboard: {str(e)}")
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
    
    # Get all businesses where this customer has credit
    credits_response = query_table('customer_credits', filters=[('customer_id', 'eq', customer_id)])
    customer_credits = credits_response.data if credits_response and credits_response.data else []
    
    # Gather business details
    businesses = []
    for credit in customer_credits:
        business_id = credit.get('business_id')
        if business_id:
            business_detail = query_table('businesses', filters=[('id', 'eq', business_id)])
            if business_detail and business_detail.data:
                business = business_detail.data[0]
                
                # Calculate actual balance from transactions (same method as business view)
                transactions_response = query_table('transactions',
                                                  filters=[('business_id', 'eq', business_id),
                                                          ('customer_id', 'eq', customer_id)])
                transactions = transactions_response.data if transactions_response and transactions_response.data else []
                
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
    
    # Get business details
    business_response = query_table('businesses', filters=[('id', 'eq', business_id)])
    business = business_response.data[0] if business_response and business_response.data else {}
    
    # Get credit relationship
    credit_response = query_table('customer_credits', 
                                filters=[('business_id', 'eq', business_id),
                                        ('customer_id', 'eq', customer_id)])
    credit = credit_response.data[0] if credit_response and credit_response.data else {}
    
    # Get transaction history with this business
    transactions_response = query_table('transactions',
                                      filters=[('business_id', 'eq', business_id),
                                              ('customer_id', 'eq', customer_id)])
    transactions = transactions_response.data if transactions_response and transactions_response.data else []
    
    # Sort transactions by date, newest first
    transactions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
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
            # Find business by access PIN
            business_response = query_table('businesses', filters=[('access_pin', 'eq', access_pin)])
            
            if business_response and business_response.data:
                business = business_response.data[0]
                business_id = business['id']
                customer_id = safe_uuid(session.get('customer_id'))
                
                # Check if credit relationship already exists
                existing_credit = query_table('customer_credits',
                                            filters=[('business_id', 'eq', business_id),
                                                   ('customer_id', 'eq', customer_id)])
                
                if not existing_credit or not existing_credit.data:
                    # Create new credit relationship
                    credit_data = {
                        'id': str(uuid.uuid4()),
                        'business_id': business_id,
                        'customer_id': customer_id,
                        'current_balance': 0,
                        'created_at': get_ist_isoformat(),
                        'updated_at': get_ist_isoformat()
                    }
                    
                    query_table('customer_credits', query_type='insert', data=credit_data)
                    flash(f'Successfully connected to {business["name"]}!', 'success')
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
    
    # Validate that customer exists
    customer_check = query_table('customers', filters=[('id', 'eq', customer_id)])
    if not customer_check or not customer_check.data:
        print(f"ERROR: Customer {customer_id} not found in database")
        flash('Customer account not found. Please log in again.', 'error')
        return redirect(url_for('login'))
    
    # Validate that business exists  
    business_check = query_table('businesses', filters=[('id', 'eq', business_id)])
    if not business_check or not business_check.data:
        print(f"ERROR: Business {business_id} not found in database")
        flash('Business not found', 'error')
        return redirect(url_for('customer_dashboard'))
    
    # Validate transaction type
    if transaction_type not in ['credit', 'payment']:
        flash('Invalid transaction type', 'error')
        return redirect(url_for('business_view', business_id=business_id))
    
    # Get business details
    business_response = query_table('businesses', filters=[('id', 'eq', business_id)])
    business = business_response.data[0] if business_response and business_response.data else {}
    
    if not business:
        flash('Business not found', 'error')
        return redirect(url_for('customer_dashboard'))
    
    # Calculate current balance for pre-filling payment amount
    transactions_response = query_table('transactions',
                                      filters=[('business_id', 'eq', business_id),
                                              ('customer_id', 'eq', customer_id)])
    transactions = transactions_response.data if transactions_response and transactions_response.data else []
    
    # Calculate current balance
    credit_received = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'credit'])
    payments_made = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'payment'])
    current_balance = credit_received - payments_made  # Positive means customer owes money
    
    if request.method == 'POST':
        amount = request.form.get('amount')
        notes = request.form.get('notes', '')
        
        # Handle file upload for bill photo
        bill_photo_data = None
        if 'bill_photo' in request.files:
            file = request.files['bill_photo']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    try:
                        # Read file data
                        file.seek(0)  # Reset file pointer
                        file_data = file.read()
                        
                        # Compress image before storing in database
                        from PIL import Image
                        import io
                        import base64
                        
                        # Open and compress the image
                        original_image = Image.open(io.BytesIO(file_data))
                        
                        # Convert to RGB if necessary (for JPEG compatibility)
                        if original_image.mode in ('RGBA', 'LA', 'P'):
                            original_image = original_image.convert('RGB')
                        
                        # Start with high quality and reduce if needed
                        for quality in [85, 70, 55, 40]:
                            output = io.BytesIO()
                            original_image.save(output, format='JPEG', quality=quality, optimize=True)
                            compressed_data = output.getvalue()
                            
                            # If compressed size is acceptable, break
                            if len(compressed_data) < 500 * 1024:  # 500KB limit for database
                                break
                            
                            # If still too large, resize image
                            if quality == 40:
                                width, height = original_image.size
                                if width > 800 or height > 800:
                                    original_image.thumbnail((800, 800), Image.Resampling.LANCZOS)
                                    output = io.BytesIO()
                                    original_image.save(output, format='JPEG', quality=70, optimize=True)
                                    compressed_data = output.getvalue()
                        
                        # Final size check
                        if len(compressed_data) > 1024 * 1024:  # 1MB final limit
                            flash('Unable to compress image small enough. Please use a smaller image.', 'error')
                            return render_template('customer/transaction.html', 
                                                 business=business, 
                                                 transaction_type=transaction_type,
                                                 current_balance=current_balance)
                        
                        # Convert to base64 for database storage
                        bill_photo_data = base64.b64encode(compressed_data).decode('utf-8')
                        print(f"DEBUG: Bill photo compressed and encoded to base64, size: {len(bill_photo_data)} characters")
                        
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
                'id': str(uuid.uuid4()),
                'business_id': business_id,
                'customer_id': customer_id,
                'transaction_type': transaction_type,
                'amount': amount,
                'notes': notes,
                'created_at': get_ist_isoformat()
            }
            
            # Add bill photo data if available
            if bill_photo_data:
                transaction_data['receipt_image_url'] = bill_photo_data
            
            print(f"DEBUG: Transaction data: {transaction_data}")
            
            # Insert transaction
            result = query_table('transactions', query_type='insert', data=transaction_data)
            
            print(f"DEBUG: Insert result: {result}")
            print(f"DEBUG: Result data: {result.data if result else 'None'}")
            
            if result and result.data:
                # Update customer credits table
                credit_response = query_table('customer_credits', 
                                            filters=[('business_id', 'eq', business_id),
                                                    ('customer_id', 'eq', customer_id)])
                
                print(f"DEBUG: Credit response: {credit_response.data if credit_response else 'None'}")
                
                if credit_response and credit_response.data:
                    # Update existing credit record
                    credit = credit_response.data[0]
                    current_balance = float(credit.get('current_balance', 0))
                    
                    if transaction_type == 'credit':
                        new_balance = current_balance + amount
                    else:  # payment
                        new_balance = current_balance - amount
                    
                    print(f"DEBUG: Updating balance from {current_balance} to {new_balance}")
                    
                    update_data = {
                        'current_balance': new_balance,
                        'updated_at': get_ist_isoformat()
                    }
                    
                    update_result = query_table('customer_credits', query_type='update', 
                               filters=[('id', 'eq', credit['id'])], data=update_data)
                    print(f"DEBUG: Update result: {update_result}")
                else:
                    # Create new credit record
                    print("DEBUG: Creating new credit record")
                    credit_data = {
                        'id': str(uuid.uuid4()),
                        'business_id': business_id,
                        'customer_id': customer_id,
                        'current_balance': amount if transaction_type == 'credit' else -amount,
                        'updated_at': get_ist_isoformat(),
                        'created_at': get_ist_isoformat()
                    }
                    
                    credit_result = query_table('customer_credits', query_type='insert', data=credit_data)
                    print(f"DEBUG: Credit insert result: {credit_result}")
                
                action = 'taken credit of' if transaction_type == 'credit' else 'made payment of'
                flash(f'Successfully {action} ₹{amount}', 'success')
                return redirect(url_for('business_view', business_id=business_id))
            else:
                print("ERROR: Failed to insert transaction - result or result.data is None/empty")
                flash('Failed to record transaction. Please check your database connection.', 'error')
                
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

@customer_app.route('/transaction/bill/<transaction_id>')
@login_required
def serve_bill_from_database(transaction_id):
    """Serve bill photo directly from database"""
    try:
        import base64
        from flask import Response
        
        print(f"DEBUG: Serving bill for transaction {transaction_id}")
        
        # Get the transaction with bill photo data
        transaction_result = query_table('transactions', 
                                       filters=[('id', 'eq', transaction_id)])
        
        if not transaction_result or not transaction_result.data:
            print(f"DEBUG: Transaction {transaction_id} not found")
            return "Transaction not found", 404
            
        transaction = transaction_result.data[0]
        bill_photo_data = transaction.get('receipt_image_url')
        
        if not bill_photo_data:
            print(f"DEBUG: No bill photo data for transaction {transaction_id}")
            return "No bill photo found", 404
            
        # Check if data is base64 encoded or old file path
        if bill_photo_data.startswith('/uploads/bills/'):
            print(f"DEBUG: Old file format for transaction {transaction_id}")
            return "Old file format not supported", 404
            
        print(f"DEBUG: Found bill photo data, size: {len(bill_photo_data)} characters")
        
        # Decode base64 image data
        try:
            image_data = base64.b64decode(bill_photo_data)
            print(f"DEBUG: Decoded image data, size: {len(image_data)} bytes")
            
            # Determine content type based on image signature
            content_type = 'image/jpeg'  # Default
            if image_data.startswith(b'\x89PNG'):
                content_type = 'image/png'
            elif image_data.startswith(b'GIF'):
                content_type = 'image/gif'
            elif image_data.startswith(b'\xff\xd8'):
                content_type = 'image/jpeg'
                
            print(f"DEBUG: Serving image as {content_type}")
            return Response(image_data, mimetype=content_type)
            
        except Exception as e:
            print(f"ERROR: Failed to decode image data: {e}")
            return f"Invalid image data: {str(e)}", 400
            
    except Exception as e:
        print(f"ERROR: Failed to serve bill image: {e}")
        return f"Server error: {str(e)}", 500

@customer_app.route('/api/business/<business_id>/transactions', methods=['GET'])
def api_business_transactions(business_id):
    """API endpoint for business owners to view all transactions with bill photos"""
    try:
        # Get all transactions for this business
        transactions_result = query_table('transactions', 
                                        filters=[('business_id', 'eq', business_id)])
        
        if not transactions_result or not transactions_result.data:
            return jsonify({'success': True, 'transactions': []})
            
        transactions = []
        for tx in transactions_result.data:
            # Get customer info
            customer_result = query_table('customers', 
                                        filters=[('id', 'eq', tx.get('customer_id'))])
            customer_info = customer_result.data[0] if customer_result and customer_result.data else {}
            
            transaction_data = {
                'id': tx.get('id'),
                'customer_name': customer_info.get('name', 'Unknown Customer'),
                'customer_phone': customer_info.get('phone_number', ''),
                'amount': float(tx.get('amount', 0)),
                'transaction_type': tx.get('transaction_type'),
                'notes': tx.get('notes', ''),
                'created_at': tx.get('created_at'),
                'has_bill_photo': bool(tx.get('receipt_image_url')),
                'bill_photo_url': f"/transaction/bill/{tx.get('id')}" if tx.get('receipt_image_url') else None
            }
            transactions.append(transaction_data)
        
        # Sort by date, newest first
        transactions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'transactions': transactions,
            'total_count': len(transactions),
            'with_photos': len([t for t in transactions if t['has_bill_photo']])
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@customer_app.route('/business-dashboard')
def business_dashboard():
    """Business dashboard to view all transactions and bill photos"""
    return render_template('business_dashboard.html')

# Error handling
@customer_app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@customer_app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

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

# Run the application
if __name__ == '__main__':
    port = int(os.environ.get('CUSTOMER_PORT', 5002))
    customer_app.run(debug=False, host='0.0.0.0', port=port)
