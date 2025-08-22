
import os
import re
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException

# Appwrite Configuration
APPWRITE_ENDPOINT = os.getenv('APPWRITE_ENDPOINT')
APPWRITE_PROJECT_ID = os.getenv('APPWRITE_PROJECT_ID')
APPWRITE_API_KEY = os.getenv('APPWRITE_API_KEY')
APPWRITE_DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')

# Initialize Appwrite Client
appwrite_client = Client()
appwrite_client.set_endpoint(APPWRITE_ENDPOINT)
appwrite_client.set_project(APPWRITE_PROJECT_ID)
appwrite_client.set_key(APPWRITE_API_KEY)

# Initialize Services
appwrite_db = Databases(appwrite_client)

def parse_schema(sql_file):
    with open(sql_file, 'r') as f:
        content = f.read()

    collections = []
    tables = re.findall(r'CREATE TABLE (\w+) \((.*?)\);', content, re.DOTALL)

    for table_name, columns_str in tables:
        collection = {'name': table_name, 'attributes': []}
        columns = re.findall(r'(\w+) (.*?) (NOT NULL|NULL)? ?(UNIQUE)?', columns_str)
        for col_name, col_type, _, _ in columns:
            collection['attributes'].append({'name': col_name, 'type': col_type.strip(',')})
        collections.append(collection)

    return collections

def setup_database(schema_file):
    collections = parse_schema(schema_file)

    for collection_info in collections:
        collection_name = collection_info['name']
        try:
            appwrite_db.get_collection(APPWRITE_DATABASE_ID, collection_name)
            print(f'Collection "{collection_name}" already exists.')
        except AppwriteException as e:
            if e.code == 404:
                print(f'Creating collection "{collection_name}"...')
                appwrite_db.create_collection(APPWRITE_DATABASE_ID, collection_name, collection_name, [], True)
                print(f'Collection "{collection_name}" created.')
            else:
                raise e

        for attribute in collection_info['attributes']:
            attribute_name = attribute['name']
            attribute_type = attribute['type']
            try:
                appwrite_db.get_attribute(APPWRITE_DATABASE_ID, collection_name, attribute_name)
                print(f'Attribute "{attribute_name}" in "{collection_name}" already exists.')
            except AppwriteException as e:
                if e.code == 404:
                    print(f'Creating attribute "{attribute_name}" in "{collection_name}"...')
                    size = 255 # default
                    if 'VARCHAR' in attribute_type:
                        match = re.search(r'\((\d+)\)', attribute_type)
                        if match:
                            size = int(match.group(1))
                        appwrite_db.create_string_attribute(APPWRITE_DATABASE_ID, collection_name, attribute_name, size, False)
                    elif 'DECIMAL' in attribute_type:
                        appwrite_db.create_float_attribute(APPWRITE_DATABASE_ID, collection_name, attribute_name, True)
                    elif 'DATETIME' in attribute_type:
                        appwrite_db.create_datetime_attribute(APPWRITE_DATABASE_ID, collection_name, attribute_name, False)
                    elif 'TEXT' in attribute_type:
                        appwrite_db.create_string_attribute(APPWRITE_DATABASE_ID, collection_name, attribute_name, 1000000, False)
                    print(f'Attribute "{attribute_name}" created.')
                else:
                    raise e

if __name__ == '__main__':
    schema_file = os.path.join(os.path.dirname(__file__), 'database_schema.sql')
    setup_database(schema_file)
