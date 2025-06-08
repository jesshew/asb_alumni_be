import json
import os
from collections import Counter, defaultdict
from datetime import datetime

def load_enriched_profiles(file_path="enriched_profiles/all_enriched_profiles.json"):
    """Load the consolidated enriched profiles"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {file_path} not found. Please run the enrichment script first.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return []

def analyze_profiles(profiles):
    """Analyze the enriched profiles and generate insights"""
    
    if not profiles:
        print("No profiles to analyze.")
        return
    
    print(f"=== ENRICHED PROFILES ANALYSIS ===")
    print(f"Total Profiles Processed: {len(profiles)}")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Extract data for analysis
    industries = []
    company_stages = []
    seniority_levels = []
    graduation_years = []
    school_tiers = []
    current_companies = []
    career_paths = []
    
    for profile in profiles:
        enriched = profile.get('enriched_metadata', {})
        original = profile.get('original_profile', {})
        
        # Current company analysis
        current_company = enriched.get('current_company', {})
        if current_company.get('industry_category'):
            industries.append(current_company['industry_category'])
        if current_company.get('company_stage'):
            company_stages.append(current_company['company_stage'])
        if current_company.get('name'):
            current_companies.append(current_company['name'])
        
        # Career insights
        career_insights = enriched.get('career_insights', {})
        if career_insights.get('current_seniority_level'):
            seniority_levels.append(career_insights['current_seniority_level'])
        if career_insights.get('career_trajectory', {}).get('career_path'):
            career_paths.append(career_insights['career_trajectory']['career_path'])
        
        # Education analysis
        education_analysis = enriched.get('education_analysis', [])
        for edu in education_analysis:
            if edu.get('school_tier'):
                school_tiers.append(edu['school_tier'])
        
        # Graduation year from original profile
        if original.get('GraduatedYear'):
            graduation_years.append(original['GraduatedYear'])
    
    # Industry Distribution
    print("\n📊 INDUSTRY DISTRIBUTION")
    print("-" * 30)
    industry_counts = Counter(industries)
    for industry, count in industry_counts.most_common():
        percentage = (count / len(profiles)) * 100
        print(f"{industry}: {count} ({percentage:.1f}%)")
    
    # Company Stage Distribution
    print("\n🏢 COMPANY STAGE DISTRIBUTION")
    print("-" * 30)
    stage_counts = Counter(company_stages)
    for stage, count in stage_counts.most_common():
        percentage = (count / len(profiles)) * 100
        print(f"{stage}: {count} ({percentage:.1f}%)")
    
    # Seniority Level Distribution
    print("\n👔 SENIORITY LEVEL DISTRIBUTION")
    print("-" * 30)
    seniority_counts = Counter(seniority_levels)
    for level, count in seniority_counts.most_common():
        percentage = (count / len(profiles)) * 100
        print(f"{level}: {count} ({percentage:.1f}%)")
    
    # School Tier Distribution
    print("\n🎓 EDUCATION TIER DISTRIBUTION")
    print("-" * 30)
    school_counts = Counter(school_tiers)
    for tier, count in school_counts.most_common():
        percentage = (count / len(school_tiers)) * 100 if school_tiers else 0
        print(f"{tier}: {count} ({percentage:.1f}%)")
    
    # Graduation Year Distribution
    print("\n📅 GRADUATION YEAR DISTRIBUTION")
    print("-" * 30)
    year_counts = Counter(graduation_years)
    for year, count in sorted(year_counts.items()):
        percentage = (count / len(profiles)) * 100
        print(f"{year}: {count} ({percentage:.1f}%)")
    
    # Career Path Analysis
    print("\n🚀 CAREER PATH ANALYSIS")
    print("-" * 30)
    path_counts = Counter(career_paths)
    for path, count in path_counts.most_common(10):  # Top 10 career paths
        percentage = (count / len(profiles)) * 100
        print(f"{path}: {count} ({percentage:.1f}%)")
    
    # Current Companies
    print("\n🏭 CURRENT COMPANIES")
    print("-" * 30)
    company_counts = Counter(current_companies)
    for company, count in company_counts.most_common(10):  # Top 10 companies
        print(f"{company}: {count}")
    
    # Key Expertise Analysis
    print("\n💡 KEY EXPERTISE ANALYSIS")
    print("-" * 30)
    all_expertise = []
    for profile in profiles:
        expertise = profile.get('enriched_metadata', {}).get('career_insights', {}).get('key_expertise', [])
        all_expertise.extend(expertise)
    
    expertise_counts = Counter(all_expertise)
    for skill, count in expertise_counts.most_common(15):  # Top 15 skills
        percentage = (count / len(profiles)) * 100
        print(f"{skill}: {count} ({percentage:.1f}%)")
    
    # Leadership Experience
    print("\n👑 LEADERSHIP EXPERIENCE")
    print("-" * 30)
    leadership_count = 0
    for profile in profiles:
        has_leadership = profile.get('enriched_metadata', {}).get('career_insights', {}).get('leadership_experience', False)
        if has_leadership:
            leadership_count += 1
    
    leadership_percentage = (leadership_count / len(profiles)) * 100
    print(f"Profiles with Leadership Experience: {leadership_count} ({leadership_percentage:.1f}%)")
    print(f"Profiles without Leadership Experience: {len(profiles) - leadership_count} ({100 - leadership_percentage:.1f}%)")

def generate_individual_summaries(profiles, output_file="enriched_profiles/profile_summaries.txt"):
    """Generate individual profile summaries"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=== INDIVIDUAL PROFILE SUMMARIES ===\n\n")
        
        for i, profile in enumerate(profiles, 1):
            original = profile.get('original_profile', {})
            enriched = profile.get('enriched_metadata', {})
            company_research = profile.get('company_research', {})
            
            # Basic info
            full_name = enriched.get('profile_summary', {}).get('full_name', 'Unknown')
            graduation_year = original.get('GraduatedYear', 'Unknown')
            program = original.get('Program', 'Unknown')
            
            # Current position
            current_company = enriched.get('current_company', {})
            company_name = current_company.get('name', 'Unknown')
            job_title = current_company.get('job_title', 'Unknown')
            industry = current_company.get('industry_category', 'Unknown')
            
            # Career insights
            career_insights = enriched.get('career_insights', {})
            seniority = career_insights.get('current_seniority_level', 'Unknown')
            experience_years = career_insights.get('years_experience_estimate', 'Unknown')
            
            f.write(f"{i}. {full_name}\n")
            f.write(f"   Graduation: {graduation_year} | Program: {program}\n")
            f.write(f"   Current: {job_title} at {company_name}\n")
            f.write(f"   Industry: {industry} | Seniority: {seniority} | Experience: {experience_years}\n")
            
            if company_research and company_research.get('company_summary'):
                f.write(f"   Company Info: {company_research['company_summary'][:100]}...\n")
            
            f.write("\n")
    
    print(f"\nIndividual summaries saved to: {output_file}")

def main():
    """Main analysis function"""
    profiles = load_enriched_profiles()
    
    if profiles:
        analyze_profiles(profiles)
        generate_individual_summaries(profiles)
        
        print(f"\n✅ Analysis complete!")
        print(f"📁 Enriched profiles directory: enriched_profiles/")
        print(f"📊 Individual summaries: enriched_profiles/profile_summaries.txt")
    else:
        print("❌ No profiles found to analyze.")

if __name__ == "__main__":
    main() 