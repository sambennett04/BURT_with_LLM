import re


def _build_screen_id_maps(graph_path):
    """
    Helper function to create sorted screen ID mappings by processing the file once.
    This ensures S1, S2, S3... are assigned based on sorted hash values.
    """
    unique_screen_hashes = {}

    with open(graph_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # Collect hashes from transitions
        if re.match(r'^[a-f0-9]{64}:', line) and "(s:" in line and ",t:" in line:
            s_match = re.search(r'\(s:\s*([a-f0-9]+)\s*,\s*t:\s*([a-f0-9]+)\s*\)', line)
            if s_match:
                source_hash = s_match.group(1)
                target_hash = s_match.group(2)
                if source_hash not in unique_screen_hashes:
                    unique_screen_hashes[source_hash] = None  # Placeholder for name
                if target_hash not in unique_screen_hashes:
                    unique_screen_hashes[target_hash] = None  # Placeholder for name

        # Collect hashes and names from states
        elif re.match(r'^[a-f0-9]{64},', line):
            screen_hash = re.match(r'^[a-f0-9]{64}', line).group(0)
            name_match = re.search(r'^[a-f0-9]{64},\s*([^,]+),', line)
            screen_name = "Unknown Screen"  # Default
            if name_match:
                screen_name = name_match.group(1).strip()
            unique_screen_hashes[screen_hash] = screen_name

    # Sort hashes and assign sequential S IDs
    sorted_screen_hashes = sorted(unique_screen_hashes.keys())
    screen_id_map = {}
    reverse_screen_id_map = {}
    screen_counter = 1
    for screen_hash in sorted_screen_hashes:
        sid = f"S{screen_counter}"
        reverse_screen_id_map[screen_hash] = sid
        screen_id_map[sid] = screen_hash
        screen_counter += 1

    return screen_id_map, reverse_screen_id_map, unique_screen_hashes


def get_transitions(graph_path):
    screen_id_map, reverse_screen_id_map, _ = _build_screen_id_maps(graph_path)

    transition_id_map = {}
    reverse_transition_id_map = {}
    simplified_transitions = []
    transition_counter = 1

    with open(graph_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    inside_transition_block = False
    for line in lines:
        line = line.strip()
        if line.startswith("Transitions"):
            inside_transition_block = True
            continue
        if line.startswith("States"):
            break

        if inside_transition_block and re.match(r'^[a-f0-9]{64}:', line):
            parts = line.split(":", 1)
            if len(parts) != 2:
                continue

            transition_hash = parts[0].strip()

            s_match = re.search(r'\(s:\s*([a-f0-9]+)\s*,\s*t:\s*([a-f0-9]+)\s*\)', parts[1])
            if not s_match:
                continue

            source_hash = s_match.group(1)
            target_hash = s_match.group(2)

            if transition_hash not in reverse_transition_id_map:
                tid = f"T{transition_counter}"
                reverse_transition_id_map[transition_hash] = tid
                transition_id_map[tid] = transition_hash
                transition_counter += 1

            # Use already assigned sorted S IDs
            simplified_source_id = reverse_screen_id_map.get(source_hash, source_hash)
            simplified_target_id = reverse_screen_id_map.get(target_hash, target_hash)

            remaining = re.sub(r'^[a-f0-9]{64}:\s*\(s:\s*[a-f0-9]+\s*,\s*t:\s*[a-f0-9]+\s*\):', '', line).strip()
            new_line = f"{reverse_transition_id_map[transition_hash]}: (s:{simplified_source_id},t:{simplified_target_id}): {remaining}"
            simplified_transitions.append(new_line)

    return simplified_transitions, transition_id_map, reverse_transition_id_map, screen_id_map, reverse_screen_id_map


def clean_transitions(transitions_list):
    """
    Cleans a list of transition strings by removing all information
    starting from the "weight=" keyword to the end of the string.

    Args:
        transitions_list (list): A list of transition strings, typically
                                 in the format "T#: (s:S#,t:S#): [...] weight=...".

    Returns:
        list: A new list of cleaned transition strings.
    """
    cleaned_list = []
    # Regex to match ' weight=' and everything that follows it (non-greedy .*?)
    # and then greedy .* to match till the end of the line.
    # The '?' after .* makes the matching non-greedy for the text before 'weight=',
    # ensuring we cut exactly from the *first* occurrence of ' weight='.
    # Actually, a simpler regex `r' weight=.*'` should work perfectly because we want
    # to remove everything *after* ' weight='.
    pattern = re.compile(r'\s*weight=.*')

    for transition_str in transitions_list:
        # Substitute the matched pattern with an empty string
        cleaned_str = pattern.sub('', transition_str)
        cleaned_list.append(cleaned_str.strip()) # .strip() to remove any leftover whitespace

    return cleaned_list


def get_screens(graph_path):
    screen_id_map, reverse_screen_id_map, unique_screen_hashes = _build_screen_id_maps(graph_path)

    screen_names_output = []

    # Create a list of (numerical_id, formatted_string) for sorting
    for screen_hash, screen_name_from_states in unique_screen_hashes.items():
        simplified_id = reverse_screen_id_map.get(screen_hash)
        if simplified_id:
            # Use the name found in the states block, or fallback if not found
            display_name = screen_name_from_states if screen_name_from_states is not None else "Unknown Screen"
            screen_names_output.append((int(simplified_id[1:]), f"{simplified_id}: {display_name}"))

    # Sort by the numerical part of the simplified ID (S1, S2, S3...)
    screen_names_output.sort(key=lambda x: x[0])

    return "\n".join([item[1] for item in screen_names_output])


def get_original_transition_ids(response_text, transition_id_map):
    """
    Replaces all <T#> with actual transition hashes using the provided map.

    Args:
        response_text (str): The response text containing <T#> placeholders.
        transition_id_map (dict): Mapping from simple IDs (e.g., 'T1') to hash values.

    Returns:
        str: Modified response with hash values instead of simplified IDs.
    """

    def replacer(match):
        tid = match.group(1)
        return f"<{transition_id_map.get(tid, tid)}>"  # fallback to original if not found

    pattern = r"<(T\d+)>"
    return re.sub(pattern, replacer, response_text)


def get_extracted_transitions(simplified_transitions):
    """
    Parses a list of simplified transition strings and extracts important information,
    formatting it into a cleaner, more readable representation.

    Args:
        simplified_transitions (list): A list of strings, where each string is
                                       a simplified transition in the format:
                                       "T_id: (s:S_id,t:S_id): [id=..., act=(...) click, cp=[...], ...]"

    Returns:
        list: A list of newly formatted strings with extracted details.
              Example: "T3: (s:S3,t:S4): Action = click; Component = [Type = Button, Identifier = permission_allow_button, Text = Allow, Description = ""]"
    """
    formatted_transitions = []

    for transition_str in simplified_transitions:
        # 1. Extract the initial part: T_id: (s:S_id,t:S_id):
        # This regex captures the 'T#: (s:S#,t:S#):' part and the rest of the string
        header_match = re.match(r'^(T\d+:\s*\(s:S\d+,t:S\d+\)):(.*)', transition_str)
        if not header_match:
            # Skip lines that don't match the expected header format
            continue

        header_part = header_match.group(1).strip()
        details_part = header_match.group(2).strip()  # The part after the header

        # Initialize extracted values with blank strings for attributes that might be missing
        action = ""
        comp_type = ""
        comp_identifier = ""
        comp_text = ""
        comp_description = ""

        # 2. Extract Action (act)
        # Looks for 'act=(digit) ' followed by the action text (non-greedy, stopping at comma or end)
        action_match = re.search(r'act=\(\d+\)\s*([^,\]]+)', details_part)
        if action_match:
            action = action_match.group(1).strip()

        # 3. Extract Component (cp) and its sub-attributes
        # First, find the 'cp=' part. It can be 'cp=null' or 'cp=[...]'
        component_value_match = re.search(r'cp=(null|\[.*?\])', details_part)

        component_details_string = ""
        if component_value_match:
            raw_cp_value = component_value_match.group(1)
            if raw_cp_value.startswith('['):
                # If it's a bracketed component, remove the outer brackets
                component_details_string = raw_cp_value[1:-1].strip()
            # If raw_cp_value is 'null', component_details_string remains empty, which is desired

        if component_details_string:
            # Now parse the content within the component_details_string for specific attributes

            # Type (ty)
            type_match = re.search(r'ty=([^,\]]+)', component_details_string)
            if type_match:
                comp_type = type_match.group(1).strip()

            # Identifier (idx)
            identifier_match = re.search(r'idx=([^,\]]+)', component_details_string)
            if identifier_match:
                comp_identifier = identifier_match.group(1).strip()

            # Text (tx) - often within the component payload
            text_match = re.search(r'tx=([^,\]]+)', component_details_string)
            if text_match:
                comp_text = text_match.group(1).strip()

            # Description (dsc) - often at the end, so it might not be followed by a comma
            # Using [^\]]* to allow empty description and match till the end of the component string
            description_match = re.search(r'dsc=([^\]]*)', component_details_string)
            if description_match:
                comp_description = description_match.group(1).strip()

        # 4. Format the extracted information into the desired output string
        formatted_line = (
            f"{header_part}: Action = \"{action}\"; "
            f"Component = [Type = \"{comp_type}\", Identifier = \"{comp_identifier}\", "
            f"Text = \"{comp_text}\", Description = \"{comp_description}\"]"
        )
        formatted_transitions.append(formatted_line)

    return formatted_transitions