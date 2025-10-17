import time
import json
import re
import os
import requests
from urllib.parse import urljoin, urlparse
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
        "bird of paradise",
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


def extract_plant_images(soup, plant_name, base_url, max_images=1):
    """Extract plant-specific images from the page"""
    images = []
    found_images = set()  # Track to avoid duplicates

    # Create plant-specific search terms
    plant_keywords = [
        plant_name.lower(),
        plant_name.lower().replace(" ", ""),
        plant_name.lower().replace(" ", "-"),
        plant_name.lower().replace(" ", "_"),
    ]

    # Simplified image selectors - start broad and get more specific
    image_selectors = [
        "img",  # Try all images first
        'img[alt*="plant"]',
        'img[src*="plant"]',
        f'img[alt*="{plant_name.lower()}"]',
        f'img[title*="{plant_name.lower()}"]',
        "div img",
        "section img",
        "article img",
    ]

    for selector in image_selectors:
        if len(images) >= max_images:
            break

        try:
            img_elements = soup.select(selector)
            print(f"    Trying selector: {selector} - found {len(img_elements)} images")

            for img in img_elements:
                if len(images) >= max_images:
                    break

                src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
                if not src:
                    continue

                # Convert relative URLs to absolute
                if src.startswith("//"):
                    src = "https:" + src
                elif src.startswith("/"):
                    src = urljoin(base_url, src)
                elif not src.startswith("http"):
                    src = urljoin(base_url, src)

                # Skip if already found
                if src in found_images:
                    continue

                # Skip tiny images, logos, icons (but be less strict)
                if any(
                    skip in src.lower()
                    for skip in ["icon", "logo", "favicon", "avatar"]
                ):
                    print(f"    Skipping icon/logo: {src[:50]}...")
                    continue

                # Skip data URLs and SVGs (usually icons)
                if src.startswith("data:") or ".svg" in src.lower():
                    print(f"    Skipping data/svg: {src[:50]}...")
                    continue

                # Get image info
                alt_text = img.get("alt", "")
                title = img.get("title", "")

                # Check if image is relevant to this plant
                image_text = f"{alt_text} {title} {src}".lower()
                is_plant_specific = any(
                    keyword in image_text for keyword in plant_keywords
                )

                # Basic validation - more lenient approach
                valid_image = True
                content_type = "image/jpeg"  # Default assumption

                try:
                    # Try a quick HEAD request but don't fail if it doesn't work
                    response = requests.head(
                        src,
                        timeout=3,  # Shorter timeout
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        },
                    )

                    if response.status_code == 200:
                        content_type = response.headers.get(
                            "content-type", "image/jpeg"
                        )
                        # Only skip if we're sure it's not an image
                        if content_type and not content_type.startswith("image/"):
                            valid_image = False
                    # If HEAD request fails, we'll still try the image

                except:
                    # If validation fails, assume it's valid and try it anyway
                    print(f"    Validation failed for {src[:50]}..., but keeping it")
                    pass

                # TEMPORARY: Just accept any image that has a valid src
                if src and src.startswith("http"):
                    image_info = {
                        "url": src,
                        "alt_text": alt_text,
                        "title": title,
                        "plant_specific": is_plant_specific,
                        "content_type": "image/jpeg",
                    }

                    images.append(image_info)
                    found_images.add(src)

                    print(f"    ✅ Added image for {plant_name}: {src[:60]}...")
                    break  # Take the first valid image and move on

        except Exception as e:
            print(f"Error extracting images with selector {selector}: {e}")
            continue

        # If we found a plant-specific image, stop trying other selectors
        if images and images[-1].get("plant_specific"):
            break

    return images


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


def save_images_locally(plant_data, images_dir="plant_images", download_images=False):
    """Optionally download images locally, or just keep URLs in JSON"""

    for plant in plant_data:
        plant_name = plant.get("name", "unknown").replace(" ", "_").lower()

        if download_images:
            # Create directory for this plant
            plant_folder = os.path.join(images_dir, plant_name)
            if not os.path.exists(plant_folder):
                os.makedirs(plant_folder)

            for i, image in enumerate(plant.get("images", [])):
                if image.get("url"):
                    try:
                        print(
                            f"  Downloading image for {plant['name']}: {image['url'][:60]}..."
                        )
                        response = requests.get(
                            image["url"],
                            timeout=10,
                            headers={
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                            },
                        )

                        if response.status_code == 200:
                            # Get file extension from URL or content type
                            url_path = urlparse(image["url"]).path
                            ext = os.path.splitext(url_path)[1] or ".jpg"

                            filename = f"{plant_name}_image_{i+1}{ext}"
                            filepath = os.path.join(plant_folder, filename)

                            with open(filepath, "wb") as f:
                                f.write(response.content)

                            # Add local path to image data
                            image["local_path"] = filepath
                            print(f"  Saved: {filename}")

                    except Exception as e:
                        print(f"  Failed to download {image['url']}: {e}")
        else:
            # Just keep URLs - no downloading needed
            print(f"  Keeping image URLs for {plant['name']}")

    return plant_data


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

            # Extract plant images
            print(f"  Extracting images for {plant_link['name']}...")
            plant_images = extract_plant_images(
                plant_soup, plant_link["name"], plant_link["url"]
            )
            care_data["images"] = plant_images
            print(f"  Found {len(plant_images)} images")

            all_plant_data.append(care_data)

        except Exception as e:
            print(f"Error scraping {plant_link['name']}: {e}")
            continue

    plant_data = all_plant_data

    # Process images - choose whether to download or keep URLs
    print("\nProcessing images...")

    # Option 1: Just keep URLs (faster, smaller JSON)
    plant_data = save_images_locally(plant_data, download_images=False)

    # Option 2: Download images locally (uncomment to enable)
    # plant_data = save_images_locally(plant_data, download_images=True)

    # Save to JSON file
    with open("plant_care_data.json", "w", encoding="utf-8") as f:
        json.dump(plant_data, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(plant_data)} plant entries")
    print("Data saved to plant_care_data.json")

    driver.quit()

except Exception as e:
    print(f"Error: {e}")
    print("Make sure Firefox and geckodriver are installed")
