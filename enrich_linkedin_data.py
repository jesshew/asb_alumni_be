import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

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
        search_prompt = f"""Search and provide a brief summary about this company:
Company Name: {company_name}
Search Query: {search_query}

Please provide:
1. Company type and size
2. Main industry and focus
3. Key business areas
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

def create_profile_prompt(row):
    """Create a structured prompt for profile analysis"""
    # Handle NaN values by replacing them with empty strings
    profile_data = {
        'fullName': str(row['fullName']) if pd.notna(row['fullName']) else '',
        'jobTitle': str(row['jobTitle']) if pd.notna(row['jobTitle']) else '',
        'jobTitle2': str(row['jobTitle2']) if pd.notna(row['jobTitle2']) else '',
        'company': str(row['company']) if pd.notna(row['company']) else '',
        'company2': str(row['company2']) if pd.notna(row['company2']) else '',
        'location': str(row['location']) if pd.notna(row['location']) else '',
        'school': str(row['school']) if pd.notna(row['school']) else '',
        'schoolDegree': str(row['schoolDegree']) if pd.notna(row['schoolDegree']) else '',
        'school2': str(row['school2']) if pd.notna(row['school2']) else '',
        'schoolDegree2': str(row['schoolDegree2']) if pd.notna(row['schoolDegree2']) else '',
        'jobDateRange': str(row['jobDateRange']) if pd.notna(row['jobDateRange']) else '',
        'jobDateRange2': str(row['jobDateRange2']) if pd.notna(row['jobDateRange2']) else '',
        'schoolDateRange': str(row['schoolDateRange']) if pd.notna(row['schoolDateRange']) else '',
        'schoolDateRange2': str(row['schoolDateRange2']) if pd.notna(row['schoolDateRange2']) else '',
        'industry': str(row['industry']) if pd.notna(row['industry']) else ''
    }
    
    # Skip creating prompt if essential fields are empty
    if not (profile_data['fullName'] or profile_data['jobTitle'] or profile_data['company']):
        return None

    # Create company history text with proper handling of empty values
    current_company_text = f"{profile_data['company']} as {profile_data['jobTitle']}" if profile_data['company'] and profile_data['jobTitle'] else profile_data['company'] or profile_data['jobTitle'] or 'Not specified'
    previous_company_text = f"{profile_data['company2']} as {profile_data['jobTitle2']}" if profile_data['company2'] and profile_data['jobTitle2'] else profile_data['company2'] or profile_data['jobTitle2'] or 'Not specified'

    prompt = f"""Analyze this professional profile and provide enriched insights about their career, companies, and education.
Return ONLY valid JSON without any additional text or formatting.

Profile Information:
- Full Name: {profile_data['fullName']}
- Current Position: {current_company_text}
- Current Job Duration: {profile_data['jobDateRange']}
- Previous Position: {previous_company_text}
- Previous Job Duration: {profile_data['jobDateRange2']}
- Industry: {profile_data['industry']}
- Location: {profile_data['location']}
- Education 1: {profile_data['school']} - {profile_data['schoolDegree']} ({profile_data['schoolDateRange']})
- Education 2: {profile_data['school2']} - {profile_data['schoolDegree2']} ({profile_data['schoolDateRange2']})

Required JSON structure:
{{
    "current_company": {{
        "name": "{profile_data['company']}",
        "industry_category": "string",
        "company_type": "string",
        "company_stage": "string",
        "job_title": "{profile_data['jobTitle']}",
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

def process_linkedin_data(csv_path):
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Filter out rows with errors and empty/NaN essential fields
    df = df[
        df['error'].isna() & 
        df['fullName'].notna() & 
        ((df['jobTitle'].notna()) | (df['company'].notna()))
    ]
    
    enriched_data = []
    
    for index, row in df.iterrows():
        try:
            # Create prompt for current profile
            prompt = create_profile_prompt(row)
            
            # Skip if prompt creation failed due to insufficient data
            if prompt is None:
                print(f"Skipping row {index}: Insufficient data")
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
                print(f"JSON parsing error for {row['fullName']}: {str(e)}")
                print(f"Raw response: {response.text}")
                continue
            
            # Combine original data with enriched metadata
            profile_data = row.to_dict()
            profile_data['enriched_metadata'] = enriched_metadata
            
            enriched_data.append(profile_data)
            
            print(f"Successfully processed profile: {row['fullName']}")
            
        except Exception as e:
            print(f"Error processing profile {row['fullName']}: {str(e)}")
    
    if enriched_data:
        # Save enriched data
        enriched_df = pd.DataFrame(enriched_data)
        enriched_df.to_csv('enriched_linkedin_data.csv', index=False)
        
        # Also save as JSON for better readability of nested structures
        with open('enriched_linkedin_data.json', 'w') as f:
            json.dump(enriched_data, f, indent=2)
        
        print(f"\nSuccessfully processed {len(enriched_data)} profiles")
    else:
        print("\nNo profiles were successfully processed")

if __name__ == "__main__":
    process_linkedin_data('scraped_result.csv') 