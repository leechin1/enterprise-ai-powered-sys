#!/usr/bin/env python3
"""
Main script to orchestrate data generation and insertion
"""

from gemini_generator import GeminiDataGenerator
from db_connector import DatabaseConnector
from config import DATA_COUNTS
from generate_data import (
    generate_order_items,
    generate_payments,
    generate_shipments,
    generate_reviews,
    generate_inventory,
    generate_inventory_transactions,
    generate_case_messages,
    generate_workflow_executions
)


def main():
    """Main data generation workflow"""
    print("=" * 60)
    print("FAKE DATA GENERATION WITH GEMINI API")
    print("=" * 60)

    generator = GeminiDataGenerator()
    db = DatabaseConnector()

    try:
        # Connect to database
        db.connect()

        # Generate and insert data in order (respecting foreign key constraints)
        print("\n1. Generating genres...")
        genres_data = generator.generate_genres(DATA_COUNTS['genres'])
        genre_ids = db.insert_genres(genres_data)
        print(f"✓ Inserted {len(genre_ids)} genres")

        print("\n2. Generating labels...")
        labels_data = generator.generate_labels(DATA_COUNTS['labels'])
        label_ids = db.insert_labels(labels_data)
        print(f"✓ Inserted {len(label_ids)} labels")

        print("\n3. Generating users...")
        users_data = generator.generate_users(DATA_COUNTS['users'])
        user_ids = db.insert_users(users_data)
        print(f"✓ Inserted {len(user_ids)} users")

        print("\n4. Generating customers...")
        customers_data = generator.generate_customers(DATA_COUNTS['customers'])
        customer_ids = db.insert_customers(customers_data)
        print(f"✓ Inserted {len(customer_ids)} customers")

        print("\n5. Generating albums...")
        albums_data = generator.generate_albums(DATA_COUNTS['albums'], genre_ids, label_ids)
        album_ids = db.insert_albums(albums_data)
        print(f"✓ Inserted {len(album_ids)} albums")

        print("\n6. Generating inventory...")
        generate_inventory(album_ids, db)

        print("\n7. Generating orders...")
        orders_data = generator.generate_orders(DATA_COUNTS['orders'], customer_ids)
        order_ids = db.insert_orders(orders_data)
        print(f"✓ Inserted {len(order_ids)} orders")

        print("\n8. Generating order items...")
        generate_order_items(order_ids, album_ids, db)

        print("\n9. Generating payments...")
        generate_payments(order_ids, db)

        print("\n10. Generating shipments...")
        generate_shipments(order_ids, db)

        print("\n11. Generating reviews...")
        generate_reviews(customer_ids, album_ids, db)

        # For inventory transactions, we'd need to query inventory IDs
        # Simplified version here
        print("\n12. Generating inventory transactions...")
        # Using album_ids as proxy for inventory_ids (1:1 relationship)
        generate_inventory_transactions(album_ids, order_ids, user_ids, db)

        print("\n13. Generating cases...")
        cases_data = generator.generate_cases(DATA_COUNTS['cases'], customer_ids, user_ids)
        case_ids = db.insert_cases(cases_data)
        print(f"✓ Inserted {len(case_ids)} cases")

        print("\n14. Generating case messages...")
        generate_case_messages(case_ids, user_ids, db)

        print("\n15. Generating workflows...")
        workflows_data = generator.generate_workflows(DATA_COUNTS['workflows'])
        workflow_ids = db.insert_workflows(workflows_data)
        print(f"✓ Inserted {len(workflow_ids)} workflows")

        print("\n16. Generating workflow executions...")
        generate_workflow_executions(workflow_ids, db)

        print("\n17. Generating integrations...")
        integrations_data = generator.generate_integrations(DATA_COUNTS['integrations'])
        integration_ids = db.insert_integrations(integrations_data)
        print(f"✓ Inserted {len(integration_ids)} integrations")

        print("\n18. Generating system logs...")
        logs_data = generator.generate_system_logs(DATA_COUNTS['system_logs'], user_ids)
        db.insert_system_logs(logs_data)
        print(f"✓ Inserted {DATA_COUNTS['system_logs']} system logs")

        print("\n" + "=" * 60)
        print("✓ DATA GENERATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during data generation: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == '__main__':
    main()
