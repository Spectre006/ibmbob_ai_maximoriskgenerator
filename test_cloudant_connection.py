#!/usr/bin/env python3
"""Test script to debug Cloudant connection and query issues."""

import asyncio
import sys
from services.cloudant_service import cloudant_service
from utils.logger import get_logger

logger = get_logger(__name__)


async def test_cloudant():
    """Test Cloudant connection and list reports."""
    print("=" * 60)
    print("Cloudant Connection Test")
    print("=" * 60)
    
    # Test 1: Connection
    print("\n1. Testing connection...")
    try:
        cloudant_service.connect()
        if cloudant_service.database:
            print("✓ Connected to Cloudant successfully")
            print(f"  Database: {cloudant_service.database_name}")
        else:
            print("✗ Failed to connect (database is None)")
            print("  Check your .env file for correct credentials:")
            print("  - CLOUDANT_URL")
            print("  - CLOUDANT_API_KEY")
            print("  - CLOUDANT_DATABASE")
            return
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return
    
    # Test 2: List all documents
    print("\n2. Listing all documents in database...")
    try:
        all_docs = cloudant_service.database.all_docs(include_docs=True)
        doc_count = 0
        jha_count = 0
        
        for doc in all_docs:
            doc_count += 1
            doc_data = doc.get('doc', {})
            if doc_data.get('type') == 'jha_report':
                jha_count += 1
                print(f"  - JHA Report: {doc_data.get('_id')} | WO: {doc_data.get('work_order_id')} | Created: {doc_data.get('created_at')}")
        
        print(f"\n  Total documents: {doc_count}")
        print(f"  JHA reports: {jha_count}")
        
        if jha_count == 0:
            print("\n  ⚠ No JHA reports found in database!")
            print("  Generate a report first to test the history feature.")
            
    except Exception as e:
        print(f"✗ Failed to list documents: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Query using list_reports
    print("\n3. Testing list_reports method...")
    try:
        reports = await cloudant_service.list_reports(limit=50)
        print(f"  Found {len(reports)} reports")
        
        for report in reports:
            print(f"  - {report.get('report_id')} | WO: {report.get('work_order_id')}")
            
        if len(reports) == 0:
            print("\n  ⚠ list_reports returned empty list")
            print("  This could mean:")
            print("  - No documents with type='jha_report' exist")
            print("  - Query selector is not matching documents")
            print("  - Sort index is missing (check logs)")
            
    except Exception as e:
        print(f"✗ list_reports failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Check for sort index
    print("\n4. Checking for sort index...")
    try:
        indexes = cloudant_service.database.get_query_indexes()
        print(f"  Found {len(indexes)} indexes:")
        for idx in indexes:
            print(f"  - {idx.get('name')}: {idx.get('def', {}).get('fields')}")
    except Exception as e:
        print(f"  Could not retrieve indexes: {e}")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
    
    # Cleanup
    cloudant_service.disconnect()


if __name__ == "__main__":
    asyncio.run(test_cloudant())

# Made with Bob
