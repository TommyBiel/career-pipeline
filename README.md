# Automated Remote Career Pipeline (Airflow & BigQuery)

## 📌 Project Overview
An automated, containerized ETL (Extract, Transform, Load) pipeline designed to aggregate, normalize, and store remote Junior Data Engineer job listings from the UK and US markets. The pipeline executes daily to track global salary trends, converting foreign currencies (GBP and USD) into PHP using real-time exchange rates, and loads the cleaned data into a Google Cloud BigQuery data warehouse.

## 🏗️ Architecture & Technologies
*   **Orchestration:** Apache Airflow (running locally via Docker)
*   **Data Extraction:** Adzuna API (Job Listings), ExchangeRate-API (Currency Conversion)
*   **Data Transformation:** Python, Pandas
*   **Data Warehouse:** Google Cloud Platform (BigQuery)
  
<img width="562" height="82" alt="career-pipeline drawio" src="https://github.com/user-attachments/assets/0f8fd616-a981-46c3-bd15-7884f800f31e" />

## ⚙️ Pipeline Workflow
1.  **Extract:** Airflow triggers a daily DAG that pings the Adzuna API for remote data engineering roles in the US and UK. Simultaneously, it fetches the live GBP-to-PHP and USD-to-PHP exchange rates.
2.  **Transform:** 
    *   Pandas converts the raw JSON payloads into structured DataFrames.
    *   Calculates and appends localized salary columns (`Salary_Min_PHP`, `Salary_Max_PHP`) for standardized financial comparison.
    *   Concatenates international data into a single master dataset.
3.  **Data Integrity (Anti-Duplication Shield):** 
    *   Queries the existing BigQuery table to retrieve a list of all historical `Job_ID`s.
    *   Filters the incoming Pandas DataFrame to isolate only brand-new, unseen job postings.
4.  **Load:** Securely appends only the net-new records into the BigQuery `remote_career_dataset`.

## 🚀 Why I Built This
To eliminate the manual overhead of scanning multiple international job boards. By containerizing the orchestration in Docker and automating the BigQuery load, the pipeline functions as a hands-off data aggregator, ensuring the warehouse only scales with unique, verified data points while preventing duplicate key errors.

## 📂 Repository Setup (Local Execution)
To run this pipeline locally, you will need a `.env` file containing your API credentials and a valid GCP Service Account JSON key placed in the `/dags` directory.
