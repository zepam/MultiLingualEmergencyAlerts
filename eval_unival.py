"""
git clone https://github.com/maszhongming/UniEval.git
cd UniEval
pip install transformers >= 4.17.0.dev0
accelerate
datasets >= 1.8.0
sentencepiece != 0.1.92
protobuf
rouge-score
nltk
py7zr
torch >= 1.3
evaluate
prettytable
"""

# get scores for factual consistency
from UniEval.utils import convert_to_json
from UniEval.metric.evaluator import get_evaluator

task = 'fact'

# a list of source documents
src_list = ['Peter and Elizabeth took a taxi to attend the night party in the city. \
             While in the party, Elizabeth collapsed and was rushed to the hospital.']
# a list of model outputs (claims) to be evaluataed
output_list = ['Tom was rushed to hospital.']

# Prepare data for pre-trained evaluators
data = convert_to_json(output_list=output_list, src_list=src_list)
# Initialize evaluator for a specific task
evaluator = get_evaluator(task)
# Get factual consistency scores
eval_scores = evaluator.evaluate(data, print_result=True)