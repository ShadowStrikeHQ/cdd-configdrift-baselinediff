#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import json
import yaml
from jsondiffpatch import diff
from jsondiffpatch import configure_make_patch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.

    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    parser = argparse.ArgumentParser(description="Compares current configuration against a known good baseline, highlighting differences.")
    parser.add_argument("baseline", help="Path to the baseline configuration file (JSON or YAML)")
    parser.add_argument("current", help="Path to the current configuration file (JSON or YAML)")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format for the diff (default: json)")
    parser.add_argument("--ignore", nargs="+", help="List of keys to ignore in the diff")
    parser.add_argument("--output", help="Path to the output file for the diff. If not specified, diff is printed to stdout.")
    parser.add_argument("--indent", type=int, default=4, help="Indentation level for JSON/YAML output (default: 4)")
    parser.add_argument("--no-color", action="store_true", help="Disable color output.")

    return parser

def load_config(file_path):
    """
    Loads a configuration file from either JSON or YAML format.

    Args:
        file_path (str): The path to the configuration file.

    Returns:
        dict: The configuration data as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is invalid or the content is not valid JSON/YAML.
    """
    try:
        with open(file_path, 'r') as f:
            if file_path.lower().endswith('.json'):
                return json.load(f)
            elif file_path.lower().endswith(('.yaml', '.yml')):
                return yaml.safe_load(f)
            else:
                raise ValueError("Unsupported file format.  Must be JSON or YAML.")
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {file_path}: {e}")
        raise ValueError(f"Invalid JSON: {e}")
    except yaml.YAMLError as e:
        logging.error(f"Invalid YAML in {file_path}: {e}")
        raise ValueError(f"Invalid YAML: {e}")
    except Exception as e:
        logging.error(f"Error loading {file_path}: {e}")
        raise

def filter_config(config, ignore_keys):
    """
    Filters a configuration by removing specified keys recursively.

    Args:
        config (dict): The configuration dictionary.
        ignore_keys (list): A list of keys to ignore.

    Returns:
        dict: The filtered configuration dictionary.
    """
    if not ignore_keys:
        return config

    def _filter(data, keys):
        if isinstance(data, dict):
            return {k: _filter(v, keys) for k, v in data.items() if k not in keys}
        elif isinstance(data, list):
            return [_filter(item, keys) for item in data]
        else:
            return data

    return _filter(config, ignore_keys)

def compare_configs(baseline, current, ignore_keys=None):
    """
    Compares two configuration dictionaries and returns the diff.

    Args:
        baseline (dict): The baseline configuration.
        current (dict): The current configuration.
        ignore_keys (list): A list of keys to ignore during comparison.

    Returns:
        dict: The diff between the two configurations.
    """
    if ignore_keys:
        baseline = filter_config(baseline, ignore_keys)
        current = filter_config(current, ignore_keys)

    delta = diff(baseline, current)
    return delta

def format_diff(delta, format_type="json", indent=4, no_color=False):
    """
    Formats the diff into a human-readable string.

    Args:
        delta (dict): The diff dictionary.
        format_type (str): The output format ("json" or "yaml").
        indent (int): Indentation level for JSON/YAML output.
        no_color (bool): Whether to disable color output.

    Returns:
        str: The formatted diff string.
    """

    if not delta:
        return "No differences found."

    try:
        if format_type == "json":
            return json.dumps(delta, indent=indent)
        elif format_type == "yaml":
            return yaml.dump(delta, indent=indent, sort_keys=False)
        else:
            raise ValueError("Invalid format type. Must be 'json' or 'yaml'.")
    except Exception as e:
        logging.error(f"Error formatting diff: {e}")
        raise

def write_output(output_path, formatted_diff):
    """
    Writes the formatted diff to a file.

    Args:
        output_path (str): The path to the output file.
        formatted_diff (str): The formatted diff string.
    """
    try:
        with open(output_path, 'w') as f:
            f.write(formatted_diff)
        logging.info(f"Diff written to {output_path}")
    except Exception as e:
        logging.error(f"Error writing to file: {e}")
        raise

def main():
    """
    Main function to parse arguments, load configurations, compare them,
    format the diff, and write it to output.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        # Load configurations
        baseline_config = load_config(args.baseline)
        current_config = load_config(args.current)

        # Compare configurations
        delta = compare_configs(baseline_config, current_config, args.ignore)

        # Format the diff
        formatted_diff = format_diff(delta, args.format, args.indent, args.no_color)

        # Write output
        if args.output:
            write_output(args.output, formatted_diff)
        else:
            print(formatted_diff)

    except FileNotFoundError:
        sys.exit(1)  # Exit with an error code
    except ValueError as e:
        logging.error(e)
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Example usage:
# 1. Create two config files, baseline.json and current.json, with some differences.
# 2. Run the script: python main.py baseline.json current.json --format yaml --ignore secret_key api_key --output diff.yaml
# 3. Or, without output file: python main.py baseline.json current.json