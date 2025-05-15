# Abstract Client parent
class Client:
    def __init__(self, key):
        self.key = key
        self.temperature = 0.7
        self.max_tokens = 2048
        self.top_p = 1.0

    def gather_prompt(self, prompt_file, disaster, language, sending_agency=None, location=None, time=None, url=None):
        with open(prompt_file, "r") as file:
            prompt_text = file.read()
            prompt_text = prompt_text.replace("{DISASTER}", disaster)
            prompt_text = prompt_text.replace("{LANGUAGE}", language)
            if sending_agency:
                prompt_text = prompt_text.replace("{SENDING_AGENCY}", sending_agency)
            if sending_agency:
                prompt_text = prompt_text.replace("{LOCATION}", location)
            if sending_agency:
                prompt_text = prompt_text.replace("{TIME}", time)

        return prompt_text
