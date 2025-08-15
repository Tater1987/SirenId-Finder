import os
import re
from pathlib import Path

class CarcolsMetaExtractor:
    def __init__(self, base_directories=None):
        # Handle both single directory (string) and multiple directories (list)
        if base_directories is None:
            self.base_directories = ["emergency"]
        elif isinstance(base_directories, str):
            self.base_directories = [base_directories]
        else:
            self.base_directories = base_directories
        self.results = []
    
    def find_carcols_meta_files(self):
        """Find all carcols.meta files in all specified directories and their subdirectories"""
        meta_files = []
        
        for base_directory in self.base_directories:
            if not os.path.exists(base_directory):
                print(f"Warning: Directory '{base_directory}' not found! Skipping...")
                continue
            
            print(f"Searching in directory: {base_directory}")
            
            # Walk through all directories and subdirectories
            for root, dirs, files in os.walk(base_directory):
                for file in files:
                    if file.lower() == 'carcols.meta':
                        file_path = os.path.join(root, file)
                        # Get the folder name (parent directory of the file)
                        folder_name = os.path.basename(root)
                        # Get relative path from the base directory for better identification
                        relative_path = os.path.relpath(file_path, base_directory)
                        meta_files.append({
                            'folder': folder_name,
                            'file_path': file_path,
                            'relative_path': relative_path,
                            'base_directory': base_directory
                        })
        
        return meta_files
    
    def extract_id_values(self, file_path):
        """Extract all id values from within <Sirens> to </Sirens> sections (case-sensitive)"""
        id_values = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find all <Sirens> to </Sirens> sections (case-sensitive - capital S only)
            sirens_pattern = r'<Sirens>(.*?)</Sirens>'
            sirens_sections = re.findall(sirens_pattern, content, re.DOTALL)
            
            for section in sirens_sections:
                # Within each sirens section, find all <id value= patterns
                # Pattern for quoted values: <id value="ABC123">
                quoted_pattern = r'<id\s+value="([^"]+)"'
                quoted_matches = re.findall(quoted_pattern, section, re.IGNORECASE)
                id_values.extend(quoted_matches)
                
                # Pattern for unquoted values: <id value=ABC123>
                unquoted_pattern = r'<id\s+value=([^>\s]+)'
                unquoted_matches = re.findall(unquoted_pattern, section, re.IGNORECASE)
                # Filter out quoted matches to avoid duplicates
                unquoted_matches = [match for match in unquoted_matches if not match.startswith('"')]
                id_values.extend(unquoted_matches)
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
        
        return id_values
    
    def process_all_files(self):
        """Process all carcols.meta files and extract ID values"""
        meta_files = self.find_carcols_meta_files()
        
        if not meta_files:
            print("No carcols.meta files found!")
            return
        
        print(f"Found {len(meta_files)} carcols.meta files")
        print("Processing files...\n")
        
        for meta_info in meta_files:
            id_values = self.extract_id_values(meta_info['file_path'])
            
            if id_values:
                for id_value in id_values:
                    result = {
                        'folder': meta_info['folder'],
                        'file_path': meta_info['relative_path'],
                        'id_value': id_value,
                        'base_directory': meta_info['base_directory']
                    }
                    self.results.append(result)
                    print(f"Directory: {meta_info['base_directory']} | Folder: {meta_info['folder']} | ID: {id_value}")
            # Removed the else block - no longer prints folders with no ID values found
        
        print(f"\nTotal ID values extracted: {len(self.results)}")
    
    def natural_sort_key(self, text):
        """Generate a key for natural sorting (handles numbers properly)"""
        import re
        return [int(x) if x.isdigit() else x.lower() for x in re.split(r'(\d+)', text)]
    
    def save_to_txt(self, output_file="carcols_ids.txt"):
        """Save extracted data to text file"""
        if not self.results:
            print("No data to save!")
            return
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Carcols.meta ID Values Extraction Report\n")
            f.write("=" * 50 + "\n\n")
            
            # Group by folder for cleaner output
            folders = {}
            for result in self.results:
                folder = result['folder']
                if folder not in folders:
                    folders[folder] = []
                folders[folder].append(result['id_value'])
            
            # Write grouped results (only sort IDs within each folder)
            for folder, ids in folders.items():
                sorted_ids = sorted(ids, key=self.natural_sort_key)
                f.write(f"Folder: {folder}\n")
                f.write("-" * 30 + "\n")
                for id_value in sorted_ids:
                    f.write(f"ID: {id_value}\n")
                f.write("\n")
            
            # Write summary
            f.write("=" * 50 + "\n")
            f.write(f"Total folders processed: {len(folders)}\n")
            f.write(f"Total ID values found: {len(self.results)}\n")
        
        print(f"\nResults saved to {output_file}")
    
    def check_for_duplicates(self):
        """Check for duplicate ID values and return duplicate info"""
        id_map = {}
        duplicates = {}
        
        # Build a map of ID values to their locations
        for result in self.results:
            id_value = result['id_value']
            if id_value not in id_map:
                id_map[id_value] = []
            id_map[id_value].append(result)
        
        # Find duplicates
        for id_value, locations in id_map.items():
            if len(locations) > 1:
                duplicates[id_value] = locations
        
        return duplicates
    
    def save_simple_format(self, output_file="carcols_ids_simple.txt"):
        """Save in simple format: id_value | folder_name (sorted by ID numerically)"""
        if not self.results:
            print("No data to save!")
            return
        
        # Sort results by ID value numerically
        sorted_results = sorted(self.results, key=lambda x: self.natural_sort_key(x['id_value']))
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in sorted_results:
                f.write(f"{result['id_value']} | {result['folder']}\n")
        
        print(f"Simple format saved to {output_file}")
    
    def save_duplicates_report(self, output_file="duplicate_ids.txt"):
        """Save duplicate ID values report (IDs sorted numerically)"""
        duplicates = self.check_for_duplicates()
        
        if not duplicates:
            print("No duplicate ID values found!")
            return
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("DUPLICATE ID VALUES REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Sort duplicate IDs numerically
            for id_value in sorted(duplicates.keys(), key=self.natural_sort_key):
                locations = duplicates[id_value]
                f.write(f"ID: {id_value} (found {len(locations)} times)\n")
                f.write("-" * 30 + "\n")
                for location in locations:
                    f.write(f"  Folder: {location['folder']}\n")
                    f.write(f"  Path: {location['file_path']}\n")
                f.write("\n")
            
            f.write("=" * 50 + "\n")
            f.write(f"Total duplicate IDs: {len(duplicates)}\n")
            total_duplicates = sum(len(locations) for locations in duplicates.values())
            f.write(f"Total duplicate instances: {total_duplicates}\n")
        
        print(f"Duplicate report saved to {output_file}")
        print(f"Found {len(duplicates)} duplicate IDs with {sum(len(locations) for locations in duplicates.values())} total instances")

def main():
    # Initialize the extractor with multiple directories
    # You can specify multiple directories like this:
    directories_to_search = [
        "[emergency]",
        "[Vehicles]",
    ]
    
    # Or use a single directory:
    # directories_to_search = "[emergency]"
    
    extractor = CarcolsMetaExtractor(directories_to_search)
    
    # Process all carcols.meta files
    extractor.process_all_files()
    
    # Save results to text files
    extractor.save_to_txt()
    extractor.save_simple_format()
    
    # Check for and save duplicate IDs
    extractor.save_duplicates_report()

if __name__ == "__main__":
    main()
