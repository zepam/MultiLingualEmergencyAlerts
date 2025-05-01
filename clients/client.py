# Abstract Client parent
class Client:
    def __init__(self, key):
        self.key = key

    def gather_prompts(self, prompt_files, disaster, language, sending_agency=None, location=None, time=None, url=None):
        prompts = []
        for file in prompt_files:
            with open(file, "r") as file:

                prompt_text = file.read()
                prompt_text = prompt_text.replace("{DISASTER}", disaster)
                prompt_text = prompt_text.replace("{LANGUAGE}", language)
                if sending_agency:
                    prompt_text = prompt_text.replace("{SENDING_AGENCY}", sending_agency)
                if sending_agency:
                    prompt_text = prompt_text.replace("{LOCATION}", location)
                if sending_agency:
                    prompt_text = prompt_text.replace("{TIME}", time)

            prompts.append(prompt_text)
        return prompts

