import csv
import os
from bs4 import BeautifulSoup

def split_location(location):
    parts = [part.strip() for part in location.split(',')]
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    elif len(parts) == 2:
        return parts[0], parts[1], ''
    elif len(parts) == 1:
        return parts[0], '', ''
    else:
        return '', '', ''

def extract_info_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    
    location_div = soup.select_one('.job-details-jobs-unified-top-card__primary-description-container')
    job_location = "Not found"
    if location_div:
        location_span = location_div.select_one('.tvm__text.tvm__text--low-emphasis')
        if location_span:
            job_location = location_span.text.strip()
    
    company_div = soup.select_one('.job-details-jobs-unified-top-card__company-name')
    company_name = company_div.a.text.strip() if company_div and company_div.a else "Not found"
    company_link = company_div.a['href'] if company_div and company_div.a else "Not found"
    
    job_div = soup.select_one('.t-24.job-details-jobs-unified-top-card__job-title')
    job_title = job_div.h1.a.text.strip() if job_div and job_div.h1 and job_div.h1.a else "Not found"
    job_link = job_div.h1.a['href'] if job_div and job_div.h1 and job_div.h1.a else "Not found"

    if job_link.startswith('/'):
        job_link = f"https://www.linkedin.com{job_link}"
    elif not job_link.startswith('http'):
        job_link = f"https://www.linkedin.com/{job_link}"
    
    city, state, country = split_location(job_location)
    
    # Extract job description
    job_description = "Not found"
    description_div = soup.select_one('.jobs-box__html-content.jobs-description-content__text')
    if description_div:
        job_description = description_div.get_text(separator='\n', strip=True)
    
    # Extract company size and sector
    company_info_div = soup.select_one('.t-14.mt5')
    company_sector = "Not found"
    company_size = "Not found"
    if company_info_div:
        sector_text = company_info_div.contents[0].strip() if company_info_div.contents else "Not found"
        company_sector = sector_text if sector_text != "" else "Not found"
        size_span = company_info_div.select_one('.jobs-company__inline-information')
        if size_span:
            company_size = size_span.text.strip()
    
    return {
        'Company Name': company_name,
        'Company Link': company_link,
        'Job Title': job_title,
        'Job Link': job_link,
        'City': city,
        'State': state,
        'Country': country,
        'Job Description': job_description,
        'Company Sector': company_sector,
        'Company Size': company_size
    }

folder_path = 'HtmlPages/JobOpeningPage'  

csv_file_path = 'cleaned_job_details.csv'

unique_data = {}

for filename in os.listdir(folder_path):
    if filename.endswith('.html'):
        file_path = os.path.join(folder_path, filename)
        try:
            job_info = extract_info_from_html(file_path)
            if 'Not found' not in job_info.values():
                unique_key = (job_info['Company Name'], job_info['Job Title'])
                if unique_key not in unique_data:
                    unique_data[unique_key] = job_info
            print(f"Processed: {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

sorted_data = sorted(unique_data.values(), key=lambda x: x['Company Name'])

with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Company Name', 'Company Link', 'Job Title', 'Job Link', 'City', 'State', 'Country', 'Job Description', 'Company Sector', 'Company Size']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(sorted_data)

print(f"CSV file '{csv_file_path}' has been created with cleaned and sorted information from all HTML files.")