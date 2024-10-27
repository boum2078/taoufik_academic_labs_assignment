from transformations.base_transformations import TransformationStrategy
import logging
import sys
class ClinicalTrialTransformationMapping(TransformationStrategy):
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

    def transform(self, raw_studies):
        if not raw_studies:
            self.logger.error("No raw studies provided")
            return []
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
        self.logger.warning(f'Transformed {len(structured_studies)} studies')
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


