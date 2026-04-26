import json
import os
import random
import string

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_test_cases(module_file):
    print(f"--- AI Test Case Generator started for: {module_file} ---")
    
    with open(module_file, 'r') as f:
        module = json.load(f)
        
    module_name = module.get("moduleName", "Unknown Module")
    fields = module.get("fields", [])
    
    test_cases = []
    
    # 1. Valid Test Case (Happy Path)
    valid_tc = {"type": "Valid (Happy Path)", "inputs": {}}
    for field in fields:
        # Generate valid data based on constraints
        min_l = field.get("minLength", 5)
        valid_tc["inputs"][field["name"]] = generate_random_string(min_l + 2)
    test_cases.append(valid_tc)
    
    # 2. Invalid Test Cases (Missing Required Fields)
    for field in fields:
        if field.get("required"):
            invalid_tc = {"type": f"Invalid (Missing {field['name']})", "inputs": {}}
            for other_field in fields:
                if other_field["name"] == field["name"]:
                    invalid_tc["inputs"][other_field["name"]] = "" # Empty
                else:
                    invalid_tc["inputs"][other_field["name"]] = generate_random_string(8)
            test_cases.append(invalid_tc)
            
    # 3. Edge Cases (Boundary Values)
    for field in fields:
        # Below min length
        if "minLength" in field:
            edge_tc = {"type": f"Edge Case (Below minLength for {field['name']})", "inputs": {}}
            for f in fields:
                if f["name"] == field["name"]:
                    edge_tc["inputs"][f["name"]] = generate_random_string(field["minLength"] - 1)
                else:
                    edge_tc["inputs"][f["name"]] = generate_random_string(8)
            test_cases.append(edge_tc)
            
        # Above max length
        if "maxLength" in field:
            edge_tc = {"type": f"Edge Case (Above maxLength for {field['name']})", "inputs": {}}
            for f in fields:
                if f["name"] == field["name"]:
                    edge_tc["inputs"][f["name"]] = generate_random_string(field["maxLength"] + 1)
                else:
                    edge_tc["inputs"][f["name"]] = generate_random_string(8)
            test_cases.append(edge_tc)
            
    # Output results
    output_file = f"{module_name.replace(' ', '_').lower()}_test_cases.json"
    with open(output_file, 'w') as f:
        json.dump(test_cases, f, indent=4)
        
    print(f"Generated {len(test_cases)} test cases for '{module_name}'.")
    print(f"Saved to {output_file}")
    
    # Also print to console for viva demonstration
    for idx, tc in enumerate(test_cases, 1):
        print(f"\nTest Case {idx}: {tc['type']}")
        print(f"Inputs: {tc['inputs']}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_json = os.path.join(current_dir, "login_module.json")
    
    if os.path.exists(input_json):
        generate_test_cases(input_json)
    else:
        print(f"Input file not found: {input_json}")
