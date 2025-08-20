import openai
import os
from dotenv import load_dotenv
import tiktoken
from utils import *

def generateReport(app_select, user_description, chat_model, max_completion_tokens):

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt_template = """
    **Android Bug Report Generator**

    You are an automated bug report generator for Android applications.

    Given a user-provided description of a bug and a set of application transitions with the action and component information, your task is to generate a complete and structured bug report. The action of each transitions represents an GUI interaction (e.g.,  tap, swipe, long tap, etc.) that a user can perform on the GUI component of an app screen.

    The report should include the following sections:

    - **Title**  
    - **Observed Behavior**  
    - **Expected Behavior**  
    - **Steps to Reproduce**  

    **Bug Description:**  
    "{user_input}"

    **Application Transitions (Graph Context):**  
    {transitions}

    **Instructions for Generating Steps to Reproduce:**

    1. Begin the steps by opening the application.  
    2. Assume this is the first time the app is being opened (fresh install).  
    3. Each step must describe one **specific user interaction** (e.g., tap, swipe, long tap, etc.).  
    4. Only include interactions that have a corresponding **transition** in the graph graph_data.  
    5. Each transition includes:
    - A **source screen (s)** — where the interaction starts.  
    - A **target screen (t)** — the result of the interaction.  
    6. The steps must form a **valid and complete path** in the transition graph, starting from the initial screen and ending at the screen where the bug occurs.  
    7. The **target screen** of one step must be the **source screen** of the next.  
    8. Use natural language to describe each step, referencing the interaction and screen information from the transition graph_data.  
    9. Append the **transition ID** to the end of each step in this format: `<transition_id>`.  
    10. **Do not include** any steps that are not interactions or are not backed by a valid transition (e.g., "observe the error").  

    Follow these instructions strictly to ensure accuracy and consistency in the generated report.
    """

    app_folder_name = app_select.replace(" ", "_") + "/"

    #TODO: make local graph data folder to upload to personal repo
    data_folder_path = 'graph_data_example/'

    print(f"Generating for App: {app_select}")
    print("========================")

    #construct graph folder path
    bug_folder_path = os.path.join(data_folder_path, app_folder_name)
    
    graph_folder_name = [name for name in os.listdir(bug_folder_path)
                         if os.path.isdir(os.path.join(bug_folder_path, name))][0]
    graph_folder_path = os.path.join(bug_folder_path, graph_folder_name)
    graph_file_name = [f for f in os.listdir(graph_folder_path) if
                       f.endswith('graph.txt') and os.path.isfile(os.path.join(graph_folder_path, f))][0]
    graph_file_path = os.path.join(graph_folder_path, graph_file_name)
    # print(f'Bug{bug_id}: {graph_file_path}')

    transitions, transition_id_map, screen_id_map, reverse_transition_id_map, reverse_screen_id_map = get_transitions(
        graph_file_path)
    
    transition_lines = "\n".join(transitions)
    # print(transition_lines)

    extracted_transitions = get_extracted_transitions(transitions)
    #extracted_transition_lines = "\n".join(extracted_transitions)
    # print(extracted_transition_lines)

    screens = get_screens(graph_file_path)
    
    prompt = prompt_template.replace('{user_input}', user_description).replace('{transitions}', transition_lines)

    # === Send to GPT-o4-mini and print response ===
    response = client.chat.completions.create(
        model=chat_model,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=max_completion_tokens,
    )

    response_text = response.choices[0].message.content

    response_text = get_original_transition_ids(response_text, transition_id_map)
    return response_text