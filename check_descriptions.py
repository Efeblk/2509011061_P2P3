from src.database.connection import db_connection


def check_descriptions():
    print("Connecting to database...")
    # Connection is automatic on import

    query = """
    MATCH (e:Event)
    RETURN e.title, e.description, e.source
    LIMIT 10
    """

    print("Executing query...")
    result = db_connection.execute_query(query)

    if not result.result_set:
        print("No events found in database.")
        return

    print(f"\nFound {len(result.result_set)} events. Checking descriptions:\n")
    print(f"{'Source':<15} | {'Title':<40} | {'Description Length'}")
    print("-" * 80)

    count_missing = 0
    for row in result.result_set:
        title = row[0]
        description = row[1]
        source = row[2]

        desc_len = len(description) if description else 0
        desc_preview = "MISSING" if not description else f"{desc_len} chars"

        print(f"{source:<15} | {title[:40]:<40} | {desc_preview}")

        if not description:
            count_missing += 1

    print("-" * 80)
    print(f"Total checked: {len(result.result_set)}")
    print(f"Missing descriptions: {count_missing}")


if __name__ == "__main__":
    check_descriptions()
