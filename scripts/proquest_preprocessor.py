"""ProQuest CSV Preprocessor for WSJ Headlines

This script processes one or more ProQuest CSV exports and prepares them
for use in the sentiment analysis pipeline.

Usage:
    python proquest_preprocessor.py

Features:
    - Merges multiple ProQuest export batches
    - Cleans and standardizes date formats
    - Removes duplicates
    - Validates data structure
    - Outputs to data/wsj_apple_proquest.csv
"""

from pathlib import Path
from typing import List
import pandas as pd


def load_proquest_export(csv_path: Path) -> pd.DataFrame:
    """Load a single ProQuest CSV export and standardize column names."""
    print(f"Loading {csv_path}...")
    
    # ProQuest exports can have various encodings - try multiple
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            print(f"  Successfully loaded with {encoding} encoding")
            break
        except (UnicodeDecodeError, Exception) as e:
            if encoding == encodings[-1]:  # Last encoding failed
                raise ValueError(
                    f"Could not read {csv_path} with any of these encodings: {encodings}"
                ) from e
            continue
    
    # Display original columns for debugging
    print(f"  Original columns: {list(df.columns)}")
    
    # Try to identify date and headline columns (case-insensitive matching)
    date_col = None
    headline_col = None
    
    for col in df.columns:
        col_lower = col.lower().strip()
        
        # Common ProQuest date column names (exact match first, then partial)
        if col_lower in ['pubdate', 'publication date', 'date', 'pub date', 'published']:
            date_col = col
        elif date_col is None and 'date' in col_lower and 'entry' not in col_lower:
            date_col = col
        
        # Common ProQuest headline/title column names (prioritize exact "title" over "pubtitle")
        if col_lower == 'title':
            headline_col = col
        elif headline_col != 'Title' and col_lower in ['headline', 'article title']:
            headline_col = col
        elif headline_col is None and 'title' in col_lower and 'pub' not in col_lower:
            headline_col = col
    
    if not date_col:
        raise ValueError(
            f"Could not identify date column in {csv_path}. "
            f"Available columns: {list(df.columns)}"
        )
    if not headline_col:
        raise ValueError(
            f"Could not identify headline/title column in {csv_path}. "
            f"Available columns: {list(df.columns)}"
        )
    
    # Standardize to our pipeline format
    result = pd.DataFrame({
        'date': df[date_col],
        'headline': df[headline_col]
    })
    
    print(f"  Mapped '{date_col}' → 'date', '{headline_col}' → 'headline'")
    print(f"  Loaded {len(result)} records")
    
    return result


def clean_proquest_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate ProQuest data."""
    print("\nCleaning data...")
    initial_count = len(df)
    
    # Remove rows with missing headlines
    df = df.dropna(subset=['headline']).copy()
    df['headline'] = df['headline'].astype(str).str.strip()
    df = df[df['headline'] != '']
    print(f"  Removed {initial_count - len(df)} rows with missing headlines")
    
    # Parse dates
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    invalid_dates = df['date'].isna().sum()
    if invalid_dates > 0:
        print(f"  Warning: {invalid_dates} rows have invalid dates, removing them")
        df = df.dropna(subset=['date'])
    
    # Normalize dates to YYYY-MM-DD format
    df['date'] = df['date'].dt.normalize()
    
    # Remove duplicates (same date + headline)
    before_dedup = len(df)
    df = df.drop_duplicates(subset=['date', 'headline'])
    duplicates_removed = before_dedup - len(df)
    if duplicates_removed > 0:
        print(f"  Removed {duplicates_removed} duplicate headlines")
    
    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)
    
    print(f"  Final cleaned dataset: {len(df)} records")
    
    return df


def merge_proquest_batches(input_paths: List[Path]) -> pd.DataFrame:
    """Merge multiple ProQuest export files into a single dataset."""
    if not input_paths:
        raise ValueError("No input files provided")
    
    print(f"Merging {len(input_paths)} ProQuest export file(s)...\n")
    
    all_dataframes = []
    for path in input_paths:
        if not path.exists():
            print(f"Warning: {path} not found, skipping...")
            continue
        try:
            df = load_proquest_export(path)
            all_dataframes.append(df)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            continue
    
    if not all_dataframes:
        raise ValueError("No valid ProQuest files could be loaded")
    
    # Combine all batches
    combined = pd.concat(all_dataframes, ignore_index=True)
    print(f"\nCombined {len(combined)} total records from {len(all_dataframes)} file(s)")
    
    # Clean the merged dataset
    cleaned = clean_proquest_data(combined)
    
    return cleaned


def display_summary(df: pd.DataFrame) -> None:
    """Display a summary of the processed dataset."""
    print("\n" + "="*70)
    print("DATASET SUMMARY")
    print("="*70)
    print(f"Total headlines: {len(df)}")
    print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"Unique dates: {df['date'].nunique()}")
    print(f"Average headlines per day: {len(df) / df['date'].nunique():.2f}")
    print("\nFirst 5 records:")
    print(df.head())
    print("\nLast 5 records:")
    print(df.tail())
    print("="*70 + "\n")


def main():
    """Main preprocessing workflow."""
    # Directory containing ProQuest exports
    data_dir = Path("../data/raw")
    data_dir.mkdir(exist_ok=True)
    
    # Look for ProQuest export files (you can add multiple batches here)
    # Common naming patterns for ProQuest exports
    proquest_patterns = [
        "proquest*.csv",
        "wsj*.csv",
        "*proquest*.csv",
        "export*.csv"
    ]
    
    input_files = []
    for pattern in proquest_patterns:
        input_files.extend(data_dir.glob(pattern))
    
    # Remove duplicates (same file matched by multiple patterns)
    input_files = list(set(input_files))
    
    # Exclude our output file if it exists
    output_path = Path("../data/processed/wsj_apple_proquest.csv")
    input_files = [f for f in input_files if f != output_path]
    
    if not input_files:
        print("❌ No ProQuest export files found in data/raw/ directory.")
        print("\nExpected file patterns:")
        for pattern in proquest_patterns:
            print(f"  - data/raw/{pattern}")
        print("\nPlease:")
        print("  1. Export your WSJ headlines from ProQuest")
        print("  2. Save the CSV file(s) to the data/raw/ directory")
        print("  3. Run this script again")
        return
    
    print(f"Found {len(input_files)} ProQuest export file(s):")
    for f in input_files:
        print(f"  - {f.name}")
    print()
    
    try:
        # Process and merge all files
        merged_df = merge_proquest_batches(input_files)
        
        # Display summary
        display_summary(merged_df)
        
        # Save to output
        merged_df.to_csv(output_path, index=False)
        print(f"✅ Processed data saved to: {output_path}")
        print(f"\nYou can now run 'python scripts/main.py' to analyze this dataset!")
        
    except Exception as e:
        print(f"\n❌ Error during preprocessing: {e}")
        raise


if __name__ == "__main__":
    main()

