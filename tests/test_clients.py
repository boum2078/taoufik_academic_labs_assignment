import pytest
from datetime import date
from clients.api_client import APIClientFactory, ClinicalTrialsAPIClient, MockedDataSourceClient

def test_api_client_factory():
    # Test valid client creation
    client = APIClientFactory.get_api_client("clinical_trials")
    assert isinstance(client, ClinicalTrialsAPIClient)
    
    client = APIClientFactory.get_api_client("mocked_api")
    assert isinstance(client, MockedDataSourceClient)
    
    # Test invalid client type
    with pytest.raises(ValueError):
        APIClientFactory.get_api_client("invalid_source")

def test_client_fetch():
    client = ClinicalTrialsAPIClient()
    studies = list(client.fetch_trials(date(2024, 10, 20), date(2024, 1, 21)))
    assert isinstance(studies, list)
    assert len(studies) == 1  
