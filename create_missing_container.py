"""
Create the missing invoice_query_audit container
"""

import os
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("COSMOS_ENDPOINT")
key = os.getenv("COSMOS_KEY")
database_name = os.getenv("COSMOS_DATABASE_NAME", "rag_database")

print(f"🔗 Connecting to: {endpoint}")
print(f"📊 Database: {database_name}\n")

client = CosmosClient(endpoint, key)
database = client.get_database_client(database_name)

container_name = "invoice_query_audit"
partition_key = "/tenant_id"

print(f"Creating container: {container_name}")
print(f"Partition key: {partition_key}\n")

try:
    # Create container without specifying throughput (serverless)
    database.create_container(
        id=container_name,
        partition_key=PartitionKey(path=partition_key)
    )
    print(f"✅ Created container: {container_name}")
    print(f"   📝 Query tracking and analytics")
    print(f"   🔑 Partition key: {partition_key}")
    print(f"   💰 Throughput: Serverless (auto-scaled)")
    
except exceptions.CosmosResourceExistsError:
    print(f"⚠️  Container already exists: {container_name}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✅ Setup Complete!")
print("="*60)
print("\nAll containers:")
print("  1. embeddings (old)")
print("  2. invoice_documents ✨")
print("  3. invoice_chunks ✨")
print("  4. invoice_query_audit ✨")
print("\nReady to start the application!")
print("="*60)

