import re
import ast
import csv
import json

def modify_args(args):
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

    # return base
    
    # with open("newTools.json","r") as readfile:
    #     newTools = json.load(readfile)
    #     for tool in newTools:
    #         base[tool]= {}
    #         for arg in newTools[tool]["Arguments"]:
    #             base[tool][arg["ArgumentName"]] = arg["AllowedValues"]

    # print(base)
    # return base

    with open("dynamicDicts.csv","r") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            base[row[0]] = ast.literal_eval(row[1])
    
    return base

def edit_distance(str1, str2):
    """
    An optimized version of the edit distance algorithm for better performance.
    This implementation reduces unnecessary operations and improves cache locality.
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
    avl_tools = get_avl_tools()

    return general_update(tool_name,avl_tools.keys())

def update_arg_name(arg_name,tool_name):
    avl_tools = get_avl_tools()

    return general_update(arg_name,avl_tools[tool_name].keys())

def update_arg_val(arg_value,arg_name,tool_name,arg_index,tools,start,temp_index=None):
    if len(arg_value) == 0:
        return None

    avl_tools = get_avl_tools()
    arg_value = arg_value.strip()
    print("upargval1",arg_value)
    if arg_value[0] == '[':
        if arg_value[-1] != ']':
            arg_value += ']'
        arg_value = arg_value[1:-1].strip("\"").strip("\'").split(",")

        arg_val_list = []
        for value in arg_value:
            value = value.strip().strip("\"").strip("\'")
            value = update_arg_val(value,arg_name,tool_name,arg_index,tools,start,temp_index)
            arg_val_list.append(value)

        if len(arg_val_list) == 0:
            return avl_tools[tool_name][arg_name]

        return arg_val_list
        #print(arg_value)

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
    
def wrong_name_handler(index,tool_name,args,tools,arg_index,start,temp_index=None):

    if start == "var_":
        for var_ind in arg_index:
            args = args.replace(start+str(var_ind),f"$$PREV[{arg_index[var_ind]}]")

    elif start == "temp_":
        for temp_ind in arg_index:
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

    args = modify_args(args)

    copy_of_tool_name = tool_name
    tool_name = update_tool(tool_name)
    if not tool_name:
        tool = wrong_name_handler(index,copy_of_tool_name,args,tools,arg_index,start,temp_index)
    else:
        tool = make_tool(tool_name,args,arg_index,tools,start,temp_index)
    
    tools.append(tool)

    if start == "temp_":
        temp_index[index] = len(tools)-1
    else:
        arg_index[index] = len(tools)-1

    return tool

def if_handler(condition,arg_index):

    condition = condition.strip().strip('(').strip(')')

    for var_ind in arg_index:
        condition = condition.replace("var_"+str(var_ind),f"$$PREV[{arg_index[var_ind]}]")   

    condition = condition.replace("range","$$RANGE") 

    return {
        "tool_name": "conditional_magic",
        "condition": condition,
        "true": [],
        "false": []
    }

def for_handler(looping_var,arg_index,tools):
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
        if function_call.startswith("RANGE"):
            continue
        match = re.match(r"\s*(\w+)\((.*)\)",function_call)
        if match:
            
            process_tool(0,match.group(1),match.group(2),tools,arg_index,"var_")

            looping_var = looping_var.replace(function_call,f"$$PREV[{arg_index[0]}]")

    base["looping_var"] = looping_var 

    return base

def arg_splitter(args):
    split_args = []
    cur_arg = ""
    brack_count = 0
    last_comma = -1
    for i in args:
        if i == '[':
            brack_count += 1
        if i == ']':
            brack_count -= 1
        if brack_count == 0 and i == ',':
            split_args.append(cur_arg)
            cur_arg = ""
            continue
        if i == ',':
            last_comma = len(cur_arg)
        cur_arg += i
        if cur_arg.count("=")>1:
            split_args.append(cur_arg[:last_comma]+']')
            cur_arg = cur_arg[last_comma+1:]
    split_args.append(cur_arg)

    return split_args
        
def make_tool(tool_name,args,arg_index,tools,start,temp_index):

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

            #print("make_tool",arg_value)

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

    try:

        tools = []
        arg_index = {}
        inIf = False
        inElse = False
        inFor = False
        for i in string.split("\n"):

            match = re.match(r"\s*var_(\d+)\s*=\s*(\w+)\((.*)\)", i)

            if match:
                #print(match.group(0))
                inIf = False
                inElse = False
                inFor = False
                index = int(match.group(1)) 
                tool_name = match.group(2)
                args = match.group(3)

                process_tool(index,tool_name,args,tools,arg_index,start="var_")
                continue

            match = re.match(r"\s*if\s*(.*)\s*:", i)

            if match:
                inIf = True
                inFor = False
                temp_index = {}
                #print(match.group(0))

                condition = match.group(1)

                tools.append(if_handler(condition,arg_index))
                ifInd = len(tools)-1
                continue

            if inIf:
                
                match = re.match(r"\s*temp_(\d+)\s*=\s*(\w+)\((.*)\)", i)

                if match:
                    #print(match.group(0))
                    index = int(match.group(1))
                    tool_name = match.group(2)
                    args = match.group(3)

                    process_tool(index,tool_name,args,tools[ifInd]["true"],arg_index,"temp_",temp_index)
                    continue
                    #print(temp_index)

                match = re.match(r"\s*else:\s*",i)

                if match:
                    inElse = True
                    inIf = False
                    temp_index = {}
                    continue
            
            if inElse:

                match = re.match(r"\s*temp_(\d+)\s*=\s*(\w+)\((.*)\)", i)

                if match:
                    #print(match.group(0))
                    index = int(match.group(1))
                    tool_name = match.group(2)
                    args = match.group(3)

                    process_tool(index,tool_name,args,tools[ifInd]["false"],arg_index,"temp_",temp_index)
                    continue

            match = re.match(r"\s*for\s*loop_var\s*in\s*(.*)",i)

            if match:
                #print(match.group(1))
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
                    #print(match.group(0))
                    index = int(match.group(1))
                    tool_name = match.group(2)
                    args = match.group(3)

                    process_tool(index,tool_name,args,tools[forInd]["loop"],arg_index,"temp_",temp_index)
                    continue

        return json.dumps(tools, indent=2)

    except Exception as e:
        #print("Error: " ,e)
        return []


print(converter("""
var_1 = works_list(issue.priority = ["p4","p3"])

"""))
