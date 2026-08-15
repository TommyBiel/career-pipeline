import os
import requests
from dotenv import load_dotenv

load_dotenv('../keys.env')

def adzuna_response_func(country):

    adzuna_id = os.getenv('adzuna_id')
    adzuna_key = os.getenv('adzuna_key')

    adzuna_url=f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"

    adzuna_headers = {
        "Accept": "application/json",
    }
    adzuna_params={
        "app_id": adzuna_id,
        "app_key": adzuna_key,
        "what": "junior data engineer"
    }
    try:
        adzuna_response = requests.get(adzuna_url, params=adzuna_params, headers=adzuna_headers, timeout=5)
        adzuna_response.raise_for_status()
        adzuna_json = adzuna_response.json()

        job_list = adzuna_json.get('results', [])

        clean_jobs = []

        for job in job_list:
            job_id = job.get('id', 0)
            job_title = job.get('title', 'Title not provided')
            salary_min = job.get('salary_min', 0)
            salary_max = job.get('salary_max', 0)
            company = job.get('company', {}).get('display_name', 'Unknown')
            job_location = job.get('location', {}).get('area', [])
            clean_area = ", ".join(job_location)
            country = f"{country.upper()}"

            clean_job = {
                "Job_ID": str(job_id),
                "Title": job_title,
                "Country": country,
                "Salary_Min": float(salary_min),
                "Salary_Max": float(salary_max),
                "Company": company,
                "Location": clean_area,
            }
            clean_jobs.append(clean_job)

        return clean_jobs

    except Exception as e:
        print(e)
