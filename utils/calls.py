import json


def function_call(prompt,groq_client):
    
    sys_msg=("""
        You are an AI function calling model. You will determine whether extracting the user's clipboard
        content, taking a screenshot, capturing the webcam, checking the weather, checking the news, or calling no functions is best for a voice
        assistant to respond to the user's prompt. The webcam can be assumed to be a normal laptop webcam
        facing the user. If the best response involves checking the weather or news, also include the required parameters like time and place. 
        You will respond with a JSON object containing the function name and parameters.
        The available functions are: ["extract clipboard", "take screenshot","play song", "capture webcam", "check weather", "check news","manage tasks", "check mails", "None"].
        Format your response as follows:
        {
            "function": "function_name",
            "parameters": {
                "time": "optional_time",
                "location": "optional_location"
            }
        }
        If no parameters are needed, return an empty parameters object with function=None.

        Examples:
        User: What's the weather like in New York tomorrow?
        Response: {
            "function": "check weather",
            "parameters": {
                "time": "tomorrow",
                "location": "New York"
            }
        }

        User: Show me the latest news.
        Response: {
            "function": "check news",
            "parameters": {}
        }

        User: Can you take a screenshot?
        Response: {
            "function": "take screenshot",
            "parameters": {}
        }

        User: Play Shape of you by Ed Sheeran.
        Response: {
            "function": "play song",
            "parameters": {
                "song":Shape of you Ed Sheeran
            }
        }
        
        User: Please capture a photo.
        Response: {
            "function": "capture webcam",
            "parameters": {}
        }
        User: What do I have in my clipboard?
        Response: {
            "function": "extract clipboard",
            "parameters": {}
        }
        
        User: What tasks do I have for today?.
        Response: {
            "function": "manage task",
            "parameters": {
            }
        }
        User: Get my recent two emails.
        Response: {
            "function": "check mails",
            "parameters": {
                "n":2
            }
        }
        User: Delete the task with title 'Buy Groceries'.
        Response: {
            "function": "manage task",
            "parameters": {
            }
        }
        User: Hello, how are you?
        Response: {
            "function": "None",
            "parameters": {}
        }
    """)
    
    function_convo=[{'role':'system','content':sys_msg},
                    {'role':'user','content':prompt}]
    
    chat_completion=groq_client.chat.completions.create(messages=function_convo,model='llama3-70b-8192')
    
    
    response=chat_completion.choices[0].message.content

    return json.loads(response)

def extract_news_param(prompt,groq_client):

    sys_msg = """
        You are an AI function calling model. You will determine the best way to check the news based on the user's prompt.
    The available functions are: ["check news"].
    You will only repond with a JSON object.
    Format your response as follows:
    {
        "function": "check news",
        "parameters": {
            "country": "optional_country_code",
            "category": "optional_category",
            "sources": "optional_sources",
            "query": "optional_query_terms",
            "pageSize": "optional_page_size",
            "page": "optional_page"
        }
    }
    If no parameters are needed, return an empty parameters object.
    Examples:
    User: What's the latest business news in the US?
    Response: {
        "function": "check news",
        "parameters": {
            "country": "us",
            "category": "business"
        }
    }

    User: Show me the top headlines from BBC News.
    Response: {
        "function": "check news",
        "parameters": {
            "sources": "bbc-news"
        }
    }

    User: What's happening in technology today?
    Response: {
        "function": "check news",
        "parameters": {
            "category": "technology"
        }
    }
    """
    
    function_convo2 = [{'role': 'system', 'content': sys_msg},
                      {'role': 'user', 'content': prompt}]
    
   
    chat_completion2 = groq_client.chat.completions.create(messages=function_convo2, model='llama3-70b-8192')
    
    
    response2 = chat_completion2.choices[0].message.content.strip()
    
    return json.loads(response2)


def extract_todoist_param(prompt, groq_client):
    sys_msg = """
    You are an AI function calling model. You will determine the best way to interact with the Todoist API based on the user's prompt.
    The available functions are: ["create_task", "get_tasks", "get_task", "update_task", "delete_task", "get_urgent_tasks"].
    You will only respond with a JSON object.
    Format your response as follows:
    {
        "function": "function_name",
        "parameters": {
            "content": "optional_content",
            "due_string": "optional_due_string",
            "due_date": "optional_due_date",
            "project_id": "optional_project_id",
            "priority": "optional_priority",
            "task_title": "optional_task_title",
            "pageSize": "optional_page_size",
            "page": "optional_page"
        }
    }
    If no parameters are needed, return an empty parameters object.
    Examples:
    User: Create a new task to buy groceries tomorrow with priority 1.
    Response: {
        "function": "create_task",
        "parameters": {
            "content": "buy groceries",
            "due_string": "tomorrow",
            "priority": 1
        }
    }

    User: Show me all my tasks.
    Response: {
        "function": "get_tasks",
        "parameters": {}
    }

    User: Get the details of the task with title 'Buy Groceries'.
    Response: {
        "function": "get_task",
        "parameters": {
            "task_title": "Buy Groceries"
        }
    }

    User: Update the task with title 'Buy Groceries' to 'Buy groceries and cook dinner' with priority 2.
    Response: {
        "function": "update_task",
        "parameters": {
            "task_title": "Buy Groceries",
            "content": "Buy groceries and cook dinner",
            "priority": 2
        }
    }

    User: Delete the task with title 'Buy Groceries'.
    Response: {
        "function": "delete_task",
        "parameters": {
            "task_title": "Buy Groceries"
        }
    }

    User: Show me the most urgent tasks.
    Response: {
        "function": "get_urgent_tasks",
        "parameters": {}
    }
    """
    
    function_convo = [{'role': 'system', 'content': sys_msg},
                      {'role': 'user', 'content': prompt}]
    
    chat_completion = groq_client.chat.completions.create(messages=function_convo, model='llama3-70b-8192')
    
    response = chat_completion.choices[0].message.content.strip()
    
    return json.loads(response)