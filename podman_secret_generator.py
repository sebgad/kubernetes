import yaml
import base64
import os
import logging
import pathlib
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def base64_encode(value: str) -> str:
    return base64.b64encode(value.encode('utf-8')).decode('utf-8')

def update_k8s_secret(file_path: str, output_path: str):
    if not os.path.exists(file_path):
        logger.error(f"File {file_path} does not exist.")
        return

    try:
        with open(file_path, 'r') as f:
            secret = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load YAML: {e}")
        return

    if 'data' not in secret:
        logger.warning("The YAML does not contain a 'data' section.")
        return

    logger.info("Current keys in 'data':")
    for key in secret['data']:
        logger.info(f" - {key}")

    logger.info("Enter new values for keys (leave blank to keep current value):")
    for key in secret['data']:
        user_input = input(f"{key}: ").strip()
        if user_input:
            encoded_value = base64_encode(user_input)
            secret['data'][key] = encoded_value
            logger.debug(f"Updated '{key}' with base64 encoded value.")

    try:
        with open(output_path, 'w') as f:
            yaml.safe_dump(secret, f, default_flow_style=False)
        logger.info(f"Updated secret written to: {output_path}")
    except Exception as e:
        logger.error(f"Failed to write updated YAML: {e}")

if __name__ == "__main__":
    input_file = input("Enter path to Kubernetes secret YAML: (leave blank to iterate over all templates)").strip()
    if not input_file:
        input_files = pathlib.Path(__file__).parent.glob("**/secret*.template")
        for input_file in input_files:
            answer = input(f"Do you want to run secret generation for {input_file}? [y/Any]").strip()
            if answer == "y":
                output_file = input_file.parent / f"{input_file.stem}.yaml"
                update_k8s_secret(input_file, output_file)

                answer = input("Do you want to run the generated secret? [y/Any]").strip()
                if answer == "y":
                    subprocess.run(["podman", "kube", "play", output_file])
		answer = input("Do you want to delete the generated secret file? [y/Any]").strip()
		if answer == "y":
		    subprocess.run(["rm", output_file])
    else:
        output_file = input("Enter path for updated YAML output: ").strip()
