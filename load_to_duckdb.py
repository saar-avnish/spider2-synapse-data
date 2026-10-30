import os
import glob
import duckdb

DATA_DIR = "data"
DB_PATH = "dirty_synapse.duckdb"

# Connect to a persistent DuckDB database file (created if not exists)
con = duckdb.connect(DB_PATH)

csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))

if not csv_files:
    print(f"No CSV files found in ./{DATA_DIR}/. Run generate_dirty_tables.py first.")
    exit(1)

print(f"Connecting to DuckDB file: {DB_PATH}")
print(f"Ingesting {len(csv_files)} dirty tables...\n")

for file_path in sorted(csv_files):
    # Extract table name from filename (e.g., 'mkt_utm_clicks_raw.csv' -> 'mkt_utm_clicks_raw')
    table_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # Normalize Windows path separators for SQL
    normalized_path = file_path.replace("\\", "/")
    
    # Read CSV with lenient parsing options to handle dirty data without crashes
    query = f"""
    CREATE OR REPLACE TABLE "{table_name}" AS 
    SELECT * FROM read_csv(
        '{normalized_path}',
        header = true,
        auto_detect = true,
        sample_size = 2000,
        ignore_errors = true,
        null_padding = true
    );
    """
    con.execute(query)
    
    # Get row count and column count
    row_count = con.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
    col_count = len(con.execute(f'PRAGMA table_info("{table_name}")').fetchall())
    
    print(f"? Loaded table: {table_name:<30} | {row_count:>6,} rows | {col_count:>2} columns")

print("\nIngestion complete.")
con.close()
