import requests
from ruamel.yaml import YAML
from pathlib import Path

yaml = YAML()


def read_spec_from_quarto(branch="main"):
    url = f"https://github.com/quarto-dev/quarto-cli/raw/{branch}/src/resources/schema/definitions.yml"
    return yaml.load(requests.get(url).content)


def filter_spec_brand(spec: list[dict[str, object]]):
    brand = [item for item in spec if "id" in item and item["id"].startswith("brand")]
    brand.sort(key=lambda item: item["id"])
    return brand


def write_brand_spec(brand: list[dict[str, object]]):
    path = Path(__file__).parent / "brand.spec.yml"
    with path.open("w") as f:
        yaml.dump(brand, f)


def read_brand_spec():
    path = Path(__file__).parent / "brand.spec.yml"
    with path.open("r") as f:
        return yaml.load(f)


if __name__ == "__main__":
    print("Running the thing now!")
    spec = read_spec_from_quarto()
    brand = filter_spec_brand(spec)
    write_brand_spec(brand)
