from pydantic import BaseModel,Field,ConfigDict
from typing import Optional

class File(BaseModel):
    path: str = Field(description="The path of the file to be created or modified")
    purpose: str = Field(description="The purpose of the file, e.g. 'To store the main function of the app'")

class Plan(BaseModel):
    name: str = Field(description="The name of the app to be built")
    description: str = Field(description="A one line description of the app to be built, e.g. 'A webapp for managing your tasks'")
    tech_stack: str = Field(description="Technologies used, e.g. 'HTML, CSS, Vanilla JavaScript'")
    features: list[str] = Field(description="A list of features of the app, e.g. ['Add a task', 'View tasks', 'Delete tasks']")
    files: list[File] = Field(description="A list of files to be created, max 4 files, e.g. ['index.html', 'style.css', 'script.js']")

class ImplementationPlan(BaseModel):
    file_path: str = Field(description="The path of the file to be modified")
    task_description: str = Field(description="The description of the task to be implemented")

class TaskPlan(BaseModel):
    implementation_steps:list[ImplementationPlan]=Field(description="A list of implementation steps for the task")
    model_config=ConfigDict(extra="allow") # allows extra fields to be added to the model

class CoderState(BaseModel):
    task_plan:TaskPlan=Field(description="The task plan to be implemented")
    current_step_idx:int=Field(0,description="The index of the current step to be implemented")
    current_file_content:Optional[str]=Field(None,description="The content of the current file to be implemented or modified")