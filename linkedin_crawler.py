import asyncio
import json
from datetime import datetime
from crawl4ai import AsyncWebCrawler

# LinkedIn URLs to crawl
LINKEDIN_URLS = [
    "https://www.linkedin.com/in/sharanjm",
    "https://www.linkedin.com/in/addis-olujohungbe/"
]

async def crawl_linkedin_profile(url):
    """
    Crawl a single LinkedIn profile and return the results
    """
    try:
        async with AsyncWebCrawler(
            # Use stealth mode to avoid detection
            stealth=True,
            # Add some delay to be respectful
            delay_before_return_html=2,
            # Set user agent
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ) as crawler:
            print(f"[CRAWLING] Starting crawl for: {url}")
            
            result = await crawler.arun(
                url=url,
                # Extract structured data
                extraction_strategy="LLMExtractionStrategy",
                extraction_config={
                    "provider": "openai/gpt-4o-mini",
                    "api_token": "your-api-key-here",  # You'll need to add your API key
                    "instruction": """
                    Extract the following information from this LinkedIn profile:
                    - Full name
                    - Current job title and company
                    - Location
                    - About/Summary section
                    - Experience (job titles, companies, dates)
                    - Education
                    - Skills
                    - Contact information if available
                    
                    Return the data in a structured JSON format.
                    """
                },
                # Wait for page to load completely
                wait_for="networkidle",
                # Take a screenshot for verification
                screenshot=True
            )
            
            if result.success:
                print(f"[SUCCESS] Successfully crawled: {url}")
                return {
                    "url": url,
                    "success": True,
                    "title": result.title,
                    "markdown": result.markdown,
                    "extracted_content": result.extracted_content,
                    "screenshot": result.screenshot,
                    "crawl_timestamp": datetime.now().isoformat()
                }
            else:
                print(f"[ERROR] Failed to crawl: {url} - {result.error_message}")
                return {
                    "url": url,
                    "success": False,
                    "error": result.error_message,
                    "crawl_timestamp": datetime.now().isoformat()
                }
                
    except Exception as e:
        print(f"[EXCEPTION] Error crawling {url}: {str(e)}")
        return {
            "url": url,
            "success": False,
            "error": str(e),
            "crawl_timestamp": datetime.now().isoformat()
        }

async def crawl_all_profiles():
    """
    Crawl all LinkedIn profiles concurrently
    """
    print(f"[INIT] Starting to crawl {len(LINKEDIN_URLS)} LinkedIn profiles...")
    
    # Create tasks for concurrent crawling
    tasks = [crawl_linkedin_profile(url) for url in LINKEDIN_URLS]
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful_crawls = []
    failed_crawls = []
    
    for result in results:
        if isinstance(result, dict):
            if result.get("success"):
                successful_crawls.append(result)
            else:
                failed_crawls.append(result)
        else:
            # Handle exceptions
            failed_crawls.append({
                "url": "unknown",
                "success": False,
                "error": str(result),
                "crawl_timestamp": datetime.now().isoformat()
            })
    
    # Save results to files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save all results
    all_results = {
        "crawl_session": {
            "timestamp": datetime.now().isoformat(),
            "total_urls": len(LINKEDIN_URLS),
            "successful": len(successful_crawls),
            "failed": len(failed_crawls)
        },
        "successful_crawls": successful_crawls,
        "failed_crawls": failed_crawls
    }
    
    results_filename = f"linkedin_crawl_results_{timestamp}.json"
    with open(results_filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[COMPLETE] Crawling session completed!")
    print(f"[RESULTS] Total URLs: {len(LINKEDIN_URLS)}")
    print(f"[RESULTS] Successful: {len(successful_crawls)}")
    print(f"[RESULTS] Failed: {len(failed_crawls)}")
    print(f"[RESULTS] Results saved to: {results_filename}")
    
    # Save individual markdown files for successful crawls
    for i, result in enumerate(successful_crawls):
        if result.get("markdown"):
            profile_name = result["url"].split("/")[-1].replace("/", "")
            markdown_filename = f"linkedin_profile_{profile_name}_{timestamp}.md"
            with open(markdown_filename, 'w', encoding='utf-8') as f:
                f.write(f"# LinkedIn Profile: {result['url']}\n\n")
                f.write(f"**Crawled on:** {result['crawl_timestamp']}\n\n")
                f.write(f"**Page Title:** {result.get('title', 'N/A')}\n\n")
                f.write("## Profile Content\n\n")
                f.write(result["markdown"])
            print(f"[SAVED] Profile markdown saved to: {markdown_filename}")
    
    return all_results

# Simple version without LLM extraction for basic crawling
async def simple_crawl_linkedin_profile(url):
    """
    Simple crawl without LLM extraction - just get the basic content
    """
    try:
        async with AsyncWebCrawler(
            stealth=True,
            delay_before_return_html=2,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ) as crawler:
            print(f"[CRAWLING] Starting simple crawl for: {url}")
            
            result = await crawler.arun(
                url=url,
                wait_for="networkidle",
                screenshot=True
            )
            
            if result.success:
                print(f"[SUCCESS] Successfully crawled: {url}")
                return {
                    "url": url,
                    "success": True,
                    "title": result.title,
                    "markdown": result.markdown,
                    "html": result.html,
                    "screenshot": result.screenshot,
                    "crawl_timestamp": datetime.now().isoformat()
                }
            else:
                print(f"[ERROR] Failed to crawl: {url} - {result.error_message}")
                return {
                    "url": url,
                    "success": False,
                    "error": result.error_message,
                    "crawl_timestamp": datetime.now().isoformat()
                }
                
    except Exception as e:
        print(f"[EXCEPTION] Error crawling {url}: {str(e)}")
        return {
            "url": url,
            "success": False,
            "error": str(e),
            "crawl_timestamp": datetime.now().isoformat()
        }

async def simple_crawl_all_profiles():
    """
    Simple crawl all LinkedIn profiles without LLM extraction
    """
    print(f"[INIT] Starting simple crawl of {len(LINKEDIN_URLS)} LinkedIn profiles...")
    
    results = []
    for url in LINKEDIN_URLS:
        result = await simple_crawl_linkedin_profile(url)
        results.append(result)
        # Add delay between requests to be respectful
        await asyncio.sleep(3)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    successful_crawls = [r for r in results if r.get("success")]
    failed_crawls = [r for r in results if not r.get("success")]
    
    all_results = {
        "crawl_session": {
            "timestamp": datetime.now().isoformat(),
            "total_urls": len(LINKEDIN_URLS),
            "successful": len(successful_crawls),
            "failed": len(failed_crawls)
        },
        "results": results
    }
    
    results_filename = f"linkedin_simple_crawl_{timestamp}.json"
    with open(results_filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[COMPLETE] Simple crawling session completed!")
    print(f"[RESULTS] Total URLs: {len(LINKEDIN_URLS)}")
    print(f"[RESULTS] Successful: {len(successful_crawls)}")
    print(f"[RESULTS] Failed: {len(failed_crawls)}")
    print(f"[RESULTS] Results saved to: {results_filename}")
    
    # Save individual markdown files
    for result in successful_crawls:
        if result.get("markdown"):
            profile_name = result["url"].split("/")[-1].replace("/", "")
            markdown_filename = f"linkedin_simple_{profile_name}_{timestamp}.md"
            with open(markdown_filename, 'w', encoding='utf-8') as f:
                f.write(f"# LinkedIn Profile: {result['url']}\n\n")
                f.write(f"**Crawled on:** {result['crawl_timestamp']}\n\n")
                f.write(f"**Page Title:** {result.get('title', 'N/A')}\n\n")
                f.write("## Profile Content\n\n")
                f.write(result["markdown"])
            print(f"[SAVED] Profile markdown saved to: {markdown_filename}")
    
    return all_results

if __name__ == "__main__":
    print("LinkedIn Profile Crawler")
    print("=" * 50)
    print("Choose crawling method:")
    print("1. Simple crawl (no LLM extraction)")
    print("2. Advanced crawl with LLM extraction (requires API key)")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        print("\nStarting simple crawl...")
        asyncio.run(simple_crawl_all_profiles())
    elif choice == "2":
        print("\nStarting advanced crawl with LLM extraction...")
        print("Note: You'll need to add your OpenAI API key to the script")
        asyncio.run(crawl_all_profiles())
    else:
        print("Invalid choice. Running simple crawl by default...")
        asyncio.run(simple_crawl_all_profiles()) 