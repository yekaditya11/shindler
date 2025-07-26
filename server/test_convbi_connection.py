#!/usr/bin/env python3
"""
Test script to isolate the ConversationalBI connection issue
"""

import os
import json
import psycopg
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Load environment variables
load_dotenv()

def test_postgres_connection():
    """Test PostgreSQL connection"""
    print("Testing PostgreSQL connection...")
    try:
        DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        print(f"Database URL: {DATABASE_URL}")
        connection = psycopg.connect(DATABASE_URL)
        print("✅ PostgreSQL connection successful!")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_azure_openai_connection():
    """Test Azure OpenAI connection"""
    print("\nTesting Azure OpenAI connection...")
    
    # Load round robin count
    try:
        with open("src/convBI_engine/round_robin.json", "r") as f:
            round_robin_count = json.load(f)["count"]
        print(f"Round robin count: {round_robin_count}")
    except Exception as e:
        print(f"❌ Failed to read round_robin.json: {e}")
        return False
    
    # Test Azure OpenAI connection
    try:
        endpoint = os.environ.get(f"AZURE_OPENAI_ENDPOINT_{round_robin_count}")
        deployment = os.environ.get(f"AZURE_OPENAI_DEPLOYMENT_NAME_{round_robin_count}")
        api_version = os.environ.get(f"AZURE_OPENAI_API_VERSION_{round_robin_count}")
        api_key = os.environ.get(f"AZURE_OPENAI_API_KEY_{round_robin_count}")
        
        print(f"Endpoint: {endpoint}")
        print(f"Deployment: {deployment}")
        print(f"API Version: {api_version}")
        print(f"API Key: {'*' * 10 if api_key else 'None'}")
        
        if not all([endpoint, deployment, api_version, api_key]):
            print("❌ Missing Azure OpenAI environment variables")
            return False
        
        llm = AzureChatOpenAI(
            azure_endpoint=endpoint,
            azure_deployment=deployment,
            openai_api_version=api_version,
            api_key=api_key
        )
        
        # Test with a simple prompt
        response = llm.invoke("Hello, this is a test message.")
        print("✅ Azure OpenAI connection successful!")
        print(f"Response: {response.content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Azure OpenAI connection failed: {e}")
        return False

def test_langgraph_postgres_connection():
    """Test LangGraph PostgreSQL connection"""
    print("\nTesting LangGraph PostgreSQL connection...")
    try:
        from langgraph.checkpoint.postgres import PostgresSaver
        
        DB_URI = f"postgres://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        print(f"LangGraph DB URI: {DB_URI}")
        
        with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
            print("✅ LangGraph PostgreSQL connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ LangGraph PostgreSQL connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing ConversationalBI connections...\n")
    
    postgres_ok = test_postgres_connection()
    azure_ok = test_azure_openai_connection()
    langgraph_ok = test_langgraph_postgres_connection()
    
    print(f"\n📊 Test Results:")
    print(f"PostgreSQL: {'✅' if postgres_ok else '❌'}")
    print(f"Azure OpenAI: {'✅' if azure_ok else '❌'}")
    print(f"LangGraph PostgreSQL: {'✅' if langgraph_ok else '❌'}")
    
    if all([postgres_ok, azure_ok, langgraph_ok]):
        print("\n🎉 All connections are working!")
    else:
        print("\n⚠️ Some connections are failing. Check the errors above.")
