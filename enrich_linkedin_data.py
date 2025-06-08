import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re
import glob

# Load environment variables
load_dotenv()

# Configure Gemini AI
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-pro')  # Using pro model for better search capabilities

def get_company_info(company_name, company_url):
    """Get company information using web search"""
    if not company_name or pd.isna(company_name):
        return None
        
    # Extract company domain from LinkedIn URL if available
    if company_url and pd.notna(company_url):
        match = re.search(r'company/(\d+)', company_url)
        if match:
            company_id = match.group(1)
            # Use company ID in search to get more specific results
            search_query = f"{company_name} LinkedIn company {company_id} about industry background"
        else:
            search_query = f"{company_name} company industry background"
    else:
        search_query = f"{company_name} company industry background"

    try:
        # Create a search-focused prompt
        search_prompt = f"""You are a persistent, structured data enrichment agent. Your mission is to transform and enrich alumni profile data from Asia School of Business (ASB) into a comprehensive, high-quality, and searchable knowledge base.Search and provide a brief summary about this company:
You are given a structured JSON profile representing core alumni data (education, work experience, graduation details). Your task is to reason, research, infer, and output a **new enriched JSON object** with extended metadata that supports advanced alumni analytics, searchability, and network visualization.

Company Name: {company_name}
Search Query: {search_query}

Please provide:
- CompanyInfo: Type, size, website, main industry, and stage (Startup, Growth, Mature, Enterprise).
- IndustryClassification: Standardized sector or domain (e.g., "Tech - Sustainability").
- GeoInsights: Current country, region, city from experience data.

Keep the summary concise and factual."""

        response = model.generate_content(search_prompt)
        
        if response.text:
            return {
                "company_summary": response.text.strip(),
                "search_query": search_query
            }
        return None
    except Exception as e:
        print(f"Error getting company info for {company_name}: {str(e)}")
        return None

def extract_current_company_info(profile_data):
    """Extract current company information from the profile data"""
    experience = profile_data.get('Experience', [])
    
    if not experience:
        return {
            'current_company_name': '',
            'current_job_title': '',
            'current_location': '',
            'current_start_date': '',
            'current_end_date': '',
            'current_duration': ''
        }
    
    # First experience entry is typically the current one
    current_exp = experience[0]
    
    return {
        'current_company_name': current_exp.get('Company', ''),
        'current_job_title': current_exp.get('Title', ''),
        'current_location': current_exp.get('Location', ''),
        'current_start_date': current_exp.get('StartDate', ''),
        'current_end_date': current_exp.get('EndDate', ''),
        'current_duration': current_exp.get('Duration', '')
    }

def create_profile_prompt(profile_data):
    """Create a structured prompt for profile analysis"""
    # Extract basic profile information
    full_name = f"{profile_data.get('First', '')} {profile_data.get('Last', '')}".strip()
    graduated_year = profile_data.get('GraduatedYear', '')
    program = profile_data.get('Program', '')
    
    # Extract current company info
    current_company_info = extract_current_company_info(profile_data)
    
    # Skip creating prompt if essential fields are empty
    if not (full_name or current_company_info['current_job_title'] or current_company_info['current_company_name']):
        return None

    # Extract experience history
    experience_list = profile_data.get('Experience', [])
    experience_text = ""
    for i, exp in enumerate(experience_list):
        exp_text = f"Position {i+1}: {exp.get('Title', 'N/A')} at {exp.get('Company', 'N/A')} ({exp.get('StartDate', 'N/A')} - {exp.get('EndDate', 'N/A')}) - {exp.get('Location', 'N/A')}"
        if exp.get('Description'):
            exp_text += f"\nDescription: {exp.get('Description')[:200]}..."  # Truncate long descriptions
        experience_text += exp_text + "\n"

    # Extract education history
    education_list = profile_data.get('Education', [])
    education_text = ""
    for i, edu in enumerate(education_list):
        edu_text = f"Education {i+1}: {edu.get('Degree', 'N/A')} in {edu.get('FieldOfStudy', 'N/A')} from {edu.get('SchoolName', 'N/A')} ({edu.get('StartYear', 'N/A')} - {edu.get('EndYear', 'N/A')})"
        education_text += edu_text + "\n"

    prompt = f"""Analyze this professional profile and provide enriched insights about their career, companies, and education.
Return ONLY valid JSON without any additional text or formatting.

Profile Information:
- Full Name: {full_name}
- Graduated Year: {graduated_year}
- Program: {program}
- Current Company: {current_company_info['current_company_name']}
- Current Job Title: {current_company_info['current_job_title']}
- Current Location: {current_company_info['current_location']}
- Current Position Duration: {current_company_info['current_duration']}
- Current Position Start Date: {current_company_info['current_start_date']}
- Current Position End Date: {current_company_info['current_end_date']}

Work Experience:
{experience_text}

Education:
{education_text}

Required JSON structure:
{{
    "current_company": {{
        "name": "{current_company_info['current_company_name']}",
        "industry_category": "string",
        "company_type": "string",
        "company_stage": "string",
        "job_title": "{current_company_info['current_job_title']}",
        "date_range": {{
            "start": "string (YYYY-MM format)",
            "end": "string (YYYY-MM format) or null if current"
        }}
    }},
    "list_of_companies": [
        {{
            "name": "string",
            "industry_category": "string",
            "company_type": "string",
            "job_title": "string",
            "date_range": {{
                "start": "string (YYYY-MM format)",
                "end": "string (YYYY-MM format)"
            }},
            "is_current": boolean
        }}
    ],
    "list_of_education": [
        {{
            "school": "string",
            "degree": "string",
            "field_of_study": "string",
            "date_range": {{
                "start": "string (YYYY-MM format)",
                "end": "string (YYYY-MM format)"
            }}
        }}
    ],
    "career_insights": {{
        "industry": "string",
        "seniority_level": "string",
        "key_expertise": ["string"],
        "years_experience_estimate": "string",
        "career_trajectory": {{
            "recent_transition": "string",
            "growth_path": "string",
            "potential_roles": ["string"]
        }}
    }}
}}

Please ensure:
1. All dates are in YYYY-MM format
2. Companies are listed chronologically
3. Education entries are listed chronologically
4. Industry categories are standardized
5. Company stages are one of: "Startup", "Growth", "Mature", "Enterprise"
6. Seniority levels are one of: "Entry", "Mid", "Senior", "Executive"
"""
    return prompt

def process_linkedin_data(profiles_folder='cleaned_profiles'):
    """Process JSON profile files from the specified folder"""
    # Get all JSON files from the profiles folder
    json_files = glob.glob(os.path.join(profiles_folder, '*.json'))
    
    if not json_files:
        print(f"No JSON files found in {profiles_folder} folder")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    enriched_data = []
    
    for json_file in json_files:
        try:
            # Read the JSON file
            with open(json_file, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            # Extract filename for identification
            filename = os.path.basename(json_file)
            
            # Create prompt for current profile
            prompt = create_profile_prompt(profile_data)
            
            # Skip if prompt creation failed due to insufficient data
            if prompt is None:
                print(f"Skipping {filename}: Insufficient data")
                continue
            
            # Get response from Gemini
            response = model.generate_content(prompt)
            
            # Clean the response text by removing markdown code block formatting if present
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove ```
            response_text = response_text.strip()
            
            # Extract the JSON string from the response and parse it
            try:
                enriched_metadata = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error for {filename}: {str(e)}")
                print(f"Raw response: {response.text}")
                continue
            
            # Combine original data with enriched metadata
            combined_data = profile_data.copy()
            combined_data['enriched_metadata'] = enriched_metadata
            combined_data['source_file'] = filename
            
            enriched_data.append(combined_data)
            
            full_name = f"{profile_data.get('First', '')} {profile_data.get('Last', '')}".strip()
            print(f"Successfully processed profile: {full_name} ({filename})")
            
        except Exception as e:
            print(f"Error processing file {json_file}: {str(e)}")
    
    if enriched_data:
        # Save enriched data as JSON for better readability of nested structures
        with open('enriched_linkedin_data.json', 'w', encoding='utf-8') as f:
            json.dump(enriched_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nSuccessfully processed {len(enriched_data)} profiles")
        print("Enriched data saved to 'enriched_linkedin_data.json'")
    else:
        print("\nNo profiles were successfully processed")

if __name__ == "__main__":
    process_linkedin_data('cleaned_profiles') 