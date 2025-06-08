import os
import csv
import time
import json
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import logging

class LinkedInScraper:
    def __init__(self):
        self.setup_logging()
        self.driver = None
        self.wait = None
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('linkedin_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self):
        """Initialize Chrome driver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 20)
        
    def login_to_linkedin(self):
        """Login to LinkedIn using environment variables"""
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')
        
        if not email or not password:
            raise ValueError("Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
        
        self.logger.info("Attempting to login to LinkedIn...")
        
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(random.uniform(2, 4))
            
            # Enter email
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            email_field.clear()
            email_field.send_keys(email)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(random.uniform(3, 5))
            
            # Check if login was successful
            if "feed" in self.driver.current_url or "in/" in self.driver.current_url:
                self.logger.info("Successfully logged in to LinkedIn")
                return True
            else:
                self.logger.error("Login may have failed - unexpected URL")
                return False
                
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False
    
    def load_urls_from_csv(self, csv_file_path):
        """Load LinkedIn URLs from CSV file"""
        try:
            df = pd.read_csv(csv_file_path)
            if 'LinkedIn' not in df.columns:
                raise ValueError("CSV file must contain a 'LinkedIn' column")
            
            # Filter out empty URLs
            urls = df['LinkedIn'].dropna().tolist()
            urls = [url.strip() for url in urls if url.strip()]
            
            self.logger.info(f"Loaded {len(urls)} LinkedIn URLs from CSV")
            return urls
            
        except Exception as e:
            self.logger.error(f"Error loading CSV file: {str(e)}")
            return []
    
    def extract_profile_data(self, profile_url):
        """Extract all available data from a LinkedIn profile"""
        try:
            self.logger.info(f"Scraping profile: {profile_url}")
            
            # Navigate to profile
            self.driver.get(profile_url)
            time.sleep(random.uniform(3, 6))
            
            # Scroll to load dynamic content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            profile_data = {
                'URL': profile_url,
                'Scraped_At': datetime.now().isoformat(),
                'First': '',
                'Preferred': '',
                'Last': '',
                'Gender': '',
                'Graduated_Year': '',
                'Intake': '',
                'Program': '',
                'Graduation_Awards': '',
                'Birthdate': '',
                'LinkedIn': profile_url,
                'Citizenship_Primary': '',
                'Region_Primary': '',
                'Citizenship_Secondary': '',
                'Phone': '',
                'Organizations_Pre_ASB': '',
                'City_Alumni': '',
                'Country_Alumni': '',
                'Current_Job_Title': '',
                'Current_Job_Location_City': '',
                'Current_Job_Location_Country': '',
                'Current_Company_Name': '',
                'Current_Start_Date': '',
                'Additional_Notes': '',
                'Are_they_in_Startup_ecosystem': '',
                'Startup_Description': ''
            }
            
            # Extract name
            name_element = soup.find('h1', class_='text-heading-xlarge')
            if name_element:
                full_name = name_element.get_text(strip=True)
                name_parts = full_name.split()
                if len(name_parts) >= 2:
                    profile_data['First'] = name_parts[0]
                    profile_data['Last'] = name_parts[-1]
                    if len(name_parts) > 2:
                        profile_data['Preferred'] = ' '.join(name_parts[1:-1])
                elif len(name_parts) == 1:
                    profile_data['First'] = name_parts[0]
            
            # Extract headline/current position
            headline_element = soup.find('div', class_='text-body-medium')
            if headline_element:
                headline = headline_element.get_text(strip=True)
                profile_data['Current_Job_Title'] = headline
            
            # Extract location
            location_element = soup.find('span', class_='text-body-small')
            if location_element:
                location = location_element.get_text(strip=True)
                profile_data['Current_Job_Location_City'] = location
            
            # Extract experience section
            experience_section = soup.find('section', {'data-section': 'experience'}) or \
                               soup.find('div', id='experience') or \
                               soup.find('section', class_=lambda x: x and 'experience' in x.lower())
            
            if experience_section:
                # Look for current position
                experience_items = experience_section.find_all('div', class_=lambda x: x and 'experience-item' in str(x))
                if not experience_items:
                    experience_items = experience_section.find_all('li')
                
                for item in experience_items[:1]:  # Get first (most recent) experience
                    # Company name
                    company_elements = item.find_all('span', class_='t-14') + \
                                     item.find_all('span', class_='t-normal') + \
                                     item.find_all('h4') + \
                                     item.find_all('h3')
                    
                    for elem in company_elements:
                        text = elem.get_text(strip=True)
                        if text and len(text) > 2:
                            if not profile_data['Current_Company_Name']:
                                profile_data['Current_Company_Name'] = text
                                break
            
            # Extract education section for graduation year
            education_section = soup.find('section', {'data-section': 'education'}) or \
                              soup.find('div', id='education') or \
                              soup.find('section', class_=lambda x: x and 'education' in str(x).lower())
            
            if education_section:
                # Look for years in education section
                year_patterns = education_section.find_all(text=lambda text: text and any(year in text for year in ['2020', '2021', '2022', '2023', '2024', '2025']))
                for pattern in year_patterns:
                    if pattern.strip():
                        profile_data['Graduated_Year'] = pattern.strip()
                        break
            
            # Extract about section
            about_section = soup.find('section', {'data-section': 'summary'}) or \
                          soup.find('div', id='about') or \
                          soup.find('section', class_=lambda x: x and 'about' in str(x).lower())
            
            if about_section:
                about_text = about_section.get_text(strip=True)
                profile_data['Additional_Notes'] = about_text[:500] if about_text else ''
            
            # Check for startup indicators
            page_text = soup.get_text().lower()
            startup_keywords = ['startup', 'entrepreneur', 'founder', 'co-founder', 'ceo', 'cto', 'venture']
            
            if any(keyword in page_text for keyword in startup_keywords):
                profile_data['Are_they_in_Startup_ecosystem'] = 'Yes'
                # Extract startup description from headline or about
                startup_desc = profile_data['Current_Job_Title'] or profile_data['Additional_Notes']
                profile_data['Startup_Description'] = startup_desc[:200] if startup_desc else ''
            else:
                profile_data['Are_they_in_Startup_ecosystem'] = 'No'
            
            # Print all available data
            print(f"\n{'='*60}")
            print(f"PROFILE DATA FOR: {profile_url}")
            print(f"{'='*60}")
            
            for key, value in profile_data.items():
                if value:  # Only print non-empty values
                    print(f"{key}: {value}")
            
            print(f"{'='*60}\n")
            
            return profile_data
            
        except Exception as e:
            self.logger.error(f"Error scraping profile {profile_url}: {str(e)}")
            return {
                'URL': profile_url,
                'Error': str(e),
                'Scraped_At': datetime.now().isoformat()
            }
    
    def scrape_profiles(self, csv_file_path, output_file='scraped_profiles.csv'):
        """Main method to scrape all profiles from CSV"""
        try:
            # Setup driver
            self.setup_driver()
            
            # Login to LinkedIn
            if not self.login_to_linkedin():
                self.logger.error("Failed to login to LinkedIn")
                return
            
            # Load URLs from CSV
            urls = self.load_urls_from_csv(csv_file_path)
            if not urls:
                self.logger.error("No URLs to scrape")
                return
            
            all_profiles_data = []
            
            for i, url in enumerate(urls, 1):
                self.logger.info(f"Processing {i}/{len(urls)}: {url}")
                
                # Add 10 second delay between requests
                if i > 1:
                    self.logger.info(f"Waiting 10 seconds before next request...")
                    time.sleep(10)
                
                # Scrape profile
                profile_data = self.extract_profile_data(url)
                all_profiles_data.append(profile_data)
                
                # Save progress every 5 profiles
                if i % 5 == 0:
                    self.save_to_csv(all_profiles_data, f"temp_{output_file}")
                    self.logger.info(f"Saved progress: {i} profiles completed")
            
            # Save final results
            self.save_to_csv(all_profiles_data, output_file)
            self.logger.info(f"Scraping completed! Results saved to {output_file}")
            
        except KeyboardInterrupt:
            self.logger.info("Scraping interrupted by user")
        except Exception as e:
            self.logger.error(f"Unexpected error during scraping: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
    
    def save_to_csv(self, data, filename):
        """Save scraped data to CSV file"""
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            self.logger.info(f"Data saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {str(e)}")

def main():
    """Main function to run the scraper"""
    # Create sample CSV file if it doesn't exist
    sample_csv = 'linkedin_urls.csv'
    if not os.path.exists(sample_csv):
        sample_data = {
            'LinkedIn': [
                'https://www.linkedin.com/in/addis-olujohungbe/',
                'https://www.linkedin.com/in/sharanjm',
                'https://www.linkedin.com/in/poncesamaniego/',
                # 'https://www.linkedin.com/in/samuel-ler/',
                # 'https://www.linkedin.com/in/andrew-foley-6ba07779/',
                # 'https://www.linkedin.com/in/christophergbenavides/',
                # 'https://www.linkedin.com/in/mike-titzer-834a0535/'
            ]
        }
        pd.DataFrame(sample_data).to_csv(sample_csv, index=False)
        print(f"Created sample CSV file: {sample_csv}")
    
    # Initialize and run scraper
    scraper = LinkedInScraper()
    scraper.scrape_profiles(sample_csv)

if __name__ == "__main__":
    main()