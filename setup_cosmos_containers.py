"""
Setup Script for Invoice Intelligence Cosmos DB Containers

This script creates the required containers for the Invoice Intelligence system:
1. invoice_documents - Structured invoice data
2. invoice_chunks - Vector embeddings with invoice metadata
3. invoice_query_audit - Query tracking and analytics

Run this ONCE before starting the application for the first time.
"""

import os
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_containers():
    """Create the required Cosmos DB containers"""
    
    # Get Cosmos DB credentials
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")
    database_name = os.getenv("COSMOS_DATABASE_NAME", "rag_database")
    
    if not endpoint or not key:
        print("❌ Error: COSMOS_ENDPOINT and COSMOS_KEY must be set in .env file")
        return False
    
    print(f"🔗 Connecting to Cosmos DB: {endpoint}")
    print(f"📊 Database: {database_name}")
    
    try:
        # Initialize Cosmos client
        client = CosmosClient(endpoint, key)
        
        # Get or create database
        try:
            database = client.create_database(database_name)
            print(f"✅ Created database: {database_name}")
        except exceptions.CosmosResourceExistsError:
            database = client.get_database_client(database_name)
            print(f"✅ Using existing database: {database_name}")
        
        # Container configurations
        containers = [
            {
                "name": "invoice_documents",
                "partition_key": "/tenant_id",
                "description": "Structured invoice data (headers, amounts, line items, flags)"
            },
            {
                "name": "invoice_chunks",
                "partition_key": "/tenant_id",
                "description": "Vector embeddings with invoice metadata",
                "vector_policy": True  # Enable vector indexing
            },
            {
                "name": "invoice_query_audit",
                "partition_key": "/tenant_id",
                "description": "Query tracking and analytics"
            }
        ]
        
        # Create each container
        for container_config in containers:
            container_name = container_config["name"]
            partition_key = container_config["partition_key"]
            description = container_config["description"]

            try:
                # Create container with partition key
                # Note: For serverless accounts, don't specify offer_throughput
                container = database.create_container(
                    id=container_name,
                    partition_key=PartitionKey(path=partition_key)
                    # offer_throughput removed for serverless compatibility
                )
                print(f"✅ Created container: {container_name}")
                print(f"   📝 {description}")
                print(f"   🔑 Partition key: {partition_key}")
                print(f"   💰 Throughput: Serverless (auto-scaled)")

            except exceptions.CosmosResourceExistsError:
                print(f"⚠️  Container already exists: {container_name}")
                print(f"   📝 {description}")
        
        print("\n" + "="*60)
        print("✅ Cosmos DB Setup Complete!")
        print("="*60)
        print("\nContainers created:")
        print("  1. invoice_documents - Structured invoice data")
        print("  2. invoice_chunks - Vector embeddings")
        print("  3. invoice_query_audit - Query tracking")
        print("\nNext steps:")
        print("  1. Verify containers in Azure Portal")
        print("  2. Update .env file (if needed)")
        print("  3. Run: python -m uvicorn app:app --reload")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating containers: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("Invoice Intelligence - Cosmos DB Setup")
    print("="*60)
    print()
    
    success = create_containers()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("\nYou can now start the application:")
        print("  python -m uvicorn app:app --reload --port 9000")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("  1. Verify COSMOS_ENDPOINT and COSMOS_KEY in .env")
        print("  2. Check Azure Portal for Cosmos DB access")
        print("  3. Ensure you have permissions to create containers")

