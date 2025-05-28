import time
import os
import csv # For saving data to CSV
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
import traceback

# Helper function to get text safely
def get_safe_text(element):
    return element.get_text(strip=True) if element else "Not Found"

def find_detail_in_promoter_structure(section_soup, target_label_texts):
    """
    Helper function to find details within the promoter section based on a
    label-strong tag structure inside divs like <div class="ms-3">.
    """
    if not section_soup:
        print(f"    Debug: section_soup for promoter details is None for labels: {target_label_texts}")
        return "Not Found"

    # Structure: <div class="col-md-6"> -> <div class="d-flex ..."> -> <div class="ms-3"> -> <label> & <strong>
    possible_detail_containers = section_soup.select("div.row div.col-md-6 div.d-flex div.ms-3")
    if not possible_detail_containers: # Broader fallback
        possible_detail_containers = section_soup.select("div.ms-3") # Fallback if the specific path fails

    for container in possible_detail_containers:
        label_tag = container.find("label", class_="label-control")
        value_tag = container.find("strong") # Value is typically in a <strong> tag

        if label_tag and value_tag:
            label_text_cleaned = label_tag.get_text(strip=True).strip().lower().rstrip(':')
            # print(f"    [Debug] Checking Label: '{label_text_cleaned}' against {target_label_texts}") # Uncomment for deep debugging
            for target_label in target_label_texts:
                if target_label.strip().lower() == label_text_cleaned:
                    return value_tag.get_text(strip=True)
    
    print(f"    Label(s) '{', '.join(target_label_texts)}' not found in promoter details structure.")
    return "Not Found"

def extract_data_from_detail_page(driver):
    """
    Extracts details from the currently loaded project detail page.
    """
    project_data = {
        "Rera Regd. No": "Not Found", "Project Name": "Not Found",
        "Promoter Name": "Not Found", "Address of the Promoter": "Not Found",
        "GST No.": "Not Found"
    }
    screenshot_dir = "screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)

    try:
        print("  Waiting for detail page 'Project Overview' content to load...")
        WebDriverWait(driver, 45).until( 
            EC.presence_of_element_located((By.CSS_SELECTOR, "app-project-overview div.project-details div.card-body"))
        )
        time.sleep(3) 
        page_soup_overview = BeautifulSoup(driver.page_source, 'html.parser')
        print("  Detail page (Project Overview) source obtained.")

        overview_section = page_soup_overview.select_one("app-project-overview div.project-details div.card-body")
        if overview_section:
            def find_overview_detail(section_soup, label_text_to_find):
                labels = section_soup.find_all("label", class_="label-control")
                for label_tag in labels:
                    if label_text_to_find.lower() in label_tag.get_text(strip=True).lower():
                        parent_div = label_tag.find_parent("div", class_="details-project")
                        if parent_div:
                            value_strong = parent_div.find("strong")
                            if value_strong:
                                return value_strong.get_text(strip=True)
                return "Not Found"

            project_data["Project Name"] = find_overview_detail(overview_section, "Project Name")
            project_data["Rera Regd. No"] = find_overview_detail(overview_section, "RERA Regd. No.")
        else:
            print(f"  Could not find overview section on detail page.")
            driver.save_screenshot(os.path.join(screenshot_dir, f"detail_page_no_overview_section_{project_data.get('Project Name', 'Unknown').replace(' ','_')}.png"))
        
        print(f"  Extracted Project Name: {project_data['Project Name']}, RERA No: {project_data['Rera Regd. No']}")

        # --- Click on "Promoter Details" tab ---
        print(f"  Attempting to click 'Promoter Details' tab...")
        promoter_tab_xpath = "//a[@class='nav-link' and normalize-space(text())='Promoter Details']"
        try:
            promoter_tab_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, promoter_tab_xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", promoter_tab_button)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", promoter_tab_button)
            print("  'Promoter Details' tab clicked.")
        except TimeoutException:
            print(f"  Could not find or click 'Promoter Details' tab by text using XPath.")
            driver.save_screenshot(os.path.join(screenshot_dir, f"promoter_tab_click_error_{project_data.get('Project Name', 'Unknown').replace(' ','_')}.png"))
            return project_data 

        # --- Wait for and Extract Promoter Details ---
        print(f"  Waiting for promoter details content (e.g., 'Company Name' label) to load...")
        promoter_company_name_label_xpath = "//app-promoter-details//label[@class='label-control' and normalize-space(text())='Company Name']"
        try:
            WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, promoter_company_name_label_xpath))
            )
            print("  Promoter details content (label for Company Name) is visible.")
        except TimeoutException:
            print("  Timeout waiting for 'Company Name' label in promoter details. Content might not have loaded or structure is different.")
            driver.save_screenshot(os.path.join(screenshot_dir, f"promoter_details_load_timeout_{project_data.get('Project Name', 'Unknown').replace(' ','_')}.png"))
            return project_data

        time.sleep(3) # Allow full rendering after visibility of the first label
        promoter_section_soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        promoter_details_card_body = promoter_section_soup.select_one("app-promoter-details div.card-body")

        if promoter_details_card_body:
            print("  Extracting Promoter Name (Company Name)...")
            project_data["Promoter Name"] = find_detail_in_promoter_structure(promoter_details_card_body, ["Company Name"])
            
            print("  Extracting Address of the Promoter (Registered Office Address)...")
            project_data["Address of the Promoter"] = find_detail_in_promoter_structure(promoter_details_card_body, ["Registered Office Address"])
            if project_data["Address of the Promoter"] == "Not Found":
                 print("    Registered Office Address not found, trying Correspondence Office Address...")
                 project_data["Address of the Promoter"] = find_detail_in_promoter_structure(promoter_details_card_body, ["Correspondence Office Address"])

            print("  Extracting GST No....")
            project_data["GST No."] = find_detail_in_promoter_structure(promoter_details_card_body, ["GST No."])
        else:
            print("  Could not find the 'app-promoter-details div.card-body' area for promoter details.")
            driver.save_screenshot(os.path.join(screenshot_dir, f"promoter_details_card_body_missing_{project_data.get('Project Name', 'Unknown').replace(' ','_')}.png"))
        
    except TimeoutException as te:
        print(f"  Timeout occurred in extract_data_from_detail_page: {te}")
        driver.save_screenshot(os.path.join(screenshot_dir, f"detail_page_timeout_generic_{project_data.get('Project Name', 'UnknownProject').replace(' ','_')}.png"))
    except Exception as e:
        print(f"  An error occurred in extract_data_from_detail_page: {e}")
        driver.save_screenshot(os.path.join(screenshot_dir, f"detail_page_processing_error_{project_data.get('Project Name', 'UnknownProject').replace(' ','_')}.png"))
        traceback.print_exc()
    return project_data

def scrape_rera_odisha_local():
    project_list_url = "https://rera.odisha.gov.in/projects/project-list"
    screenshot_dir = "screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)

    options = webdriver.ChromeOptions()
    # To run headless (without a browser window appearing), uncomment the next line:
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu') 
    options.add_argument('--window-size=1920,1080')
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'") 
    options.add_argument("--proxy-bypass-list=*")
    
    driver_service = ChromeService(ChromeDriverManager().install())
    driver = None
    all_projects_data = []

    try:
        print("Setting up Chrome Driver for local execution...")
        driver = webdriver.Chrome(service=driver_service, options=options)
        print("Chrome Driver setup complete.")
        driver.set_page_load_timeout(90) # Increased page load timeout

        print(f"Navigating to {project_list_url}...")
        driver.get(project_list_url)
        print(f"Successfully navigated to {project_list_url}.")
        print(f"Page title: {driver.title}")
        # driver.save_screenshot(os.path.join(screenshot_dir, "project_list_after_navigation.png")) # Optional debug screenshot

        print("Waiting for project cards to appear...")
        WebDriverWait(driver, 180).until( # Long wait for initial card list
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.card.project-card"))
        )
        print("Project cards are present.")
        time.sleep(5) # Allow page to settle further

        for i in range(6): # Loop for the first 6 projects
            print(f"\nProcessing project {i + 1}...")
            
            try:
                # Re-find elements on each iteration for stability
                WebDriverWait(driver, 60).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.card.project-card"))
                )
                project_cards = driver.find_elements(By.CSS_SELECTOR, "div.card.project-card")
                
                if not project_cards or len(project_cards) <= i:
                    print(f"  Could not find project card #{i + 1} (index {i}) or list too short (found {len(project_cards)}).")
                    driver.save_screenshot(os.path.join(screenshot_dir, f"project_card_not_found_iter_{i+1}.png"))
                    break 
                
                current_project_card = project_cards[i]
                # Scroll to the card to ensure it's clickable and fully in view
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});", current_project_card)
                time.sleep(1.5) # Brief pause after scroll for smooth scroll to finish

                view_details_button = WebDriverWait(current_project_card, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-primary"))
                )
                print(f"  Found 'View Details' button for project {i + 1}.")
                # Using JavaScript click as it can be more robust for complex UIs
                driver.execute_script("arguments[0].click();", view_details_button)
                print(f"  Clicked 'View Details' for project {i + 1}.")

            except Exception as e_click:
                print(f"  Error finding/clicking 'View Details' for project {i + 1}: {e_click}")
                driver.save_screenshot(os.path.join(screenshot_dir, f"view_details_click_error_proj_{i+1}.png"))
                traceback.print_exc()
                break # Stop if we can't click a project

            # --- Now on the detail page ---
            project_info = extract_data_from_detail_page(driver)
            all_projects_data.append(project_info)
            print(f"  Data extracted for project {i + 1}: {project_info.get('Project Name', 'N/A')}")

            if len(all_projects_data) >= 6: # Ensure we only process up to 6 projects
                 break

            print("  Navigating back to project list...")
            driver.back()
            
            # IMPORTANT: Wait for the project list page to reload and cards/buttons to be present and interactive again
            print("  Waiting for project list to reload after navigating back...")
            WebDriverWait(driver, 90).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.card.project-card")) 
            )
            # Also ensure a clickable button is ready for the next potential interaction
            WebDriverWait(driver, 30).until( 
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.card.project-card a.btn.btn-primary"))
            )
            time.sleep(5) # Extra pause for stability after back navigation and waits
            print("  Project list reloaded.")
            
    except TimeoutException as te_main:
        print(f"TimeoutException in main scraping function: {te_main}")
        traceback.print_exc()
        if driver:
             driver.save_screenshot(os.path.join(screenshot_dir,"main_timeout_error_screenshot.png"))
    except Exception as e:
        print(f"A critical error occurred in the main scraping function: {e}")
        traceback.print_exc()
        if driver:
             driver.save_screenshot(os.path.join(screenshot_dir,"critical_error_screenshot.png"))
    finally:
        if driver:
            driver.quit()
            print("\nBrowser closed.")

    return all_projects_data

if __name__ == "__main__":
    print("Starting RERA Odisha Scraper locally on Windows...")
    scraped_data = scrape_rera_odisha_local()
    
    if scraped_data:
        print("\n--- Scraped Project Data (Console Output) ---")
        for i, project in enumerate(scraped_data):
            print(f"\n--- Project {i+1} ---")
            print(f"  RERA Regd. No: {project.get('Rera Regd. No', 'Not Found')}")
            print(f"  Project Name: {project.get('Project Name', 'Not Found')}")
            print(f"  Promoter Name: {project.get('Promoter Name', 'Not Found')}")
            print(f"  Address of the Promoter: {project.get('Address of the Promoter', 'Not Found')}")
            print(f"  GST No.: {project.get('GST No.', 'Not Found')}")

        # --- Save data to CSV file ---
        csv_file_name = "rera_odisha_projects_output.csv"
        fieldnames = ["Rera Regd. No", "Project Name", "Promoter Name", "Address of the Promoter", "GST No."]
        
        print(f"\nAttempting to save data to {csv_file_name}...")
        try:
            with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(scraped_data) # Write all rows from the list of dictionaries
            print(f"--- Data successfully saved to {csv_file_name} in the script's directory. ---")
        except IOError as e_io:
            print(f"\n--- IOError: Could not write data to CSV file: {csv_file_name}. Error: {e_io} ---")
            print("    Please check file permissions or if the file is locked by another program.")
        except Exception as e_csv:
            print(f"\n--- An unexpected error occurred while saving data to CSV: {e_csv} ---")
            traceback.print_exc()

    else:
        print("\nNo data was scraped or an error occurred. No CSV file was generated.")
        print("Please check console logs and the 'screenshots' folder for more details.")