import re
import json
import Levenshtein
from langchain.evaluation.parsing.json_distance import JsonEditDistanceEvaluator

def diff(string1, string2):
  string1 = json.dumps(string1)
  string2 = json.dumps(string2)
  if(len(string1) == 0 and len(string2) == 0):
    return 1
  else:
    maxm = max(len(string1) , len(string2))
    return (1-(Levenshtein.distance(string1, string2))/maxm)

def jaccard_similarity(actual, predicted):
  actual = re.sub('[^A-Za-z]+', ' ', actual).split()
  predicted = re.sub('[^A-Za-z]+', ' ', predicted).split()
  intersection = 0
  for a in actual:
    if a in predicted:
      intersection += 1
      predicted.remove(a)
  union = len(actual+predicted)
  return intersection/union if union!=0 else 0

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