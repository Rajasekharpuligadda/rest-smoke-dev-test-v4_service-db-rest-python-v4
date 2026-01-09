import yaml
import argparse
from pathlib import Path

from app.logger import logger


def process_dependencies(features: list[str], config_path: str, output_path: str):
    """
    Generates a requirements.txt file based on specified features.

    Args:
        features: A list of features to include (e.g., ['api', 'postgresql']).
        config_path: Path to the YAML dependency configuration file.
        output_path: Path to write the generated requirements.txt file.
    """
    logger.info(f"Loading dependency configuration from: {config_path}")
    with open(config_path, "r") as f:
        config: dict = yaml.safe_load(f)

    mappings = config.get("dependencies-mappings", {})
    definitions = config.get("dependencies-definition", {})

    required_deps_keys = set()
    logger.info(f"Processing requested features: {features}")

    for feature in features:
        if feature in mappings:
            deps = mappings[feature]
            logger.info(f"Feature '{feature}' requires dependencies: {deps}")
            required_deps_keys.update(deps)
        else:
            logger.warning(f"Feature '{feature}' not found in mappings. Skipping.")

    requirements_list = []
    logger.info(f"\nResolving package versions for: {sorted(list(required_deps_keys))}")
    for key in sorted(required_deps_keys):
        if key in definitions:
            dep_info: dict = definitions[key]
            package = dep_info.get("package")
            version = dep_info.get("version")

            if not package:
                logger.warning(
                    f"'package' not defined for dependency key '{key}'. Skipping."
                )
                continue

            requirement_line = f"{package}=={version}" if version else package
            requirements_list.append(requirement_line)
            logger.info(f"Added '{requirement_line}'")
        else:
            logger.warning(
                f"Dependency key '{key}' not found in definitions. Skipping."
            )

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        for req in requirements_list:
            f.write(f"{req}\n")

    logger.info(
        f"\nSuccessfully generated '{output_file}' with {len(requirements_list)} packages."
    )


# For direct usage, if needed
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a requirements.txt file for a Python microservice."
    )
    parser.add_argument(
        "--features",
        nargs="+",
        required=True,
        help="A list of features to include (e.g., api postgresql).",
    )
    parser.add_argument(
        "--config",
        default="dependencies-config.yml",
        help="Path to the dependency configuration YAML file.",
    )
    parser.add_argument(
        "--output",
        default="../requirements.txt",
        help="Path for the output requirements.txt file.",
    )
    args = parser.parse_args()

    process_dependencies(
        features=args.features, config_path=args.config, output_path=args.output
    )
