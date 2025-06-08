# Profile Enrichment System v2.0

This system enriches cleaned LinkedIn profile data using AI-powered analysis and company research.

## Overview

The enrichment system processes cleaned JSON profile files and adds:
- **Career insights** and trajectory analysis
- **Company information** with industry categorization
- **Education analysis** with school tier classification
- **Seniority level** and experience estimation
- **Industry transitions** and career path analysis
- **Company research** using Google's Gemini AI

## Files Structure

```
├── enrich_cleaned_profiles.py      # Main enrichment script
├── analyze_enriched_profiles.py    # Analysis and reporting script
├── cleaned_profiles_v1/            # Input directory (cleaned JSON profiles)
├── enriched_profiles/              # Output directory
│   ├── *_enriched.json            # Individual enriched profiles
│   ├── all_enriched_profiles.json # Consolidated enriched data
│   └── profile_summaries.txt      # Human-readable summaries
└── README_ENRICHMENT.md           # This documentation
```

## Input Format

The system expects cleaned JSON profiles with this structure:

```json
{
  "First": "John",
  "Last": "Doe",
  "GraduatedYear": 2018,
  "Program": "Master of Business Administration - MBA",
  "LinkedInURL": "https://www.linkedin.com/in/johndoe",
  "Education": [
    {
      "SchoolName": "Asia School of Business",
      "Degree": "MBA",
      "FieldOfStudy": "Business Administration",
      "StartYear": 2016,
      "EndYear": 2018
    }
  ],
  "Experience": [
    {
      "Title": "Senior Manager",
      "Company": "Tech Corp",
      "StartDate": "Jan 2020",
      "EndDate": "Present",
      "Duration": "4 yrs",
      "Location": "Singapore",
      "Description": "Leading product development..."
    }
  ]
}
```

## Output Format

Each enriched profile contains:

```json
{
  "original_profile": { /* Original cleaned data */ },
  "enriched_metadata": {
    "profile_summary": {
      "full_name": "John Doe",
      "graduation_year": 2018,
      "program": "MBA",
      "linkedin_url": "https://linkedin.com/in/johndoe"
    },
    "current_company": {
      "name": "Tech Corp",
      "industry_category": "Technology",
      "company_type": "Enterprise",
      "company_stage": "Mature",
      "job_title": "Senior Manager",
      "location": "Singapore",
      "start_date": "Jan 2020",
      "is_current": true
    },
    "career_progression": [ /* Career history analysis */ ],
    "education_analysis": [ /* Education tier analysis */ ],
    "career_insights": {
      "primary_industry": "Technology",
      "current_seniority_level": "Senior",
      "key_expertise": ["Product Management", "Strategy"],
      "years_experience_estimate": "8+",
      "career_trajectory": {
        "career_path": "Product Management",
        "recent_transitions": "Individual contributor to management",
        "growth_pattern": "Steady progression",
        "potential_next_roles": ["Director", "VP of Product"]
      },
      "industry_transitions": ["Finance to Technology"],
      "leadership_experience": true
    }
  },
  "company_research": {
    "company_summary": "Detailed company information...",
    "search_query": "Tech Corp company information"
  },
  "enrichment_timestamp": "2025-06-08T17:23:40.419897",
  "enrichment_version": "v2.0"
}
```

## Usage

### 1. Environment Setup

Ensure you have the required environment variables:

```bash
# .env file
GEMINI_API_KEY=your_google_gemini_api_key
```

### 2. Install Dependencies

```bash
pip install google-generativeai python-dotenv
```

### 3. Run Enrichment

```bash
# Process all cleaned profiles in cleaned_profiles_v1/
python enrich_cleaned_profiles.py

# Or specify custom directories
python -c "
from enrich_cleaned_profiles import process_cleaned_profiles
process_cleaned_profiles('input_dir', 'output_dir')
"
```

### 4. Analyze Results

```bash
# Generate analysis and summaries
python analyze_enriched_profiles.py
```

## Key Features

### 🔍 Company Research
- Uses Gemini AI to search for current company information
- Provides industry categorization and company stage analysis
- Includes company size, type, and business focus

### 📊 Career Analysis
- **Seniority Levels**: Entry, Mid, Senior, Executive, C-Level
- **Industry Categories**: Technology, Finance, Healthcare, Consulting, etc.
- **Company Stages**: Startup, Growth, Mature, Enterprise
- **School Tiers**: Top Tier, Mid Tier, Regional, Unknown

### 🚀 Career Insights
- Experience estimation based on career progression
- Industry transition analysis
- Leadership experience detection
- Potential next role suggestions

### 📈 Analytics Dashboard
The analysis script provides:
- Industry distribution across profiles
- Company stage breakdown
- Seniority level distribution
- Education tier analysis
- Key expertise trends
- Career path patterns

## Standardized Classifications

### Industry Categories
- Technology
- Finance / Financial Services
- Healthcare
- Consulting
- Education
- Retail
- Manufacturing
- Government
- Non-profit
- And more...

### Company Stages
- **Startup**: Early-stage companies
- **Growth**: Scaling companies
- **Mature**: Established companies
- **Enterprise**: Large corporations

### Seniority Levels
- **Entry**: 0-2 years experience
- **Mid**: 3-7 years experience
- **Senior**: 8-15 years experience
- **Executive**: 15+ years, leadership roles
- **C-Level**: C-suite executives

### School Tiers
- **Top Tier**: Ivy League, top global universities
- **Mid Tier**: Well-known regional universities
- **Regional**: Local/regional institutions
- **Unknown**: Unrecognized or missing information

## Error Handling

The system includes robust error handling:
- Skips profiles with insufficient data
- Handles JSON parsing errors gracefully
- Continues processing if individual profiles fail
- Logs errors for debugging

## Performance Considerations

- **Rate Limiting**: Gemini API calls are made sequentially to avoid rate limits
- **Caching**: Company research results could be cached for repeated companies
- **Batch Processing**: Processes all profiles in a single run
- **Memory Efficient**: Processes one profile at a time

## Customization

### Custom Prompts
Modify the `create_enrichment_prompt()` function to adjust AI analysis parameters.

### Additional Fields
Extend the JSON structure in the prompt to capture more insights.

### Custom Analysis
Add new analysis functions to `analyze_enriched_profiles.py` for specific insights.

## Troubleshooting

### Common Issues

1. **Missing API Key**
   ```
   Error: GEMINI_API_KEY not found
   Solution: Add your Gemini API key to .env file
   ```

2. **JSON Parsing Errors**
   ```
   Error: JSON parsing error for [Name]
   Solution: Check AI response format, may need prompt adjustment
   ```

3. **No Profiles Found**
   ```
   Error: No JSON files found in cleaned_profiles_v1
   Solution: Ensure cleaned profile files exist in the input directory
   ```

### Debug Mode
Add debug prints to see AI responses:
```python
print(f"Raw response: {response.text}")
```

## Future Enhancements

- [ ] Company information caching
- [ ] Batch API calls for better performance
- [ ] Additional career metrics
- [ ] Industry-specific analysis
- [ ] Export to different formats (Excel, CSV)
- [ ] Web dashboard for results visualization

## Version History

- **v2.0**: Complete rewrite for cleaned JSON format
- **v1.0**: Original CSV-based enrichment system

---

For questions or issues, please check the error logs and ensure all dependencies are properly installed. 