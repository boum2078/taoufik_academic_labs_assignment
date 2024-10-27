from datetime import date
from pipelines.trial_pipeline import ClinicalTrialPipeline

from dotenv import load_dotenv

load_dotenv(override=True)

if __name__ == "__main__":
    start_date = date(2024, 10, 20)
    end_date = date(2024, 10, 22)
    pipeline = ClinicalTrialPipeline()
    pipeline.run(start_date, end_date)
