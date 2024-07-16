import requests
import json
from datetime import datetime
from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv
import os
from utils.calls import extract_todoist_param


dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')  
load_dotenv(dotenv_path)

todoist_api_client=TodoistAPI(os.getenv('TODOIST_API'))

class todo_ist:
    def __init__(self):
        self.base_url = "https://api.todoist.com/rest/v2/"

    def create_task(self, content, due_string=None, due_date=None, project_id=None, priority=None):
        
        data = {
            "content": content
        }
        if due_string:
            data["due_string"] = due_string
        if due_date:
            data["due_date"] = due_date
        if project_id:
            data["project_id"] = project_id
        if priority:
            data["priority"] = priority

        
        try:
            task = todoist_api_client.add_task(**data)
            return f"Success Task added successfully for {content}"
        except Exception as error:
            return "failed to add the given task"
            
            
    def get_tasks(self):
       
        try:
            projects = todoist_api_client.get_tasks()
            return projects
        except Exception as error:
            return None

    def get_task(self, task_title):
        tasks = self.get_tasks()
        if tasks is None:
            return None
        for task in tasks:
            if task.content == task_title:
                return task
        return None


    def update_task(self, task_title, content=None, due_string=None, due_date=None, priority=None):
        task = self.get_task(task_title)
        if task is None:
            return {"task not found"}
        task_id = task.id
        data = {}
        if content:
            data["content"] = content
        if due_string:
            data["due_string"] = due_string
        if due_date:
            data["due_date"] = due_date
        if priority:
            data["priority"] = priority
        data['task_id']=task_id
        response = todoist_api_client.update_task(**data)
        if response:
            return {"success":"task updated successfully"}
        else:
            return {"error": "Failed to update the task"}
        
        
    def delete_task(self, task_title):
        task = self.get_task(task_title)
        if task is None:
            return {"task not found "}
        task_id = task.id
        response = todoist_api_client.delete_task(task_id=task_id)
        if response:
            print("task deleted")
            return {"success": "Task deleted successfully"}
        else:
            return {"error": "Failed to delete task"}

    def get_urgent_tasks(self):
        tasks = self.get_tasks()
        if "error" in tasks:
            return tasks

        urgent_tasks = [task for task in tasks if task.due is not None]

        # Convert due date strings to datetime objects for sorting
        for task in urgent_tasks:
            task.due=datetime.fromisoformat(task.due.date)
        # Sort tasks by due date and time
        urgent_tasks.sort(key=lambda x: x.due)

        return urgent_tasks
    
    

# process the task requests

def process_task_request(prompt, groq_client):
    # Extract parameters
    todoist_params = extract_todoist_param(prompt, groq_client)
    
    # Initialize Todoist API
    todoist = todo_ist()
    
    # Process the request
    function = todoist_params['function']
    parameters = todoist_params['parameters']
    
    if function == "create_task":
        content = parameters.get("content")
        due_string = parameters.get("due_string")
        due_date = parameters.get("due_date")
        project_id = parameters.get("project_id")
        priority = parameters.get("priority")
        result = todoist.create_task(content, due_string, due_date, project_id, priority)
    
    elif function == "get_tasks":
        result = todoist.get_tasks()
        ref_result=[]
        for res in result:
            ref_result.append(res.content)
        
        return ref_result
    
    elif function == "get_task":
        task_title = parameters.get("task_title")
        result = todoist.get_task(task_title)
    
    elif function == "update_task":
        task_title = parameters.get("task_title")
        content = parameters.get("content")
        due_string = parameters.get("due_string")
        due_date = parameters.get("due_date")
        priority = parameters.get("priority")
        result = todoist.update_task(task_title, content, due_string, due_date, priority)
    
    elif function == "delete_task":
        task_title = parameters.get("task_title")
        result = todoist.delete_task(task_title)

    elif function == "get_urgent_tasks":
        result = todoist.get_urgent_tasks()
        ref_result=[]
        for res in result:
            ref_result.append(res.content)
            
        return ref_result
    
    else:
        result = {"error": "Invalid function"}
    
    return result