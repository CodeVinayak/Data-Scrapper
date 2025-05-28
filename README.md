# Odisha RERA Project Details Scraper

**Developed by:** Vinayak Kumar Singh  
**For:** Primenumbers Technologies  
**Assignment:** Data Engineer - Python Internship

A Python web scraper designed to extract project details from the Odisha Real Estate Regulatory Authority (RERA) website and save the data into a CSV file.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technical Requirements](#technical-requirements)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Output](#output)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Project Overview

This Python script automates the process of scraping project details from the Odisha RERA website (https://rera.odisha.gov.in/projects/project-list). It navigates through the website, extracts information for the first six listed projects under the "Projects Registered" heading, and saves this data into a CSV file.

### Data Fields Extracted

For each project, the following information is collected:
- **RERA Registration Number**
- **Project Name**
- **Promoter Name** (Company Name from "Promoter Details" tab)
- **Address of the Promoter** (Registered Office Address from "Promoter Details" tab)
- **GST Number of the Promoter**

## Features

- Automated web scraping using Selenium WebDriver
- HTML parsing with BeautifulSoup
- Automatic ChromeDriver management
- CSV output generation
- Screenshot capture for debugging
- Progress tracking and console output
- Error handling and timeout management

## Technical Requirements

- **Python:** Version 3.7 or higher
- **Google Chrome:** Latest version (required for ChromeDriver)
- **Pip:** Python package installer

### Required Python Libraries

```bash
pip install selenium beautifulsoup4 webdriver-manager
```

- `selenium`: Browser automation and interaction
- `beautifulsoup4`: HTML content parsing
- `webdriver-manager`: Automatic ChromeDriver management

## Setup Instructions

### 1. Clone or Download the Script

Ensure you have the `rera_scraper.py` file in a local directory on your system.

### 2. Create a Virtual Environment (Recommended)

Open Command Prompt (cmd) or PowerShell and navigate to your project directory:

```bash
cd path\to\your\project_directory
```

Create and activate the virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# For Linux/Mac
source venv/bin/activate
```

Your command prompt should now be prefixed with `(venv)`.

### 3. Install Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install selenium beautifulsoup4 webdriver-manager
```

## Usage

### Running the Scraper

1. **Ensure Prerequisites are Met**: Python, Google Chrome, and required libraries are installed.

2. **Activate Virtual Environment** (if used):
   ```bash
   venv\Scripts\activate
   ```

3. **Execute the Script**:
   ```bash
   python rera_scraper.py
   ```
   (Use `python rera_scraper.py`)

### Execution Process

1. A Google Chrome browser window will open (unless headless mode is enabled)
2. The script navigates to the Odisha RERA projects page
3. Processes the first six projects by:
   - Navigating to their detail pages
   - Clicking the "Promoter Details" tab
   - Extracting required information
4. Progress messages are displayed in the console
5. Screenshots are saved to the `screenshots` folder for debugging

## Output

### Console Output
The script prints scraped data for each project to the console during processing.

### CSV File
Upon completion, data is saved to `rera_odisha_projects_output.csv` with the following columns:
- Rera Regd. No
- Project Name
- Promoter Name
- Address of the Promoter
- GST No.

### Screenshots
Debug screenshots are saved in the `screenshots` folder for troubleshooting purposes.

## Troubleshooting

### Common Issues and Solutions

**Internet Connection**
- Ensure you have a stable internet connection

**Website Structure Changes**
- The script is sensitive to HTML structure changes
- Update CSS selectors and XPaths if the website layout changes

**Timeout Errors**
- Increase timeout values in `WebDriverWait` calls if elements take longer to load
- Common cause: website loading slower than expected

**ChromeDriver Issues**
- Ensure Google Chrome is updated to the latest version
- Clear webdriver-manager cache if needed (located in `~/.wdm` or `C:\Users\YourUserName\.wdm`)

**File Permissions**
- Ensure the script has write permissions in the execution directory
- Run Command Prompt as administrator if necessary

### Configuration Options

**Headless Mode**
To run without displaying the browser window, uncomment this line in the script:
```python
# options.add_argument('--headless')
```

**Debug Screenshots**
Check the `screenshots` folder for visual debugging information if errors occur.

## Project Structure

```
project_directory/
│
├── rera_scraper.py
├── rera_odisha_projects_output.csv
├── screenshots/
│   └── [debug screenshots]
├── venv/
│   └── [virtual environment files]
└── README.md
```

## Contributing

This project was developed as part of an internship assignment. For suggestions or improvements, please contact the development team at Primenumbers Technologies.

## License

This project is developed for educational and professional purposes as part of an internship assignment.