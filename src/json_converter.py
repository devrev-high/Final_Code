import json
import re
import csv
import ast

def modify_args(args):
    """
    Removes comments (if present somehow)
    """
    s = ''
    cnt = 1
    for j in args:
        if j == '(': cnt += 1
        elif j == ')': cnt -= 1
        if cnt == 0:
            break
        s += j
    return s

def get_avl_tools():
    """
    Function to get available tools as a dictionary in the format {"tool_name": {"arg_name":["allowed_arg_value"]}}
    If no restrictions on arg_value, replace list with "anything"
    """

    base = {
        "works_list": {
            "applies_to_part": "anything",
            "created_by": "anything",
            "issue.priority": ["p0", "p1", "p2", "p3"],
            "issue.rev_orgs": "anything",
            "limit": "anything",
            "owned_by": "anything",
            "stage.name": "anything",
            "ticket.needs_response": ["True", "False"],
            "ticket.rev_org": "anything",
            "ticket.severity": ["blocker", "low", "medium", "high"],
            "ticket.source_channel": "anything",
            "type": ["issue","ticket","task"]
        },
        "summarize_objects": {
            "objects": "anything"
        },
        "prioritize_objects": {
            "objects": "anything"
        },
        "add_work_items_to_sprint":{
            "work_ids": "anything",
            "sprint_id": "anything"
        },
        "get_sprint_id":{
        },
        "get_similar_work_items":{
            "work_id": "anything"
        },
        "search_object_by_name":{
            "query": "anything"
        },
        "create_actionable_tasks_from_text":{
            "text": "anything"
        },
        "who_am_i":{
        }
    }

    with open("../resources/Tool_list/dynamicDicts.csv","r") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            base[row[0]] = ast.literal_eval(row[1])
    
    return base

def edit_distance(str1, str2):
    """
    Function to calculate edit distance between two strings. 
    Few hardcoded variants that correct common model mistakes.
    """

    if str1 == "whoami" and str2 == "who_am_i" : 
        return 0
    if str1 == "get_current_sprint_id" and str2 == "get_sprint_id": 
        return 0
    if str1 == "create_actions_from_text" and str2 == "create_actionable_tasks_from_text":
        return 0
    if str1 == "work_type" and str2 == "type":
        return 0

    if len(str1) < len(str2):
        str1, str2 = str2, str1

    previous_row = list(range(len(str2) + 1))
    for i, c1 in enumerate(str1):
        current_row = [i + 1]
        for j, c2 in enumerate(str2):
            # Cost of substitutions is same as previous row and column + 1 if characters are different
            cost = 0 if c1 == c2 else 1
            current_row.append(min(current_row[j] + 1,            # Deletion
                                   previous_row[j + 1] + 1,      # Insertion
                                   previous_row[j] + cost))      # Substitution
        previous_row = current_row

    return previous_row[-1]

def general_update(name,nameslist):
    """
    Returns the closest match to the the given name in the nameslist.
    If the closest edit distance is more than 50% of the of given names length, returns None.
    """
    d = len(name)
    cur_name = name
    for key in nameslist:
        cur_d = edit_distance(name,key)
        if cur_d < d:
            d = cur_d
            cur_name = key
    
    if 2*d <= len(name):
        return cur_name

    return None

def update_tool(tool_name):
    """
    Gets the closest tool name to the one given using general_update
    """
    avl_tools = get_avl_tools()

    return general_update(tool_name,avl_tools.keys())

def update_arg_name(arg_name,tool_name):
    """
    Gets the closest arg name to the one given(for the given tool) using general_update
    """
    avl_tools = get_avl_tools()

    return general_update(arg_name,avl_tools[tool_name].keys())

def update_arg_val(arg_value,arg_name,tool_name,arg_index,tools,start,temp_index=None):
    """
    Returns an updated arg val corresponding to the specific tool and argument given. 
    If given argument is determined to be invalid, returns "$$INV_ARG".
    Handles the cases of argument values being function calls, and recursively calls itself to handle lists
    """
    if len(arg_value) == 0:
        return None

    avl_tools = get_avl_tools()
    arg_value = arg_value.strip()
  
    if arg_value[0] == '[':
        if arg_value[-1] != ']':
            arg_value += ']'
        arg_value = arg_value[1:-1].strip("\"").strip("\'").split(",")

        arg_val_list = []
        for value in arg_value:
            value = value.strip().strip("\"").strip("\'")
            value = update_arg_val(value,arg_name,tool_name,arg_index,tools,start,temp_index)
            arg_val_list.append(value)

        return arg_val_list
       

    if arg_value.startswith("$$"):
        return arg_value

    if arg_value.find('(') != -1:
        match = re.match(r"\s*(\w+)\((.*)\)",arg_value)
        process_tool(0,match.group(1),match.group(2),tools,arg_index,start,temp_index)

        if start == "temp_":
            arg_value = f"$$PREV[{temp_index[0]}]"
        elif start == "var_":
            arg_value = f"$$PREV[{arg_index[0]}]"

    if avl_tools[tool_name][arg_name] == 'anything' or arg_value in avl_tools[tool_name][arg_name]:
        return arg_value

    return "$$INV_ARG"
    
def wrong_name_handler(tool_name,args,arg_index,start,temp_index=None):
    """
    Handles the case of a hallucinated tool (or any tool that was unable to be resolved by the edit distance)
    Is similar to update_arg_val but since there are no restrictions on argument names or values, 
    it returns them as they are
    """
    if start == "var_":
        for var_ind in arg_index:
            args = args.replace(start+str(var_ind),f"$$PREV[{arg_index[var_ind]}]")

    elif start == "temp_":
        for temp_ind in temp_index:
            args = args.replace(start+str(temp_ind),f"$$PREV[{temp_index[temp_ind]}]")
        for var_ind in arg_index:
            args = args.replace("var_"+str(var_ind),f"$$GLOB_PREV[{arg_index[var_ind]}]")

    tool = {"tool_name": tool_name, "arguments": []}

    split_args = arg_splitter(args)

    for arg in split_args:
        if "=" in arg:

            arg_name, arg_value = arg.split("=", 1)
            arg_name = arg_name.strip()
            arg_value = arg_value.strip().replace("\"","").replace("\'","")

            if arg_value[0] == '[':
                arg_value_list = []
                for list_arg in arg_value[1:-1].split(","):
                    arg_value_list.append(list_arg)
                tool["arguments"].append({"argument_name": arg_name,"argument_value": arg_value_list})
            else:
                tool["arguments"].append({"argument_name": arg_name,"argument_value": arg_value})

    return tool

def process_tool(index,tool_name,args,tools,arg_index,start,temp_index=None):
    """
    Processes a line into a valid tool dictionary. Makes use of multiple helper functions.
    """
    args = modify_args(args)

    copy_of_tool_name = tool_name
    tool_name = update_tool(tool_name)
    if not tool_name:
        tool = wrong_name_handler(copy_of_tool_name,args,arg_index,start,temp_index)
    else:
        tool = make_tool(tool_name,args,arg_index,tools,start,temp_index)
    
    tools.append(tool)

    if start == "temp_":
        temp_index[index] = len(tools)-1
    else:
        arg_index[index] = len(tools)-1

    return tool

def if_handler(condition,arg_index,tools):
    """
    Returns the processed if case as a conditional_magic dictionary
    """

    condition = condition.strip()

    if condition[-1] == ':':
        condition = condition[:-1]

    if condition[0] == '(' and condition[-1] == ')':
        condition = condition[1:-1]

    for var_ind in arg_index:
        condition = condition.replace("var_"+str(var_ind),f"$$PREV[{arg_index[var_ind]}]")   

    condition = condition.replace("range","$$RANGE") 

    function_calls = re.findall(r"\w+\s*\([^)]*\)", condition)
    for function_call in function_calls:
        function_call = function_call.strip()
        if function_call.startswith("RANGE") or function_call.startswith("$$RANGE"):
            continue
        match = re.match(r"\s*(\w+)\((.*)\)",function_call)
        if match:
            process_tool(0,match.group(1),match.group(2),tools,arg_index,"var_")

            condition = condition.replace(function_call,f"$$PREV[{arg_index[0]}]")

    return {
        "tool_name": "conditional_magic",
        "condition": condition,
        "true": [],
        "false": []
    }

def for_handler(looping_var,arg_index,tools):
    """
    Returns the processed for case as a iterational_magic dictionary
    """

    base =  {
        "tool_name": "iterational_magic",
        "looping_var": "",
        "loop": []
    }

    colon_pos = looping_var.find(":")
    hash_pos = looping_var.find("#")
    if colon_pos != -1:
        looping_var = looping_var[:colon_pos]
    elif hash_pos != -1:
        looping_var = looping_var[:hash_pos]

    looping_var = looping_var.strip()

    for var_ind in arg_index:
        looping_var = looping_var.replace("var_"+str(var_ind),f"$$PREV[{arg_index[var_ind]}]")   

    looping_var = looping_var.replace("range","$$RANGE") 

    function_calls = re.findall(r"\w+\s*\([^)]*\)", looping_var)
    for function_call in function_calls:
        function_call = function_call.strip()
        if function_call.startswith("RANGE") or function_call.startswith("$$RANGE"):
            continue
        match = re.match(r"\s*(\w+)\((.*)\)",function_call)
        if match:
            
            process_tool(0,match.group(1),match.group(2),tools,arg_index,"var_")

            looping_var = looping_var.replace(function_call,f"$$PREV[{arg_index[0]}]")

    base["looping_var"] = looping_var 

    return base

def arg_splitter(args):
    """
    Returns the args split on the basis of different argument names
    """
    split_args = []
    cur_arg = ""
    brack_count = 0
    last_comma = -1
    for i in args:
        if i == '[':
            brack_count += 1
        if i == ']':
            brack_count -= 1
        if i == ',':
            last_comma = len(cur_arg)
        if brack_count == 0 and i == ',':
            split_args.append(cur_arg)
            cur_arg = ""
            continue
        cur_arg += i
        if cur_arg.count("=")>1:
            split_args.append(cur_arg[:last_comma]+']')
            cur_arg = cur_arg[last_comma+1:]
    split_args.append(cur_arg)
   
    return split_args
        
def make_tool(tool_name,args,arg_index,tools,start,temp_index):
    """
    The correct tool name counterpart to wrong_name_handler. Returns each tool as a processed dictionary
    """
    if start == "var_":
        for var_ind in arg_index:
            args = args.replace(start+str(var_ind),f"$$PREV[{arg_index[var_ind]}]")

    elif start == "temp_":
        for temp_ind in temp_index:
            args = args.replace(start+str(temp_ind),f"$$PREV[{temp_index[temp_ind]}]")
        for var_ind in arg_index:
            args = args.replace("var_"+str(var_ind),f"$$GLOB_PREV[{arg_index[var_ind]}]")
        args = args.replace("loop_var","$$LOOP_VAR")

    tool = {"tool_name": tool_name, "arguments": []}

    split_args = arg_splitter(args)

    for arg in split_args:
        arg = arg.strip()
        if "=" in arg:
            arg_name, arg_value = arg.split("=", 1)
            arg_name = arg_name.strip()
            arg_value = arg_value.strip().strip("\"").strip("\'")

         

            arg_name = update_arg_name(arg_name,tool_name)
            if not arg_name:
                continue

            arg_value = update_arg_val(arg_value,arg_name,tool_name,arg_index,tools,start,temp_index)
            if not arg_value:
                continue

            tool["arguments"].append({"argument_name": arg_name, "argument_value": arg_value})

    if len(tool["arguments"]) != 0:
        return tool

    avl_tools = get_avl_tools()

    if len(avl_tools[tool_name]) == 0:
        return tool

    if len(split_args) == len(avl_tools[tool_name]):

        for arg_name,arg in zip(avl_tools[tool_name],split_args):
            arg_value = arg.strip().strip("\"").strip("\'")

            arg_value = update_arg_val(arg_value,arg_name,tool_name,arg_index,tools,start,temp_index)
            if not arg_value:
                continue

            tool["arguments"].append({"argument_name": arg_name, "argument_value": arg_value})

    return tool

def converter(string):
    """
    The driver function. Processed each line individually and calls functions on the basis of matches.
    """

    try:

        tools = []
        arg_index = {}
        inIf = False
        inElse = False
        inFor = False
        for i in string.split("\n"):

            match = re.match(r"\s*var_(\d+)\s*=\s*(\w+)\((.*)\)", i)

            if match:
        
                inIf = False
                inElse = False
                inFor = False
                index = int(match.group(1)) 
                tool_name = match.group(2)
                args = match.group(3)

                if tool_name.strip() == "if":
                    tools.append(if_handler(args,arg_index,tools))
                    ifInd = len(tools)-1
                    inIf = True
                    inFor = False
                    temp_index = {}
                    continue

                process_tool(index,tool_name,args,tools,arg_index,start="var_")
                continue

            match = re.match(r"\s*if\s*(.*)", i)

            if match:
                inIf = True
                inFor = False
                temp_index = {}
            

                condition = match.group(1)

                tools.append(if_handler(condition,arg_index,tools))
                ifInd = len(tools)-1
                continue

            if inIf:
                
                match = re.match(r"\s*temp_(\d+)\s*=\s*(\w+)\((.*)\)", i)

                if match:
                 
                    index = int(match.group(1))
                    tool_name = match.group(2)
                    args = match.group(3)

                    process_tool(index,tool_name,args,tools[ifInd]["true"],arg_index,"temp_",temp_index)
                    continue
                 

                match = re.match(r"\s*else:\s*",i)

                if match:
                    inElse = True
                    inIf = False
                    temp_index = {}
                    continue
            
            if inElse:

                match = re.match(r"\s*temp_(\d+)\s*=\s*(\w+)\((.*)\)", i)

                if match:
                 
                    index = int(match.group(1))
                    tool_name = match.group(2)
                    args = match.group(3)

                    process_tool(index,tool_name,args,tools[ifInd]["false"],arg_index,"temp_",temp_index)
                    continue

            match = re.match(r"\s*for\s*loop_var\s*in\s*(.*)",i)

            if match:
             
                inIf = False
                looping_var = match.group(1)
                temp_index = {}
                tools.append(for_handler(looping_var,arg_index,tools))
                inFor = True
                forInd = len(tools)-1
                continue

            if inFor:

                match = re.match(r"\s*temp_(\d+)\s*=\s*(\w+)\((.*)\)", i)

                if match:
              
                    index = int(match.group(1))
                    tool_name = match.group(2)
                    args = match.group(3)

                    process_tool(index,tool_name,args,tools[forInd]["loop"],arg_index,"temp_",temp_index)
                    continue

        return tools

    except Exception as e:
        return []
