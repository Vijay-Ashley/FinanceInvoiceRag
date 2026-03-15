"""
Check which Cosmos DB containers exist
"""

import os
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("COSMOS_ENDPOINT")
key = os.getenv("COSMOS_KEY")
database_name = os.getenv("COSMOS_DATABASE_NAME", "rag_database")

print(f"🔗 Connecting to: {endpoint}")
print(f"📊 Database: {database_name}\n")

client = CosmosClient(endpoint, key)
database = client.get_database_client(database_name)

print("Existing containers:")
print("-" * 60)

containers = list(database.list_containers())
for container in containers:
    print(f"✅ {container['id']}")

print("-" * 60)
print(f"\nTotal: {len(containers)} containers")

# Check for required containers
required = ["invoice_documents", "invoice_chunks", "invoice_query_audit"]
missing = [c for c in required if c not in [cont['id'] for cont in containers]]

if missing:
    print(f"\n⚠️  Missing containers: {', '.join(missing)}")
else:
    print("\n✅ All required containers exist!")

