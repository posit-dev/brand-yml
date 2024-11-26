from pathlib import Path

import requests
from ruamel.yaml import YAML

yaml = YAML()


def gh_quarto_cli_raw_url(branch="main"):
    return f"https://github.com/quarto-dev/quarto-cli/raw/{branch}"


def read_yaml_from_quarto(branch="v1.6.37"):
    url = (
        gh_quarto_cli_raw_url(branch) + "/src/resources/schema/definitions.yml"
    )
    return yaml.load(requests.get(url).content)


def find_all_refs_recursively(obj: dict[str, object]):
    refs = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "ref":
                refs.add(value)
            else:
                refs |= find_all_refs_recursively(value)
    elif isinstance(obj, list):
        for item in obj:
            refs |= find_all_refs_recursively(item)
    return refs


def filter_schema_brand(schema: list[dict[str, object]]):
    brand = [
        item
        for item in schema
        if "id" in item and item["id"].startswith("brand")
    ]

    # Make sure we've gotten all the references in the set of brand definitions
    refs = find_all_refs_recursively(brand)
    extras = refs - {item["id"] for item in brand}
    if len(extras) > 0:
        print(f"Including extra definitions: {', '.join(extras)}")
        brand.extend([item for item in schema if item["id"] in extras])

    brand.sort(key=lambda item: item["id"])
    return brand


def write_brand_schema(brand: list[dict[str, object]]):
    path = Path(__file__).parent / "brand.schema.yml"
    with path.open("w") as f:
        yaml.dump(brand, f)


def read_brand_schema():
    path = Path(__file__).parent / "brand.schema.yml"
    with path.open("r") as f:
        return yaml.load(f)


if __name__ == "__main__":
    schema = read_yaml_from_quarto()
    brand = filter_schema_brand(schema)
    write_brand_schema(brand)
