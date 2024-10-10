from __future__ import annotations

import json

from pydantic import BaseModel, RootModel
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO


class BrandYaml(YAML):
    """
    A custom yaml class that allows dumping to a string instead of a file.
    """

    # https://yaml.readthedocs.io/en/latest/example/#output-of-dump-as-a-string

    def dump(self, data, stream=None, **kw):
        if isinstance(data, (BaseModel, RootModel)):
            # Dump to JSON first to have Pydantic handle casting to JSON formats,
            # otherwise `ruamel.yaml` will raise errors for classes it doesn't know
            # how to serialize.
            data_json = data.model_dump_json(
                exclude_defaults=True,
                exclude_none=True,
            )
            data = json.loads(data_json)

        to_string = stream is None

        if to_string:
            stream = StringIO()

        YAML.dump(self, data, stream, **kw)

        if to_string:
            return stream.getvalue()


yaml_brand = BrandYaml()
