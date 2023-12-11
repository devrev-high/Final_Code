from json_converter import converter
from langchain.evaluation.parsing.json_distance import JsonEditDistanceEvaluator
import re

def langeval(json1,json2):
    eval = JsonEditDistanceEvaluator()
    res = eval.evaluate_strings(prediction = json2, reference = json1)
    return res['score']

def precision(output, ground_truth):
    if len(output) == 0 and len(ground_truth) == 0:
        return 1
    elif len(output) != 0 and len(ground_truth) == 0:
        return 0
    elif len(output) == 0 and len(ground_truth) != 0:
        return 0

    gt_tools = set()
    for tool in ground_truth:
        gt_tools.add(tool['tool_name'])

    out_tools = set()
    for tool in output:
        out_tools.add(tool['tool_name'])

    precision = len(gt_tools.intersection(out_tools)) / len(out_tools)
    return precision

def recall(output, ground_truth):
    if len(output) == 0 and len(ground_truth) == 0:
        return 1
    elif len(output) != 0 and len(ground_truth) == 0:
        return 0
    elif len(output) == 0 and len(ground_truth) != 0:
        return 0
    gt_tools = set()
    for tool in ground_truth:
        gt_tools.add(tool['tool_name'])

    out_tools = set()
    for tool in output:
        out_tools.add(tool['tool_name'])
    recall = len(gt_tools.intersection(out_tools)) / len(gt_tools)
    return recall

def f1_score(output, ground_truth):
    prec = precision(output, ground_truth)
    rec = recall(output, ground_truth)
    f1 = 2 * prec * rec / (prec + rec + 1e-5)
    return f1 

def evaluator(eval_df):
    eval_df['Output'] = eval_df['Output'].apply(lambda x: converter(x))
    eval_df['Ground_Truth'] = eval_df['Ground_Truth'].apply(lambda x: converter(x))
    eval_df['Precision'] = eval_df.apply(lambda x: precision(x['Output'],x['Ground_Truth']), axis=1)
    eval_df['Recall'] = eval_df.apply(lambda x: recall(x['Output'],x['Ground_Truth']), axis=1)
    eval_df['F1_Score'] = eval_df.apply(lambda x: f1_score(x['Output'],x['Ground_Truth']), axis=1)
    eval_df['Langchain'] = eval_df.apply(lambda x: 1 - langeval(x['Output'],x['Ground_Truth']), axis=1)

    return eval_df['Precision'].mean(), eval_df['Recall'].mean(), eval_df['F1_Score'].mean(), eval_df['Langchain'].mean(), eval_df['Latency'].mean()

def clean_output(input_text):
    regex_pattern = r'The output should be:\s*(var_\d+\s*=\s*\w+\(\w+\=[^\n]+(?:\n\s*)*)+'
    match = re.search(regex_pattern, input_text)
    # Check if a match is found
    if match:
        # Extract the matched text
        extracted_text = match.group(0)
        return(extracted_text)
    else:
        return("")