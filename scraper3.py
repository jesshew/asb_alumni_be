import os
import csv
import time
import json
import random
import re
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
from html_to_markdown import convert_to_markdown

class LinkedInMarkdownScraper:
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
                logging.FileHandler('linkedin_markdown_scraper.log'),
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
    
    def extract_profile_as_markdown(self, profile_url):
        """Extract LinkedIn profile and convert to markdown format"""
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
            
            # Extract user name for filename
            user_name = self.extract_user_name(soup)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Find the profile content div
            profile_content_div = soup.find('div', {'class': 'extended tetris pv-profile-body-wrapper', 'id': 'profile-content'})
            
            if profile_content_div:
                # Convert the raw HTML to markdown using html-to-markdown
                raw_html = str(profile_content_div)
                markdown_content = convert_to_markdown(raw_html)
                
                # Clean up excessive empty lines and whitespace
                cleaned_markdown = self.clean_markdown(markdown_content)
                
                print(f"\n{'='*80}")
                print(f"MARKDOWN PROFILE CONTENT FOR: {user_name or 'Unknown User'}")
                print(f"Profile URL: {profile_url}")
                print(f"{'='*80}")
                print(cleaned_markdown)
                print(f"{'='*80}")
                print(f"END OF MARKDOWN CONTENT FOR: {user_name or 'Unknown User'}")
                print(f"{'='*80}\n")
                
                # Save markdown to file
                filename = self.create_safe_filename(user_name, timestamp)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# LinkedIn Profile: {user_name or 'Unknown User'}\n\n")
                    f.write(f"**Profile URL:** {profile_url}\n\n")
                    f.write(f"**Scraped at:** {datetime.now().isoformat()}\n\n")
                    f.write(f"---\n\n")
                    f.write(cleaned_markdown)
                
                self.logger.info(f"Markdown content saved to: {filename}")
                
                return {
                    'url': profile_url,
                    'user_name': user_name,
                    'markdown_content': cleaned_markdown,
                    'scraped_at': datetime.now().isoformat(),
                    'filename': filename
                }
                
            else:
                self.logger.warning(f"Profile content div not found for: {profile_url}")
                
                # Try to convert the entire page as fallback
                full_page_html = str(soup)
                markdown_content = convert_to_markdown(full_page_html)
                
                # Clean up excessive empty lines and whitespace
                cleaned_markdown = self.clean_markdown(markdown_content)
                
                print(f"\n{'='*80}")
                print(f"FULL PAGE MARKDOWN FOR: {user_name or 'Unknown User'}")
                print(f"Profile URL: {profile_url}")
                print(f"(Profile content div not found - using full page)")
                print(f"{'='*80}")
                print(cleaned_markdown[:2000])  # Show first 2000 chars to avoid overwhelming output
                print(f"\n... [Content truncated for display] ...")
                print(f"{'='*80}\n")
                
                # Save full page markdown to file
                filename = self.create_safe_filename(user_name, timestamp, "fullpage")
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# LinkedIn Profile (Full Page): {user_name or 'Unknown User'}\n\n")
                    f.write(f"**Profile URL:** {profile_url}\n\n")
                    f.write(f"**Scraped at:** {datetime.now().isoformat()}\n\n")
                    f.write(f"**Note:** Profile content div not found, using full page content\n\n")
                    f.write(f"---\n\n")
                    f.write(cleaned_markdown)
                
                self.logger.info(f"Full page markdown content saved to: {filename}")
                
                return {
                    'url': profile_url,
                    'user_name': user_name,
                    'markdown_content': cleaned_markdown,
                    'scraped_at': datetime.now().isoformat(),
                    'filename': filename,
                    'note': 'Used full page content - profile div not found'
                }
            
        except Exception as e:
            self.logger.error(f"Error scraping profile {profile_url}: {str(e)}")
            return {
                'url': profile_url,
                'error': str(e),
                'scraped_at': datetime.now().isoformat()
            }
    
    def scrape_profiles_to_markdown(self, csv_file_path):
        """Main method to scrape all profiles from CSV and convert to markdown"""
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
            
            all_results = []
            
            for i, url in enumerate(urls, 1):
                self.logger.info(f"Processing {i}/{len(urls)}: {url}")
                
                # Add random delay between requests
                if i > 1:
                    delay = random.uniform(10, 14)
                    self.logger.info(f"Waiting {delay:.1f} seconds before next request...")
                    time.sleep(delay)
                
                # Scrape profile and convert to markdown
                result = self.extract_profile_as_markdown(url)
                all_results.append(result)
                
                # Log progress
                self.logger.info(f"Completed {i}/{len(urls)} profiles")
            
            # Save summary of all results
            summary_filename = f"scraping_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_filename, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Scraping completed! Summary saved to {summary_filename}")
            self.logger.info(f"Total profiles processed: {len(all_results)}")
            
        except KeyboardInterrupt:
            self.logger.info("Scraping interrupted by user")
        except Exception as e:
            self.logger.error(f"Unexpected error during scraping: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

    def clean_markdown(self, markdown_content):
        """Clean up excessive empty lines and whitespace in markdown content"""
        # Remove excessive empty lines (more than 2 consecutive empty lines)
        cleaned_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', markdown_content)
        
        # Remove trailing whitespace from each line
        lines = cleaned_content.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        
        # Join lines back together
        cleaned_content = '\n'.join(cleaned_lines)
        
        # Remove excessive spaces within lines (more than 2 consecutive spaces)
        cleaned_content = re.sub(r' {3,}', '  ', cleaned_content)
        
        # Clean up beginning and end of content
        cleaned_content = cleaned_content.strip()
        
        return cleaned_content
    
    def extract_user_name(self, soup):
        """Extract the user's name from the LinkedIn profile"""
        try:
            # Try multiple selectors to find the name
            name_selectors = [
                'h1.text-heading-xlarge',
                'h1[class*="heading-xlarge"]',
                'h1.top-card-layout__title',
                '.pv-text-details__left-panel h1',
                '.ph5 h1',
                'h1'
            ]
            
            for selector in name_selectors:
                name_element = soup.select_one(selector)
                if name_element:
                    name = name_element.get_text(strip=True)
                    if name and len(name) > 1:  # Basic validation
                        # Clean the name for filename use
                        clean_name = re.sub(r'[^\w\s-]', '', name)  # Remove special chars except spaces and hyphens
                        clean_name = re.sub(r'\s+', '_', clean_name)  # Replace spaces with underscores
                        clean_name = clean_name.strip('_')  # Remove leading/trailing underscores
                        return clean_name
            
            # If no name found, return None
            return None
            
        except Exception as e:
            self.logger.warning(f"Error extracting user name: {str(e)}")
            return None
    
    def create_safe_filename(self, name, timestamp, file_type="markdown"):
        """Create a safe filename using the user's name and timestamp"""
        if name:
            # Limit name length to avoid filesystem issues
            safe_name = name[:50] if len(name) > 50 else name
            if file_type == "markdown":
                return f"{safe_name}_{timestamp}.md"
            elif file_type == "fullpage":
                return f"{safe_name}_fullpage_{timestamp}.md"
        else:
            # Fallback to timestamp-only naming
            if file_type == "markdown":
                return f"profile_markdown_{timestamp}.md"
            elif file_type == "fullpage":
                return f"profile_fullpage_markdown_{timestamp}.md"

def main():
    """Main function to run the markdown scraper"""
    # Create sample CSV file if it doesn't exist
    # sample_csv = 'linkedin_urls.csv'
    sample_csv = 'sample_data.csv'
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
    scraper = LinkedInMarkdownScraper()
    scraper.scrape_profiles_to_markdown(sample_csv)

if __name__ == "__main__":
    main() 