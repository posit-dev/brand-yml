# Brand YAML


``` python
from brand_yml import Brand

brand = Brand(
    meta = {"name": "Posit PBC", "link": "https://posit.co"}
)

brand.meta
```

    BrandMeta(name=BrandMetaName(full='Posit PBC'), link=BrandMetaLink(home=Url('https://posit.co/')))

## Installation

### From PyPI

``` bash
uv pip install brand_yml
```

### From GitHub

``` bash
uv pip install "git+https://github.com/posit-dev/brand-yml#subdirectory=pkg-py"
```
