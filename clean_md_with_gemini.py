import os
import sys
import argparse
import google.generativeai as genai
from dotenv import load_dotenv
import json
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure Gemini AI
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
if not GOOGLE_API_KEY:
    print("Error: GEMINI_API_KEY not found in environment variables")
    sys.exit(1)

genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-pro')

def load_cleaning_prompt():
    """Load the LLM cleaning prompt from llm_cleaning.py"""
    try:
        # Import the prompt from llm_cleaning.py
        from llm_cleaning import llm_cleaning_prompt
        return llm_cleaning_prompt
    except ImportError as e:
        print(f"Error importing llm_cleaning_prompt: {str(e)}")
        print("Make sure llm_cleaning.py exists and contains llm_cleaning_prompt variable")
        sys.exit(1)

def read_markdown_file(file_path):
    """Read and return the contents of a markdown file"""
    try:
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check if file has .md extension
        if file_path.suffix.lower() != '.md':
            raise ValueError(f"File '{file_path}' does not have .md extension")
        
        # Read file contents
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if not content.strip():
            raise ValueError(f"File '{file_path}' is empty")
        
        return content
    
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        return None
    except PermissionError:
        print(f"Error: Permission denied reading file '{file_path}'")
        return None
    except UnicodeDecodeError:
        print(f"Error: Unable to decode file '{file_path}' as UTF-8")
        return None
    except Exception as e:
        print(f"Error reading file '{file_path}': {str(e)}")
        return None

def clean_markdown_with_gemini(markdown_content, cleaning_prompt):
    """Send markdown content to Gemini with cleaning prompt and return the result"""
    try:
        # Combine the cleaning prompt with the markdown content
        full_prompt = f"{cleaning_prompt}\n\nMarkdown Input:\n{markdown_content}"
        
        # Generate response from Gemini
        response = model.generate_content(full_prompt)
        
        if not response.text:
            raise ValueError("Empty response from Gemini API")
        
        # Clean the response text by removing markdown code block formatting if present
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]  # Remove ```json
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove ```
        response_text = response_text.strip()
        
        # Validate that the response is valid JSON
        try:
            json.loads(response_text)
        except json.JSONDecodeError:
            print("Warning: Response is not valid JSON format")
        
        return response_text
    
    except Exception as e:
        print(f"Error processing with Gemini API: {str(e)}")
        return None

def get_markdown_files(input_folder):
    """Get all markdown files from the input folder"""
    input_path = Path(input_folder)
    
    if not input_path.exists():
        print(f"Error: Input folder '{input_folder}' does not exist")
        return []
    
    if not input_path.is_dir():
        print(f"Error: '{input_folder}' is not a directory")
        return []
    
    # Find all .md files in the folder
    markdown_files = list(input_path.glob("*.md"))
    
    if not markdown_files:
        print(f"Warning: No markdown files found in '{input_folder}'")
    
    return markdown_files

def create_output_folder(output_folder):
    """Create output folder if it doesn't exist"""
    output_path = Path(output_folder)
    
    try:
        output_path.mkdir(parents=True, exist_ok=True)
        return True
    except PermissionError:
        print(f"Error: Permission denied creating output folder '{output_folder}'")
        return False
    except Exception as e:
        print(f"Error creating output folder '{output_folder}': {str(e)}")
        return False

def save_json_file(content, output_path):
    """Save cleaned content as JSON file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            # Try to parse and pretty-print the JSON
            try:
                json_data = json.loads(content)
                json.dump(json_data, file, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                # If not valid JSON, save as-is
                file.write(content)
        return True
    except Exception as e:
        print(f"Error saving file '{output_path}': {str(e)}")
        return False

def process_folder(input_folder, output_folder, verbose=False):
    """Process all markdown files in input folder and save to output folder"""
    # Load the cleaning prompt
    if verbose:
        print("Loading cleaning prompt...")
    cleaning_prompt = load_cleaning_prompt()
    
    # Get all markdown files
    if verbose:
        print(f"Scanning for markdown files in '{input_folder}'...")
    markdown_files = get_markdown_files(input_folder)
    
    if not markdown_files:
        return
    
    # Create output folder
    if verbose:
        print(f"Creating output folder '{output_folder}'...")
    if not create_output_folder(output_folder):
        return
    
    # Process each file
    successful_count = 0
    failed_count = 0
    
    for md_file in markdown_files:
        if verbose:
            print(f"\nProcessing: {md_file.name}")
        
        # Read markdown content
        markdown_content = read_markdown_file(md_file)
        if markdown_content is None:
            failed_count += 1
            continue
        
        # Clean with Gemini
        if verbose:
            print(f"  Sending to Gemini API...")
        cleaned_content = clean_markdown_with_gemini(markdown_content, cleaning_prompt)
        if cleaned_content is None:
            failed_count += 1
            continue
        
        # Generate output filename (replace .md with .json)
        output_filename = md_file.stem + '.json'
        output_path = Path(output_folder) / output_filename
        
        # Save the cleaned content
        if verbose:
            print(f"  Saving to: {output_path}")
        if save_json_file(cleaned_content, output_path):
            successful_count += 1
            if not verbose:
                print(f"✓ Processed: {md_file.name} -> {output_filename}")
        else:
            failed_count += 1
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"PROCESSING SUMMARY:")
    print(f"{'='*50}")
    print(f"Total files found: {len(markdown_files)}")
    print(f"Successfully processed: {successful_count}")
    print(f"Failed: {failed_count}")
    print(f"Output folder: {output_folder}")

def main():
    """Main function to handle command line arguments and orchestrate the cleaning process"""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Clean LinkedIn profile markdown files using Google Gemini AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clean_md_with_gemini.py input_folder output_folder
  python clean_md_with_gemini.py ./profiles ./cleaned_profiles --verbose
        """
    )
    
    parser.add_argument(
        'input_folder',
        help='Path to the folder containing markdown (.md) files to process'
    )
    
    parser.add_argument(
        'output_folder',
        help='Path to the folder where cleaned JSON files will be saved'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Input folder: {args.input_folder}")
        print(f"Output folder: {args.output_folder}")
    
    try:
        # Process the entire folder
        process_folder(args.input_folder, args.output_folder, args.verbose)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 