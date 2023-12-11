from langchain.evaluation.parsing.json_distance import JsonEditDistanceEvaluator

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