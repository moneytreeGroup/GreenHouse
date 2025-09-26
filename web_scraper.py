import time
import json
import re
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

url = "https://www.houseplantresource.com/?v=1923594eeec381139a09000cf8ab6186"


def get_plant_links(soup, base_url):
    """Extract plant names and their links from the main page"""
    plant_links = []
    found_plants = set()  # Track plants we've already found to avoid duplicates

    # Target plant names from your list
    target_plants = [
        "anthurium",
        "aloe",
        "alocasia",
        "begonia",
        "bird of paradise",
        "calathea",
        "chinese evergreen",
        "ctenanthe",
        "dracaena",
        "dieffenbachia",
        "ficus",
        "ivy",
        "money tree",
        "monstera",
        "peace lily",
        "poinsettia",
        "hypoestes",
        "pothos",
        "schefflera",
        "snake plant",
        "maranta",
        "yucca",
        "zamioculcas zamiifolia 'zz'",
    ]

    # Look for clickable plant names (links)
    links = soup.find_all("a", href=True)

    for link in links:
        link_text = link.get_text(strip=True).lower()
        href = link.get("href")

        # Skip empty links
        if not link_text or not href:
            continue

        # Check if this link matches one of our target plants
        for plant in target_plants:
            # More precise matching - link text should be exactly the plant name or very close
            if (
                link_text == plant
                or link_text == plant.replace(" ", "")  # Handle spaces
                or (plant in link_text and len(link_text) <= len(plant) + 3)
            ):  # Allow slight variations

                # Avoid duplicates - only take the first occurrence of each plant
                if plant not in found_plants:
                    # Convert relative URLs to absolute
                    full_url = urljoin(base_url, href)
                    plant_links.append(
                        {
                            "name": link.get_text(strip=True),  # Keep original case
                            "url": full_url,
                        }
                    )
                    found_plants.add(plant)
                    break  # Found a match, move to next link

    return plant_links


def extract_care_data(soup, plant_name):
    """Extract care information from individual plant page"""
    care_data = {"name": plant_name, "care": {}}

    # Get all text content
    page_text = soup.get_text()

    # Define care headings in order they appear on the page
    care_headings = [
        ("light_requirements", r"Light Requirements?:"),
        ("watering_needs", r"Watering Needs?:"),
        ("soil_preferences", r"Soil Preferences?:"),
        ("temperature_humidity", r"Temperature and Humidity:"),
        ("fertilization", r"Fertilization:"),
        ("pruning_maintenance", r"Pruning and Maintenance:"),
    ]

    # Use regex to extract content between headings
    for i, (care_type, pattern) in enumerate(care_headings):
        # Find the current heading
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            start_pos = match.end()

            # Find where this section ends (next heading or end of care guide)
            end_pos = len(page_text)

            # Look for the next care heading
            for j in range(i + 1, len(care_headings)):
                next_pattern = care_headings[j][1]
                next_match = re.search(
                    next_pattern, page_text[start_pos:], re.IGNORECASE
                )
                if next_match:
                    end_pos = start_pos + next_match.start()
                    break

            # Also check for common section breaks that end care info
            section_breaks = [
                r"Common Issues",
                r"Propagation Methods?",
                r"FAQs?",
                r"Share Experiences",
            ]

            for break_pattern in section_breaks:
                break_match = re.search(
                    break_pattern, page_text[start_pos:], re.IGNORECASE
                )
                if break_match:
                    potential_end = start_pos + break_match.start()
                    if potential_end < end_pos:
                        end_pos = potential_end
                        break

            # Extract and clean the content
            care_content = page_text[start_pos:end_pos].strip()
            care_content = re.sub(r"\s+", " ", care_content)  # Clean whitespace
            care_content = re.sub(
                r"^\W+", "", care_content
            )  # Remove leading punctuation

            # Only keep if it's substantial content (not just whitespace/punctuation)
            if len(care_content) > 30 and any(char.isalpha() for char in care_content):
                care_data["care"][care_type] = care_content

    return care_data


# Set up headless Firefox
firefox_options = Options()
firefox_options.add_argument("--headless")

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
    soup = BeautifulSoup(page_source, "html.parser")

    # Look for Notion's data in script tags or data attributes
    script_tags = soup.find_all("script")
    notion_data = []

    for script in script_tags:
        script_content = script.string
        if script_content and (
            "plant" in script_content.lower() or "care" in script_content.lower()
        ):
            print("Found potential plant data in JavaScript")
            # Try to extract JSON data from script
            try:
                # Look for JSON-like structures
                import re

                json_matches = re.findall(
                    r'\{[^{}]*(?:"[^"]*"[^{}]*)*\}', script_content
                )
                for match in json_matches:
                    if "plant" in match.lower() or "care" in match.lower():
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
            driver.get(plant_link["url"])
            time.sleep(3)  # Wait for page to load

            # Parse the plant page
            plant_soup = BeautifulSoup(driver.page_source, "html.parser")

            # Extract care data
            care_data = extract_care_data(plant_soup, plant_link["name"])
            care_data["url"] = plant_link["url"]

            all_plant_data.append(care_data)

        except Exception as e:
            print(f"Error scraping {plant_link['name']}: {e}")
            continue

    plant_data = all_plant_data

    # Save to JSON file
    with open("plant_care_data.json", "w", encoding="utf-8") as f:
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
