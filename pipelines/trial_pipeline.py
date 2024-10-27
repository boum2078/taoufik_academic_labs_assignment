import sys

import re
import logging
import json

from datetime import date
from clients.api_client import APIClientFactory
from clients.db_client import DBClientFactory
from transformations.trial_transformation import ClinicalTrialTransformationMapping
from transformations.llm_extraction import DiseaseExtractionTransformation
from concurrent.futures import ThreadPoolExecutor

class ClinicalTrialPipeline:
    def __init__(self, api_source="clinical_trials", db_type="mongo"):
        self.crawler = APIClientFactory.get_api_client(api_source)
        self.db_client = DBClientFactory.get_db_client(db_type)
        # self.llm_facade = DiseaseExtractionTransformation()
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            handlers=[
                logging.FileHandler('clinical_trials_processing.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def enrich(self, parsed_studies):
        """
        Extract eligibility criteria from multiple parsed studies in parallel using threads.
        
        Args:
            parsed_studies (list): A list of dictionaries containing parsed study data.
        
        Returns:
            list: A list of dictionaries containing study IDs and their eligibility criteria.
        """
        from concurrent.futures import ThreadPoolExecutor
        
        # Use more threads since they're lighter than processes
        num_workers = min(500, len(parsed_studies))  # Cap at 32 threads
        self.logger.warning(f'Starting parallel processing with {num_workers} threads')
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            enriched_studies = list(executor.map(self._process_single_study, parsed_studies))
        
        self.logger.info(f'Enriched {len(enriched_studies)} studies in parallel')
        return enriched_studies
          
    @staticmethod
    def _process_single_study(study):
        """Helper function for parallel processing of a single study"""
        if study.get('trialId') and study.get('eligibilityCriteria'):
            # Create helper function to avoid passing self
            def get_inclusion_criteria(eligibility_criteria):
                inclusion_pattern = r"Inclusion Criteria:(.+?)(?:Exclusion Criteria:|$)"
                match = re.search(inclusion_pattern, eligibility_criteria, re.DOTALL | re.IGNORECASE)
                return match.group(1) if match else ""

            inclusion_criteria = get_inclusion_criteria(study['eligibilityCriteria'])
            study['inclusion_criteria'] = inclusion_criteria.strip()
            # Create a new LLM facade instance since we're in a different process
            llm_facade = DiseaseExtractionTransformation()
            study['diseases'] = llm_facade.transform(inclusion_criteria)
            return study
        return study
        
    def run(self, start_date, end_date):
        
        for studies in self.crawler.fetch_trials(start_date, end_date, page_size= 500):
            # Apply all transformation steps
            parsed_studies = ClinicalTrialTransformationMapping().transform(studies)
            enriched_studied = self.enrich(parsed_studies)
            self.save_to_db(enriched_studied)
            
    def save_to_db(self, parsed_studies):
        # for study in parsed_studies:
        self.db_client.insert_many_documents(parsed_studies)

if __name__ == "__main__":
    pipeline = ClinicalTrialPipeline()
    pipeline.run(date(2024, 10, 20), date(2024, 10, 21))