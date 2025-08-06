import json
import datetime
import os
import logging

class Collector:
    """
    Collects responses with a specific hierarchy for services
    other than 'google_translate' and a simplified timestamp.
    """
    def __init__(self, output_file, logger, batch_size=5):
        self.output_file = output_file
        self.logger = logger
        self.batch_size = batch_size
        self.data = {}
        self.responses_added_since_last_save = 0

    def _save_to_file(self):
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                self.logger.error(f"Error creating directory {output_dir}: {e}")
                return

        temp_file = f'{self.output_file}.tmp'
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            os.replace(temp_file, self.output_file)
            self.logger.info(f"Saved {self.responses_added_since_last_save} responses to '{self.output_file}'.")
            self.responses_added_since_last_save = 0
        except (IOError, OSError) as e:
            self.logger.error(f"Error saving data to '{self.output_file}': {e}")
            
    def add_response(self, service, language, disaster, prompt, response):
        """
        Adds a new response to the hierarchical data structure based on the service name.
        """
        # Build the hierarchical data structure
        if service not in self.data:
            self.data[service] = {}
        if language not in self.data[service]:
            self.data[service][language] = {}
        if disaster not in self.data[service][language]:
            self.data[service][language][disaster] = {}

        # Get the simplified timestamp
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        response_data = {
            "response": response,
            "timestamp": timestamp
        }

        # Handle the nesting based on service name
        if service == "google_translate":
            # For google_translate, the list of responses is the direct value of the 'disaster' key
            if type(self.data[service][language][disaster]) is not list:
                 self.data[service][language][disaster] = []
            self.data[service][language][disaster].append(response_data)
        else:
            # All other services have a 'prompt' layer
            if prompt not in self.data[service][language][disaster]:
                self.data[service][language][disaster][prompt] = []
            self.data[service][language][disaster][prompt].append(response_data)
            
        self.logger.info(f"Added response for {service}/{language}/{disaster}.")
        
        self.responses_added_since_last_save += 1
        if self.responses_added_since_last_save >= self.batch_size:
            self._save_to_file()
            
    def save_remaining(self):
        if self.responses_added_since_last_save > 0:
            self._save_to_file()