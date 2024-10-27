from dotenv import load_dotenv
load_dotenv(override=True)
from langchain import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from transformations.base_transformations import TransformationStrategy
from langchain.globals import set_verbose, get_verbose
set_verbose(False)  # new way
import logging
import sys


class DiseaseExtractionTransformation(TransformationStrategy):
    def __init__(self):
        # Set up logging similar to trial transformation
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s - PID:%(process)d',
            handlers=[
                logging.FileHandler('disease_extraction_processing.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize LLM components
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.prompt_template = PromptTemplate(
            input_variables=["text"],
            template="Identify and list all diseases or medical conditions in the following text. Do not include any other text, if it does not incldue any disease return an empty string.\n\nText: {text}"
        )
        self.llm_chain = self.prompt_template | self.llm

    def transform(self, text):
        if not text:
            self.logger.warning("No text provided for disease extraction")
            return 'No diseases found because no inclusion criteria was found'
        
        try:
            response = self.llm_chain.invoke({'text': text})
            extracted_diseases = response.content  # Updated to access content
            # self.logger.info(f"Successfully extracted {(extracted_diseases)} diseases")
            return extracted_diseases
        except Exception as e:
            self.logger.error(f"Error during disease extraction: {str(e)}")
            return f'No diseases found because of {str(e)}'
        
if __name__ == "__main__":
    extractor = DiseaseExtractionTransformation()
    text = "The patient suffers from asthma, hypertension, and diabetes."
    diseases = extractor.transform(text)
    print(diseases)
