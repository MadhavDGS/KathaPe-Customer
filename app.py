"""
Customer Flask Application - Handles all customer-related operations
"""
from common_utils import *

# Create the customer Flask app
customer_app = create_app('KathaPe-Customer')

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
                            """, [customer_id, user_id, session['user_name'], phone, datetime.now().isoformat()])
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
        phone = request.form.get('phone')
        password = request.form.get('password')
        name = request.form.get('name', f"Customer {phone[-4:]}")
        
        if not phone or not password:
            flash('Please enter both phone number and password', 'error')
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
            user_result = execute_query(user_query, [user_id, name, phone, 'customer', password, datetime.now().isoformat()], fetch_one=True)
            
            if user_result:
                # Create customer record
                customer_query = """
                    INSERT INTO customers (id, user_id, name, phone_number, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """
                execute_query(customer_query, [customer_id, user_id, name, phone, datetime.now().isoformat()])
                
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
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
                    print(f"DEBUG: Credit relationship - Business: {credit['business_name']}, Balance: {credit['current_balance']}")
                    credit_relationships.append({
                        'id': credit['business_id'],  # Template expects 'id' not 'business_id'
                        'business_id': credit['business_id'],
                        'name': credit['business_name'],  # Template expects 'name' not 'business_name'
                        'business_name': credit['business_name'],
                        'current_balance': float(credit['current_balance']) if credit['current_balance'] else 0,
                        'updated_at': credit['updated_at']
                    })
                    total_balance += float(credit['current_balance']) if credit['current_balance'] else 0
                
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
                business['current_balance'] = float(credit.get('current_balance', 0))
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
    
    # Calculate current balance and credit total
    current_balance = credit_received - payments_made  # Positive means customer owes money
    credit_total = credit_received
    
    return render_template('customer/business_view.html',
                         business=business,
                         credit=credit,
                         transactions=transactions,
                         credit_received=credit_received,
                         payments_made=payments_made,
                         current_balance=current_balance,
                         credit_total=credit_total)

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
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
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
    
    if request.method == 'POST':
        amount = request.form.get('amount')
        notes = request.form.get('notes', '')
        
        try:
            amount = float(amount) if amount else 0
            if amount <= 0:
                flash('Please enter a valid amount', 'error')
                return render_template('customer/transaction.html', 
                                     business=business, 
                                     transaction_type=transaction_type)
            
            # Create transaction record
            transaction_data = {
                'id': str(uuid.uuid4()),
                'business_id': business_id,
                'customer_id': customer_id,
                'transaction_type': transaction_type,
                'amount': amount,
                'notes': notes,
                'created_at': datetime.now().isoformat()
            }
            
            # Insert transaction
            result = query_table('transactions', query_type='insert', data=transaction_data)
            
            if result and result.data:
                # Update customer credits table
                credit_response = query_table('customer_credits', 
                                            filters=[('business_id', 'eq', business_id),
                                                    ('customer_id', 'eq', customer_id)])
                
                if credit_response and credit_response.data:
                    # Update existing credit record
                    credit = credit_response.data[0]
                    current_balance = float(credit.get('current_balance', 0))
                    
                    if transaction_type == 'credit':
                        new_balance = current_balance + amount
                    else:  # payment
                        new_balance = current_balance - amount
                    
                    update_data = {
                        'current_balance': new_balance,
                        'last_transaction_date': datetime.now().isoformat()
                    }
                    
                    query_table('customer_credits', query_type='update', 
                               filters=[('id', 'eq', credit['id'])], data=update_data)
                else:
                    # Create new credit record
                    credit_data = {
                        'id': str(uuid.uuid4()),
                        'business_id': business_id,
                        'customer_id': customer_id,
                        'current_balance': amount if transaction_type == 'credit' else -amount,
                        'total_credit_taken': amount if transaction_type == 'credit' else 0,
                        'total_payments_made': amount if transaction_type == 'payment' else 0,
                        'last_transaction_date': datetime.now().isoformat(),
                        'created_at': datetime.now().isoformat()
                    }
                    
                    query_table('customer_credits', query_type='insert', data=credit_data)
                
                action = 'taken credit of' if transaction_type == 'credit' else 'made payment of'
                flash(f'Successfully {action} ₹{amount}', 'success')
                return redirect(url_for('business_view', business_id=business_id))
            else:
                flash('Failed to record transaction', 'error')
                
        except ValueError:
            flash('Please enter a valid amount', 'error')
        except Exception as e:
            flash(f'Error processing transaction: {str(e)}', 'error')
    
    return render_template('customer/transaction.html', 
                         business=business, 
                         transaction_type=transaction_type)

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
