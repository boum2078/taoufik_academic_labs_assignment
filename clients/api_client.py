import requests
from datetime import date
import json
import logging
import sys
import time

class APIClient:
    def fetch_trials(self, start_date: date, end_date: date):
        raise NotImplementedError("Subclasses should implement this method")

class ClinicalTrialsAPIClient(APIClient):
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            handlers=[
                logging.FileHandler('clinical_trials_processing.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch_trials(self, start_date: date, end_date: date, page_size: int = 500):
        url = f"https://clinicaltrials.gov/api/v2/studies"
        studies = []
        page_token = None  # Token to handle pagination
        params = {
            "format": "json",
            'query.term': f"AREA[LastUpdatePostDate]RANGE[{start_date},{end_date}]",            
            "pageSize": page_size,
            "fields": ",".join([
                "NCTId",
                "BriefTitle",
                "StartDate",
                "CompletionDate",
                "LeadSponsorName",
                "ResponsiblePartyInvestigatorFullName",
                "ResponsiblePartyInvestigatorAffiliation",
                "OverallStatus",
                "Phase",
                "EnrollmentCount",
                "OverallOfficialName",
                "OverallOfficialAffiliation",
                "OverallOfficialRole",
                "LocationFacility",
                "LocationCity",
                "LocationCountry",
                "EligibilityCriteria"
            ])
        }

        try:
            while True:
                # Add page token to params if it's available for the next page
                if page_token:
                    params['pageToken'] = page_token

                # Make the API request
                response = requests.get(url, params=params)
                response.raise_for_status()  # Raise an error for bad status codes

                # Parse the JSON response
                data = response.json()
                studies = data.get("studies", [])
                yield studies

                page_token = data.get("nextPageToken")
                if not page_token:
                    self.logger.warning('no more page token')
                    break  # Exit the loop if there is no next page
                # if len(studies) < page_size:
                #     self.logger.warn('no more studies')
                #     break
                time.sleep(0.1)  # Rate limiting

        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Error streaming studies: {str(e)}")
            return []
        
    def _structure_studies(self, raw_studies):
        structured_studies = []
        for study in raw_studies:
            protocol_section = study.get('protocolSection', {})
            
            # Extract modules safely
            identification_module = protocol_section.get('identificationModule', {})
            status_module = protocol_section.get('statusModule', {})
            design_module = protocol_section.get('designModule', {})
            contacts_locations_module = protocol_section.get('contactsLocationsModule', {})
            eligibility_module = protocol_section.get('eligibilityModule', {})

            # Extract principal investigator info
            overall_officials = contacts_locations_module.get('overallOfficials', [])
            pi_info = next((
                official for official in overall_officials 
                if official.get('role', '').upper() == 'PRINCIPAL_INVESTIGATOR'
            ), {})

            structured_study = {
                "trialId": identification_module.get('nctId', 'Unknown'),
                "title": identification_module.get('briefTitle', 'Unknown'),
                "startDate": self._get_date(status_module.get('startDateStruct')),
                "endDate": self._get_date(status_module.get('completionDateStruct')),
                "phase": design_module.get('phases', ['Unknown']),
                "principalInvestigator": {
                    "name": pi_info.get('name', 'Unknown'),
                    "affiliation": pi_info.get('affiliation', 'Unknown'),
                },
                "locations": self._extract_locations(contacts_locations_module),
                "eligibilityCriteria": eligibility_module.get('eligibilityCriteria', 'Unknown')
            }
            structured_studies.append(structured_study)
        return structured_studies
    
    def _get_date(self, date_struct):
        if not date_struct:
            return 'Unknown'
        return date_struct.get('date', 'Unknown')

    def _extract_locations(self, contacts_locations_module):
        locations = contacts_locations_module.get('locations', [])
        return [
            {
                "facility": location.get('facility', 'Unknown'),
                "city": location.get('city', 'Unknown'),
                "country": location.get('country', 'Unknown'),
            } for location in locations
        ] if locations else [{"facility": "Unknown", "city": "Unknown", "country": "Unknown"}]
    

class MockedDataSourceClient(APIClient):
    def fetch_trials(self, start_date: date, end_date: date, page_size: int = 500):
        # Simulated data for demonstration purposes : overlapping dates (start_date)
        # url = f"{CLINICAL_TRIALS_API_URL}/clinical_trials?start_date={start_date}&end_date={start_date}"
        # response = requests.get(url)
        # response.raise_for_status()
        # return response.json()["studies"]
        yield []

class APIClientFactory:
    
    @staticmethod
    def get_api_client(source_name):
        match source_name:
            case "clinical_trials":
                return ClinicalTrialsAPIClient()
            case "mocked_api":
                return MockedDataSourceClient()
            case _:
                raise ValueError(f"Unknown API client source: {source_name}")
            
if __name__ == "__main__":
    result = []
    crawler = APIClientFactory.get_api_client("clinical_trials")
    ## to be parallelized
    for studies in crawler.fetch_trials(date(2024, 10, 20), date(2024, 10, 21)):
        pass
        