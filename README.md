# Multilingual Emergency Alerts
A toolkit for generating, collecting, and evaluating multilingual emergency alert messages using a variety of large language models (LLMs) and translation APIs.


## Features

- **Automated Response Collection:** Query multiple LLMs and translation services (ChatGPT, Gemini, DeepSeek, Google Translate, DeepL) for emergency alert translations in many languages.
- **Prompt Engineering:** Test and compare different prompt strategies for each service and scenario.
- **Evaluation Suite:** Evaluate generated outputs using metrics such as ROUGE, BLEU, BERTScore, and COMET.
- **Result Aggregation:** Combine and visualize results from multiple runs and services.
- **Extensible:** Easily add new languages, services, or evaluation metrics.

---

## Latest BLEU Results
![BLEU results broken down by LANGUAGE vs. SERVICE. The data is filtered on translation category, which keeps prompts and translations. The LANGUAGE (services languages.csv) filter keeps 13 of 13 members. The BLEU filter ranges from 0.10 to 66.79. Google Translate and DeepL show the highest results.](data/bleu.png)


