import yaml
import operator

def sort_yaml(input_filename, output_filename):

    try:
        # Load the YAML data
        with open(input_filename, 'r') as file:
            data = yaml.safe_load(file)
        
        if isinstance(data, list):
            data.sort(key=operator.itemgetter('ID'))
            with open(output_filename, 'w') as file:
                yaml.dump(data, file, sort_keys=False, default_flow_style=False)
            
            print(f"Successfully sorted data from '{input_filename}' and saved to '{output_filename}'.")
        else:
            print("Error: The YAML file does not contain a list of items at the top level.")

    except yaml.YAMLError as e:
        print(f"Error processing YAML file: {e}")
    except FileNotFoundError:
        print(f"Error: The file '{input_filename}' was not found.")
    except KeyError as e:
        print(f"Error: Missing key {e} in one of the YAML entries. Cannot sort by 'id'.")


input_filename = 'NUPAQIS.yaml'
output_filename = 'NUPAQIS_copy.yaml'
sort_yaml(input_filename, output_filename)