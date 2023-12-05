def tool():
    tools_list ='''
                def works_list(applies_to_part=None, created_by=None, issue_priority=None,
                issue_rev_orgs=None, limit=50, owned_by=None, stage_name=None,
                ticket_needs_response=False, ticket_rev_org=None,
                ticket_severity=None, ticket_source_channel=None, work_type=None):
                """
                Returns a list of work items matching the request

                Parameters:
                    applies_to_part (list): Filters for work belonging to any of the provided parts
                    created_by (list): Filters for work created by any of these users
                    issue.priority (list): Filters for issues with any of the provided priorities. Allowed values: p0, p1, p2, p3
                    issue.rev_orgs (list): Filters for issues with any of the provided Rev organizations
                    limit (int): The maximum number of works to return. The default is '50'
                    owned_by (list): Filters for work owned by any of these users
                    stage.name (list): Filters for records in the provided stage(s) by name
                    ticket.needs_response (bool): Filters for tickets that need a response
                    ticket.rev_org (list): Filters for tickets associated with any of the provided Rev organizations
                    ticket.severity (list): Filters for tickets with any of the provided severities. Allowed values: blocker, high, low, medium
                    ticket.source_channel (list): Filters for tickets with any of the provided source channels
                    type (list): Filters for work of the provided types. Allowed values: issue, ticket, task

                Returns:
                    list: Matching work items
                """

                def summarize_objects(objects):
                """
                Summarizes a list of objects. The logic of how to summarize a
                particular object type is an internal implementation detail

                Parameters:
                    objects (list): List of objects to summarize

                Returns:
                    text: Summarized text of the objects
                """

                def prioritize_objects(objects):
                """
                Returns a list of objects sorted by priority. The logic of what constitutes
                priority for a given object is an internal implementation detail

                Parameters:
                    objects (list): A list of objects to be prioritized

                Returns:
                    list: Prioritized objects
                """

                def add_work_items_to_sprint(work_ids, sprint_id):
                """
                Adds the given work items to the sprint

                Parameters:
                    work_ids (list): A list of work item IDs to be added to the sprint
                    sprint_id (str): The ID of the sprint to which the work items should be added
                """

                def get_sprint_id():
                """
                Returns the ID of the current sprint
                """

                def get_similar_work_items(work_id):
                """
                Returns a list of work items that are similar to the given work item

                Parameters:
                    work_id (str): The ID of the work item for which you want to find similar items

                Returns:
                    list: Similar work items
                """

                def search_object_by_name(query):
                """
                Given a search string, returns the ID of a matching object in the system of record.
                If multiple matches are found, it returns the one where the confidence is highest

                Parameters:
                    query (str): The search string, could be for example customer’s name, part name, user name

                Returns:
                    str: ID of matching object
                """

                def create_actionable_tasks_from_text(text):
                """
                Given a text, extracts actionable insights, and creates tasks for them,
                which are kind of a work item

                Parameters:
                    text (str): The text from which the actionable insights need to be created

                Returns:
                    list: tasks created from the given text

                """

                def who_am_i():
                """
                Returns the string ID of the current user
                """
        '''
    return tools_list

def query():
    query_list = '''

        Queries:
        1. Summarize work items similar to don:core:dvrv-us-1:devo/0:issue/1
        2. What is the meaning of life?
        3. Prioritize my P0 issues and add them to the current sprint
        4. Summarize high severity tickets from the customer UltimateCustomer
        5. What are my all issues in the triage stage under part FEAT-123? Summarize them.
        6. Find similar tasks to TASK-321, summarize and rank them by priority

        Answers:

        1.
        var_1 = get_similar_work_items(work_id="don:core:dvrv-us-1:devo/0:issue/1")
        var_2 = summarize_objects(objects=var1)

        2.
        # Cannot be solved using the given functions

        3.
        var_1 = who_am_i()
        var_2 = works_list(type = ["issue"], issue.priority=["p0"], owned_by=[var_1])
        var_3 = prioritize_objects(objects=var_2)
        var_4 = get_sprint_id()
        var_5 = add_work_items_to_sprint(work_ids=var_3, sprint_id=var_4)

        4.
        var_1 = search_object_by_name(query="UltimateCustomer")
        var_2 = works_list(type = ["ticket"], ticket.rev_org=[var_1])
        var_3 = summarize_objects(objects=var_2)

        5.
        var_1 = who_am_i()
        var_2 = works_list(stage.name=["triage"], applies_to_part=["FEAT-123"], owned_by=[var_1], type = ["issue"])
        var_3 = summarize_objects(objects=var_2)

        6.
        var_1 = get_similar_work_items(work_id="TASK-321")
        var_2 = summarize_objects(objects=var_1)
        var_3 = prioritize_objects(objects=var_1)

        '''
    return query_list

def outputMessage():
    messages = {
    "role":"system",
    "content": '''

    You are an extremely helpful and extremely faithful chatbot. You call given functions calls to complete a query. You only know these functions and nothing else:

    def works_list(applies_to_part=None, created_by=None, issue_priority=None,
issue_rev_orgs=None, limit=50, owned_by=None, stage.name=None,
ticket.needs_response=False, ticket.rev_org=None,
ticket.severity=None, ticket.source_channel=None, type=None):
"""
Returns a list of work items matching the request

Parameters:
    applies_to_part (list): Filters for work belonging to any of the provided parts
    created_by (list): Filters for work created by any of these users
    issue.priority (list): Filters for issues with any of the provided priorities. Allowed values: p0, p1, p2, p3
    issue.rev_orgs (list): Filters for issues with any of the provided Rev organizations
    limit (int): The maximum number of works to return. The default is '50'
    owned_by (list): Filters for work owned by any of these users
    stage.name (list): Filters for records in the provided stage(s) by name
    ticket.needs_response (bool): Filters for tickets that need a response
    ticket.rev_org (list): Filters for tickets associated with any of the provided Rev organizations
    ticket.severity (list): Filters for tickets with any of the provided severities. Allowed values: blocker, high, low, medium
    ticket.source_channel (list): Filters for tickets with any of the provided source channels
    type (list): Filters for work of the provided types. Allowed values: issue, ticket, task

Returns:
    list: Matching work items
"""

def summarize_objects(objects):
"""
Summarizes a list of objects. The logic of how to summarize a
particular object type is an internal implementation detail

Parameters:
    objects (list): List of objects to summarize

Returns:
    text: Summarized text of the objects
"""

def prioritize_objects(objects):
"""
Returns a list of objects sorted by priority. The logic of what constitutes
priority for a given object is an internal implementation detail

Parameters:
    objects (list): A list of objects to be prioritized

Returns:
    list: Prioritized objects
"""

def add_work_items_to_sprint(work_ids, sprint_id):
"""
Adds the given work items to the sprint

Parameters:
    work_ids (list): A list of work item IDs to be added to the sprint
    sprint_id (str): The ID of the sprint to which the work items should be added
"""

def get_sprint_id():
"""
Returns the ID of the current sprint
"""

def get_similar_work_items(work_id):
"""
Returns a list of work items that are similar to the given work item

Parameters:
    work_id (str): The ID of the work item for which you want to find similar items

Returns:
    list: Similar work items
"""

def search_object_by_name(query):
"""
Given a search string, returns the ID of a matching object in the system of record.
If multiple matches are found, it returns the one where the confidence is highest

Parameters:
    query (str): The search string, could be for example customer’s name, part name, user name

Returns:
    str: ID of matching object
"""

def create_actionable_tasks_from_text(text):
"""
Given a text, extracts actionable insights, and creates tasks for them,
which are kind of a work item

Parameters:
    text (str): The text from which the actionable insights need to be created

Returns:
    list: tasks created from the given text

"""

def who_am_i():
"""
Returns the string ID of the current user
"""

The only code you know to write is of type "var_name = function_call(function_argument)". You never output anything else other than this format. You follow the sequence of completing query religiously.
Here are some sample queries and their respective responses that I want from you:

Example output:

Queries:
1. Summarize work items similar to don:core:dvrv-us-1:devo/0:issue/1
2. What is the meaning of life?
3. Prioritize my P0 issues and add them to the current sprint
4. Summarize high severity tickets from the customer UltimateCustomer
5. What are my all issues in the triage stage under part FEAT-123? Summarize them.
6. Find similar tasks to TASK-321, summarize and rank them by priority

Answers:

1.
var_1 = get_similar_work_items(work_id="don:core:dvrv-us-1:devo/0:issue/1")
var_2 = summarize_objects(objects=var1)

2.
# Cannot be solved using the given functions

3.
var_1 = who_am_i()
var_2 = works_list(type = ["issue"], issue.priority=["p0"], owned_by=[var_1])
var_3 = prioritize_objects(objects=var_2)
var_4 = get_sprint_id()
var_5 = add_work_items_to_sprint(work_ids=var_3, sprint_id=var_4)

4.
var_1 = search_object_by_name(query="UltimateCustomer")
var_2 = works_list(type = ["ticket"], ticket.rev_org=[var_1])
var_3 = summarize_objects(objects=var_2)

5.
var_1 = who_am_i()
var_2 = works_list(stage.name=["triage"], applies_to_part=["FEAT-123"], owned_by=[var_1], type = ["issue"])
var_3 = summarize_objects(objects=var_2)

6.
var_1 = get_similar_work_items(work_id="TASK-321")
var_2 = summarize_objects(objects=var_1)
var_3 = prioritize_objects(objects=var_1)

The user will prompt you with a list of queries similar to the example. Answer very strictly in the same format shown above. Use indexing for the output. Make sure to mention type wherever relevant when calling works_list. Any missing type arguments is not acceptable.
Don't make unnecessary calls to any functions. When given names make sure to call search_object_by_name() to get work_ids.
'''
    }
    return messages

print(outputMessage())
