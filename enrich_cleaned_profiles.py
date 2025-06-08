import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import glob
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Gemini AI
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-pro')

def get_company_info(company_name):
    """Get company information using web search"""
    if not company_name or company_name.strip() == "":
        return None
        
    try:
        # Create a search-focused prompt for company information
        search_prompt = f"""Search and provide detailed information about this company:
Company Name: {company_name}

Please provide a comprehensive analysis including:
1. Company type and size (startup, SME, large enterprise, etc.)
2. Main industry and business focus
3. Key business areas and services
4. Company stage (startup, growth, mature, enterprise)
5. Industry category (standardized)
6. Brief company description

Keep the information factual and concise."""

        response = model.generate_content(search_prompt)
        
        if response.text:
            return {
                "company_summary": response.text.strip(),
                "search_query": f"{company_name} company information"
            }
        return None
    except Exception as e:
        print(f"Error getting company info for {company_name}: {str(e)}")
        return None

def get_current_company_from_experience(experience_list):
    """Extract current company from experience list"""
    if not experience_list:
        return None
    
    # Look for current position (EndDate is "Present" or None)
    for exp in experience_list:
        if exp.get('EndDate') in ['Present', None, ''] or str(exp.get('EndDate')).lower() == 'present':
            return {
                'company': exp.get('Company'),
                'title': exp.get('Title'),
                'start_date': exp.get('StartDate'),
                'location': exp.get('Location'),
                'description': exp.get('Description')
            }
    
    # If no current position found, return the most recent one
    if experience_list:
        recent_exp = experience_list[0]  # Assuming list is ordered by recency
        return {
            'company': recent_exp.get('Company'),
            'title': recent_exp.get('Title'),
            'start_date': recent_exp.get('StartDate'),
            'end_date': recent_exp.get('EndDate'),
            'location': recent_exp.get('Location'),
            'description': recent_exp.get('Description')
        }
    
    return None

def create_enrichment_prompt(profile_data):
    """Create a structured prompt for profile enrichment"""
    
    # Extract basic information
    full_name = f"{profile_data.get('First', '')} {profile_data.get('Last', '')}".strip()
    current_company_info = get_current_company_from_experience(profile_data.get('Experience', []))
    
    if not current_company_info:
        return None
    
    # Build education summary
    education_summary = []
    for edu in profile_data.get('Education', []):
        school = edu.get('SchoolName', '')
        degree = edu.get('Degree', '')
        field = edu.get('FieldOfStudy', '')
        start_year = edu.get('StartYear', '')
        end_year = edu.get('EndYear', '')
        
        edu_text = f"{school}"
        if degree:
            edu_text += f" - {degree}"
        if field:
            edu_text += f" in {field}"
        if start_year or end_year:
            edu_text += f" ({start_year}-{end_year})"
        
        education_summary.append(edu_text)
    
    # Build experience summary
    experience_summary = []
    for exp in profile_data.get('Experience', []):
        company = exp.get('Company', '')
        title = exp.get('Title', '')
        duration = exp.get('Duration', '')
        start_date = exp.get('StartDate', '')
        end_date = exp.get('EndDate', '')
        
        exp_text = f"{title} at {company}"
        if duration:
            exp_text += f" ({duration})"
        elif start_date and end_date:
            exp_text += f" ({start_date} - {end_date})"
        
        experience_summary.append(exp_text)

    prompt = f"""Analyze this professional profile and provide enriched insights about their career, companies, and education.
Return ONLY valid JSON without any additional text or formatting.

Profile Information:
- Full Name: {full_name}
- Graduation Year: {profile_data.get('GraduatedYear', 'N/A')}
- Program: {profile_data.get('Program', 'N/A')}
- LinkedIn URL: {profile_data.get('LinkedInURL', 'N/A')}

Current Position:
- Company: {current_company_info.get('company', 'N/A')}
- Title: {current_company_info.get('title', 'N/A')}
- Start Date: {current_company_info.get('start_date', 'N/A')}
- Location: {current_company_info.get('location', 'N/A')}

Education Background:
{chr(10).join(f"- {edu}" for edu in education_summary)}

Career History:
{chr(10).join(f"- {exp}" for exp in experience_summary[:5])}  # Limit to first 5 experiences

Required JSON structure:
{{
    "profile_summary": {{
        "full_name": "{full_name}",
        "graduation_year": {profile_data.get('GraduatedYear', 'null')},
        "program": "{profile_data.get('Program', '')}",
        "linkedin_url": "{profile_data.get('LinkedInURL', '')}"
    }},
    "current_company": {{
        "name": "{current_company_info.get('company', '')}",
        "industry_category": "string",
        "company_type": "string",
        "company_stage": "string",
        "job_title": "{current_company_info.get('title', '')}",
        "location": "{current_company_info.get('location', '')}",
        "start_date": "{current_company_info.get('start_date', '')}",
        "is_current": true
    }},
    "career_progression": [
        {{
            "company": "string",
            "title": "string",
            "duration": "string",
            "industry_category": "string",
            "company_type": "string",
            "seniority_level": "string"
        }}
    ],
    "education_analysis": [
        {{
            "school": "string",
            "degree": "string",
            "field_of_study": "string",
            "graduation_year": "number or null",
            "school_tier": "string"
        }}
    ],
    "career_insights": {{
        "primary_industry": "string",
        "current_seniority_level": "string",
        "key_expertise": ["string"],
        "years_experience_estimate": "string",
        "career_trajectory": {{
            "career_path": "string",
            "recent_transitions": "string",
            "growth_pattern": "string",
            "potential_next_roles": ["string"]
        }},
        "industry_transitions": ["string"],
        "leadership_experience": "boolean"
    }}
}}

Please ensure:
1. Industry categories are standardized (Technology, Finance, Healthcare, Consulting, etc.)
2. Company stages are one of: "Startup", "Growth", "Mature", "Enterprise"
3. Seniority levels are one of: "Entry", "Mid", "Senior", "Executive", "C-Level"
4. School tiers are one of: "Top Tier", "Mid Tier", "Regional", "Unknown"
5. All string fields are properly escaped for JSON
"""
    return prompt

def process_cleaned_profiles(input_directory="cleaned_profiles_v1", output_directory="enriched_profiles"):
    """Process all cleaned JSON profile files and enrich them"""
    
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Find all JSON files in the input directory
    json_files = glob.glob(os.path.join(input_directory, "*.json"))
    
    if not json_files:
        print(f"No JSON files found in {input_directory}")
        return
    
    enriched_profiles = []
    successful_count = 0
    
    for json_file in json_files:
        try:
            # Load the cleaned profile data
            with open(json_file, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            print(f"Processing: {profile_data.get('First', '')} {profile_data.get('Last', '')}")
            
            # Create enrichment prompt
            prompt = create_enrichment_prompt(profile_data)
            
            if prompt is None:
                print(f"Skipping profile: No current company information found")
                continue
            
            # Get enrichment from Gemini
            response = model.generate_content(prompt)
            
            # Clean the response text
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse the enriched metadata
            try:
                enriched_metadata = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error for {profile_data.get('First', '')} {profile_data.get('Last', '')}: {str(e)}")
                print(f"Raw response: {response.text}")
                continue
            
            # Get company information for current company
            current_company = enriched_metadata.get('current_company', {}).get('name')
            company_info = None
            if current_company:
                company_info = get_company_info(current_company)
            
            # Combine original data with enriched metadata
            enriched_profile = {
                "original_profile": profile_data,
                "enriched_metadata": enriched_metadata,
                "company_research": company_info,
                "enrichment_timestamp": datetime.now().isoformat(),
                "enrichment_version": "v2.0"
            }
            
            enriched_profiles.append(enriched_profile)
            
            # Save individual enriched profile
            filename = os.path.basename(json_file).replace('.json', '_enriched.json')
            output_file = os.path.join(output_directory, filename)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(enriched_profile, f, indent=2, ensure_ascii=False)
            
            successful_count += 1
            print(f"Successfully processed and saved: {filename}")
            
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
            continue
    
    # Save consolidated enriched profiles
    if enriched_profiles:
        consolidated_file = os.path.join(output_directory, "all_enriched_profiles.json")
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_profiles, f, indent=2, ensure_ascii=False)
        
        print(f"\nSuccessfully processed {successful_count} out of {len(json_files)} profiles")
        print(f"Individual files saved in: {output_directory}")
        print(f"Consolidated file saved as: {consolidated_file}")
    else:
        print("\nNo profiles were successfully processed")

if __name__ == "__main__":
    process_cleaned_profiles() 