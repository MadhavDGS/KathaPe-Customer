"""
Appwrite Configuration and Utilities for KathaPe Customer App
Compatible with Appwrite SDK 11.1.0
"""
import os
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.account import Account
from appwrite.query import Query
from appwrite.exception import AppwriteException
import cloudinary
import cloudinary.uploader
import cloudinary.api
import uuid
from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash

# Helper to ensure required environment variables are set in production
def get_required_env(var_name):
    value = os.getenv(var_name)
    # In a production environment (like on Render), we must have these values.
    if not value and os.getenv('FLASK_ENV') == 'production':
        raise ValueError(f"FATAL: Missing required environment variable '{var_name}'. Please set it in your deployment environment.")
    return value

# Appwrite Configuration
APPWRITE_ENDPOINT = get_required_env('APPWRITE_ENDPOINT')
APPWRITE_PROJECT_ID = get_required_env('APPWRITE_PROJECT_ID')
APPWRITE_API_KEY = get_required_env('APPWRITE_API_KEY')
APPWRITE_DATABASE_ID = get_required_env('APPWRITE_DATABASE_ID')

# Initialize Appwrite Client
appwrite_client = Client()
appwrite_client.set_endpoint(APPWRITE_ENDPOINT)
appwrite_client.set_project(APPWRITE_PROJECT_ID)
appwrite_client.set_key(APPWRITE_API_KEY)

# Initialize Services
appwrite_db = Databases(appwrite_client)
appwrite_account = Account(appwrite_client)

# Collection IDs (same as business side)
USERS_COLLECTION = os.getenv('USERS_COLLECTION_ID', 'users')
BUSINESSES_COLLECTION = os.getenv('BUSINESSES_COLLECTION_ID', 'businesses')
CUSTOMERS_COLLECTION = os.getenv('CUSTOMERS_COLLECTION_ID', 'customers')
CUSTOMER_CREDITS_COLLECTION = os.getenv('CUSTOMER_CREDITS_COLLECTION_ID', 'customer_credits')
TRANSACTIONS_COLLECTION = os.getenv('TRANSACTIONS_COLLECTION_ID', 'transactions')

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

def get_ist_now():
    """Get current time in IST"""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

def get_ist_isoformat():
    """Get current time in IST ISO format"""
    return get_ist_now().isoformat()

class AppwriteDB:
    """Appwrite database wrapper class"""
    
    def __init__(self):
        self.db = appwrite_db
        self.database_id = APPWRITE_DATABASE_ID
    
    def list_documents(self, collection_id, queries=None):
        """List documents from a collection"""
        try:
            if queries is None:
                queries = []
            result = self.db.list_documents(
                database_id=self.database_id,
                collection_id=collection_id,
                queries=queries
            )
            return result['documents']
        except AppwriteException as e:
            print(f"Appwrite error listing documents: {e}")
            return []
    
    def get_document(self, collection_id, document_id):
        """Get a single document by ID"""
        try:
            result = self.db.get_document(
                database_id=self.database_id,
                collection_id=collection_id,
                document_id=document_id
            )
            return result
        except AppwriteException as e:
            print(f"Appwrite error getting document: {e}")
            return None
    
    def create_document(self, collection_id, document_id, data):
        """Create a new document"""
        try:
            result = self.db.create_document(
                database_id=self.database_id,
                collection_id=collection_id,
                document_id=document_id,
                data=data
            )
            return result
        except AppwriteException as e:
            print(f"Appwrite error creating document: {e}")
            return None
    
    def update_document(self, collection_id, document_id, data):
        """Update an existing document"""
        try:
            result = self.db.update_document(
                database_id=self.database_id,
                collection_id=collection_id,
                document_id=document_id,
                data=data
            )
            return result
        except AppwriteException as e:
            print(f"Appwrite error updating document: {e}")
            return None
    
    def delete_document(self, collection_id, document_id):
        """Delete a document"""
        try:
            result = self.db.delete_document(
                database_id=self.database_id,
                collection_id=collection_id,
                document_id=document_id
            )
            return result
        except AppwriteException as e:
            print(f"Appwrite error deleting document: {e}")
            return None

# Global database instance
appwrite_db_instance = AppwriteDB()

def safe_uuid(uuid_string):
    """Safely convert string to UUID format"""
    if not uuid_string:
        return str(uuid.uuid4())
    try:
        # If it's already a valid UUID string, return as is
        uuid.UUID(str(uuid_string))
        return str(uuid_string)
    except (ValueError, TypeError):
        # If not valid UUID, generate new one
        return str(uuid.uuid4())

# Authentication functions
def login_user(phone_number, password):
    """Authenticate user with phone and password"""
    try:
        # Query users collection for phone number and customer type
        users = appwrite_db_instance.list_documents(
            USERS_COLLECTION,
            [
                Query.equal('phone_number', phone_number),
                Query.equal('user_type', 'customer')
            ]
        )
        
        if users and len(users) > 0:
            user = users[0]
            # Securely check the hashed password
            if check_password_hash(user.get('password', ''), password):
                return user
        
        return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def register_user(name, phone_number, password):
    """Register a new customer user"""
    try:
        print(f"🔍 register_user called with: name={name}, phone={phone_number}")
        
        # Check if user already exists
        print(f"🔎 Checking if user exists...")
        existing_users = appwrite_db_instance.list_documents(
            USERS_COLLECTION,
            [Query.equal('phone_number', phone_number)]
        )
        print(f"📊 Found {len(existing_users)} existing users with phone {phone_number}")
        
        if existing_users:
            error_msg = 'Phone number already registered'
            print(f"❌ {error_msg}")
            return {'error': error_msg}
        
        # Create user
        user_id = str(uuid.uuid4())
        user_data = {
            'name': name,
            'phone_number': phone_number,
            'user_type': 'customer',
            'password': generate_password_hash(password),
            'created_at': get_ist_isoformat()
        }
        
        print(f"👤 Creating user with ID: {user_id}")
        print(f"📝 User data: {user_data}")
        user = appwrite_db_instance.create_document(USERS_COLLECTION, user_id, user_data)
        
        if user:
            print(f"✅ User created successfully: {user['$id']}")
            # Create customer profile
            customer_id = str(uuid.uuid4())
            customer_data = {
                'user_id': user_id,
                'name': name,
                'phone_number': phone_number,
                'created_at': get_ist_isoformat()
            }
            
            print(f"👥 Creating customer profile with ID: {customer_id}")
            print(f"📝 Customer data: {customer_data}")
            customer = appwrite_db_instance.create_document(CUSTOMERS_COLLECTION, customer_id, customer_data)
            
            if customer:
                print(f"✅ Customer profile created successfully: {customer['$id']}")
                return {'user': user, 'customer': customer}
            else:
                # Rollback user creation if customer creation fails
                print(f"❌ Customer creation failed, rolling back user...")
                appwrite_db_instance.delete_document(USERS_COLLECTION, user_id)
                return {'error': 'Failed to create customer profile'}
        
        print(f"❌ User creation failed")
        return {'error': 'Failed to create user'}
        
    except Exception as e:
        error_msg = f"Registration error: {e}"
        print(f"❌ Exception in register_user: {error_msg}")
        print(f"Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

# Business and customer relationship functions
def get_customer_by_user_id(user_id):
    """Get customer by user ID"""
    try:
        customers = appwrite_db_instance.list_documents(
            CUSTOMERS_COLLECTION,
            [Query.equal('user_id', user_id)]
        )
        return customers[0] if customers else None
    except Exception as e:
        print(f"Error getting customer: {e}")
        return None

def get_business_by_access_pin(access_pin):
    """Get business by access PIN"""
    try:
        businesses = appwrite_db_instance.list_documents(
            BUSINESSES_COLLECTION,
            [Query.equal('access_pin', access_pin)]
        )
        return businesses[0] if businesses else None
    except Exception as e:
        print(f"Error getting business: {e}")
        return None

def get_customer_credits(customer_id):
    """Get all credit relationships for a customer"""
    try:
        credits = appwrite_db_instance.list_documents(
            CUSTOMER_CREDITS_COLLECTION,
            [Query.equal('customer_id', customer_id)]
        )
        return credits
    except Exception as e:
        print(f"Error getting customer credits: {e}")
        return []

def get_customer_transactions(customer_id, business_id=None):
    """Get transactions for a customer, optionally filtered by business"""
    try:
        queries = [Query.equal('customer_id', customer_id)]
        if business_id:
            queries.append(Query.equal('business_id', business_id))
        
        transactions = appwrite_db_instance.list_documents(
            TRANSACTIONS_COLLECTION,
            queries
        )
        return transactions
    except Exception as e:
        print(f"Error getting transactions: {e}")
        return []

def create_transaction(transaction_data):
    """Create a new transaction"""
    try:
        transaction_id = str(uuid.uuid4())
        transaction_data['created_at'] = get_ist_isoformat()
        
        result = appwrite_db_instance.create_document(
            TRANSACTIONS_COLLECTION,
            transaction_id,
            transaction_data
        )
        return result
    except Exception as e:
        print(f"Error creating transaction: {e}")
        return None

def update_customer_credit(customer_id, business_id, new_balance):
    """Update customer credit balance"""
    try:
        # Find existing credit relationship
        credits = appwrite_db_instance.list_documents(
            CUSTOMER_CREDITS_COLLECTION,
            [
                Query.equal('customer_id', customer_id),
                Query.equal('business_id', business_id)
            ]
        )
        
        if credits:
            # Update existing
            credit = credits[0]
            result = appwrite_db_instance.update_document(
                CUSTOMER_CREDITS_COLLECTION,
                credit['$id'],
                {
                    'current_balance': new_balance,
                    'updated_at': get_ist_isoformat()
                }
            )
            return result
        else:
            # Create new credit relationship
            credit_id = str(uuid.uuid4())
            credit_data = {
                'customer_id': customer_id,
                'business_id': business_id,
                'current_balance': new_balance,
                'created_at': get_ist_isoformat(),
                'updated_at': get_ist_isoformat()
            }
            result = appwrite_db_instance.create_document(
                CUSTOMER_CREDITS_COLLECTION,
                credit_id,
                credit_data
            )
            return result
    except Exception as e:
        print(f"Error updating customer credit: {e}")
        return None

def create_customer_credit_relationship(customer_id, business_id):
    """Create a new customer-business credit relationship"""
    try:
        # Check if relationship already exists
        existing = appwrite_db_instance.list_documents(
            CUSTOMER_CREDITS_COLLECTION,
            [
                Query.equal('customer_id', customer_id),
                Query.equal('business_id', business_id)
            ]
        )
        
        if existing:
            return existing[0]  # Return existing relationship
        
        # Create new relationship
        credit_id = str(uuid.uuid4())
        credit_data = {
            'customer_id': customer_id,
            'business_id': business_id,
            'current_balance': 0,
            'created_at': get_ist_isoformat(),
            'updated_at': get_ist_isoformat()
        }
        
        result = appwrite_db_instance.create_document(
            CUSTOMER_CREDITS_COLLECTION,
            credit_id,
            credit_data
        )
        return result
    except Exception as e:
        print(f"Error creating credit relationship: {e}")
        return None

def upload_bill_image(file_data, filename, transaction_id):
    """
    Upload a bill image to Cloudinary
    Returns the public_id if successful, None if failed
    """
    try:
        # Create a unique public ID
        public_id = f"bill_receipts/bill_{transaction_id}_{uuid.uuid4().hex[:8]}"
        
        print(f"DEBUG: Uploading to Cloudinary with public_id: {public_id}")
        print(f"DEBUG: File size: {len(file_data) if isinstance(file_data, bytes) else 'N/A'} bytes")
        
        # Upload to Cloudinary with optimizations
        result = cloudinary.uploader.upload(
            file_data,
            public_id=public_id,
            resource_type="image",
            # Optimizations
            quality="85",
            fetch_format="auto",
            # Transformations for better storage and performance
            width=1200,
            height=1200,
            crop="limit",
            # Add tags for organization
            tags=["bill_receipt", f"transaction_{transaction_id}"],
            # Enable backup
            backup=True
        )
        
        print(f"DEBUG: Cloudinary upload successful!")
        print(f"DEBUG: Result public_id: {result.get('public_id')}")
        print(f"DEBUG: Result secure_url: {result.get('secure_url')}")
        
        return result['public_id']
        
    except Exception as e:
        print(f"ERROR: Cloudinary error uploading bill image: {e}")
        print(f"ERROR: Exception type: {type(e)}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        return None

def get_bill_image_url(public_id):
    """
    Get the optimized URL for a bill image from Cloudinary
    """
    try:
        # First check if we have a valid public_id
        if not public_id:
            print(f"DEBUG: No public_id provided to get_bill_image_url")
            return None
            
        print(f"DEBUG: Generating URL for public_id: {public_id}")
        
        # Generate optimized URL with transformations
        url, options = cloudinary.utils.cloudinary_url(
            public_id,
            # Automatic optimizations
            quality="85",
            fetch_format="auto",
            # Responsive sizing 
            width=800,
            crop="limit",
            # Security
            secure=True
        )
        
        print(f"DEBUG: Generated Cloudinary URL: {url}")
        return url
    except Exception as e:
        print(f"ERROR: Error generating Cloudinary URL: {e}")
        return None

def delete_bill_image(public_id):
    """
    Delete a bill image from Cloudinary
    """
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type="image")
        
        if result.get('result') == 'ok':
            print(f"DEBUG: Successfully deleted bill image: {public_id}")
            return True
        else:
            print(f"DEBUG: Failed to delete bill image: {public_id}, result: {result}")
            return False
            
    except Exception as e:
        print(f"Error deleting bill image from Cloudinary: {e}")
        return False
