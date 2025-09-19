from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import json
import re
from urllib.parse import urljoin

url = 'https://www.houseplantresource.com/?v=1923594eeec381139a09000cf8ab6186'

def get_plant_links(soup, base_url):
    """Extract plant names and their links from the main page"""
    plant_links = []
    found_plants = set()  # Track plants we've already found to avoid duplicates
    
    # Target plant names from your list
    target_plants = [
        'anthurium', 'aloe', 'begonia', 'bird of paradise', 'calathea', 
        'chinese evergreen', 'ctenanthe', 'dracaena', 'ivy', 'money tree', 'monstera'
    ]
    
    # Look for clickable plant names (links)
    links = soup.find_all('a', href=True)
    
    for link in links:
        link_text = link.get_text(strip=True).lower()
        href = link.get('href')
        
        # Skip empty links
        if not link_text or not href:
            continue
        
        # Check if this link matches one of our target plants
        for plant in target_plants:
            # More precise matching - link text should be exactly the plant name or very close
            if (link_text == plant or 
                link_text == plant.replace(' ', '') or  # Handle spaces
                (plant in link_text and len(link_text) <= len(plant) + 3)):  # Allow slight variations
                
                # Avoid duplicates - only take the first occurrence of each plant
                if plant not in found_plants:
                    # Convert relative URLs to absolute
                    full_url = urljoin(base_url, href)
                    plant_links.append({
                        'name': link.get_text(strip=True),  # Keep original case
                        'url': full_url
                    })
                    found_plants.add(plant)
                    break  # Found a match, move to next link
    
    return plant_links

def extract_care_data(soup, plant_name):
    """Extract care information from individual plant page"""
    care_data = {
        'name': plant_name,
        'care': {}
    }
    
    # Get all text content
    page_text = soup.get_text()
    
    # Look for structured care sections with headings
    care_sections = {
        'light_requirements': [
            'Light Requirements:', 'Light:', 'Lighting:', 'Lighting Requirements:'
        ],
        'watering_needs': [
            'Watering Needs:', 'Watering:', 'Water Requirements:', 'Water:'
        ],
        'soil_preferences': [
            'Soil Preferences:', 'Soil:', 'Soil Requirements:', 'Potting Mix:'
        ],
        'temperature_humidity': [
            'Temperature and Humidity:', 'Temperature:', 'Humidity:', 'Climate:'
        ],
        'fertilization': [
            'Fertilization:', 'Fertilizer:', 'Feeding:', 'Nutrients:'
        ],
        'pruning_maintenance': [
            'Pruning and Maintenance:', 'Pruning:', 'Maintenance:', 'Care Tips:'
        ]
    }
    
    # Split text into paragraphs
    paragraphs = re.split(r'\n\s*\n', page_text)
    
    for care_type, headers in care_sections.items():
        for header in headers:
            for paragraph in paragraphs:
                if header in paragraph:
                    # Extract the content after the header
                    content = paragraph.split(header, 1)
                    if len(content) > 1:
                        care_info = content[1].strip()
                        # Clean up the text
                        care_info = re.sub(r'\s+', ' ', care_info)  # Remove extra whitespace
                        if len(care_info) > 20:  # Only keep substantial content
                            care_data['care'][care_type] = care_info
                            break
        
        # If no structured header found, try keyword search as fallback
        if care_type not in care_data['care']:
            keywords = {
                'light_requirements': ['light', 'sun', 'bright', 'shade'],
                'watering_needs': ['water', 'watering', 'drought', 'moist'],
                'soil_preferences': ['soil', 'potting', 'drain', 'mix'],
                'temperature_humidity': ['temperature', 'humidity', 'warm', 'cool'],
                'fertilization': ['fertilizer', 'fertilize', 'feed', 'nutrients'],
                'pruning_maintenance': ['prune', 'trim', 'repot', 'maintenance']
            }
            
            if care_type in keywords:
                for paragraph in paragraphs:
                    if any(keyword in paragraph.lower() for keyword in keywords[care_type]):
                        if len(paragraph.strip()) > 50:  # Substantial content
                            clean_paragraph = re.sub(r'\s+', ' ', paragraph.strip())
                            care_data['care'][care_type] = clean_paragraph[:300]  # Limit length
                            break
    
    return care_data

# Set up headless Firefox
firefox_options = Options()
firefox_options.add_argument('--headless')

try:
    driver = webdriver.Firefox(options=firefox_options)
    print("Using Firefox driver")
    
    driver.get(url)
    
    # Wait for JavaScript to render and load content
    time.sleep(10)  # Longer wait for Notion
    
    print("Successfully loaded the page!")
    print("Page title:", driver.title)
    
    # Try to find Notion-specific content
    # Look for JavaScript variables or data attributes
    page_source = driver.page_source
    
    # Check if content is actually loaded
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Look for Notion's data in script tags or data attributes
    script_tags = soup.find_all('script')
    notion_data = []
    
    for script in script_tags:
        script_content = script.string
        if script_content and ('plant' in script_content.lower() or 'care' in script_content.lower()):
            print("Found potential plant data in JavaScript")
            # Try to extract JSON data from script
            try:
                # Look for JSON-like structures
                import re
                json_matches = re.findall(r'\{[^{}]*(?:"[^"]*"[^{}]*)*\}', script_content)
                for match in json_matches:
                    if 'plant' in match.lower() or 'care' in match.lower():
                        notion_data.append(match)
            except:
                pass
    
    # Extract plant links from main page
    print("Extracting plant links from main page...")
    plant_links = get_plant_links(soup, url)
    print(f"Found {len(plant_links)} potential plant links")
    
    # Visit each plant page and extract care data
    all_plant_data = []
    
    for i, plant_link in enumerate(plant_links):  # Process all plants
        print(f"Scraping plant {i+1}/{len(plant_links)}: {plant_link['name']}")
        
        try:
            # Visit individual plant page
            driver.get(plant_link['url'])
            time.sleep(3)  # Wait for page to load
            
            # Parse the plant page
            plant_soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract care data
            care_data = extract_care_data(plant_soup, plant_link['name'])
            care_data['url'] = plant_link['url']
            
            all_plant_data.append(care_data)
            
        except Exception as e:
            print(f"Error scraping {plant_link['name']}: {e}")
            continue
    
    plant_data = all_plant_data
    
    # Save to JSON file
    with open('plant_care_data.json', 'w', encoding='utf-8') as f:
        json.dump(plant_data, f, indent=2, ensure_ascii=False)
    
    print(f"Extracted {len(plant_data)} plant entries")
    print("Data saved to plant_care_data.json")
    
    # Print sample data
    if plant_data:
        print("\nSample data:")
        print(json.dumps(plant_data[:2], indent=2, ensure_ascii=False))
    
    driver.quit()
    
except Exception as e:
    print(f"Error: {e}")
    print("Make sure Firefox and geckodriver are installed")
