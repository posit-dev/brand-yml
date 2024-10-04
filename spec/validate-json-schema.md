

``` python
import json
from pathlib import Path

import jsonschema
from jsonschema import Draft202012Validator

quarto_local_path = Path("~/work/quarto-dev/quarto-cli")
schema_path = quarto_local_path.expanduser().joinpath("src/resources/schema/json-schemas.json")

if not schema_path.exists():
    raise FileNotFoundError(f"Path {schema_path} does not exist")

with open(schema_path, 'r') as schema_file:
    schema = json.load(schema_file)
```

``` python
def validate_json_schema(schema):
    try:
        Draft202012Validator.check_schema(schema)
        print("Schema is valid according to JSON Schema 2020-12 specification.")
    except jsonschema.exceptions.SchemaError as e:
        print(f"Schema is invalid: {e}")
```

``` python
validate_json_schema(schema)
```

    Schema is invalid: {'values': [None], 'hidden': True} is not of type 'array'

    Failed validating 'type' in metaschema['allOf'][0]['properties']['$defs']['additionalProperties']['$dynamicRef']['allOf'][1]['properties']['anyOf']['items']['$dynamicRef']['allOf'][3]['properties']['enum']:
        {'type': 'array', 'items': True}

    On schema['$defs']['PandocFormatOutputFile']['anyOf'][1]['enum']:
        {'values': [None], 'hidden': True}

``` python
schema["$defs"] = {k: v for k, v in schema["$defs"].items() if k.startswith("Brand")}
# not required but useful for brand-yaml work
# schema["type"] = "object"
# schema["properties"] = {"brand": {"$ref": "#/$defs/Brand"}}
schema["$ref"] = "#/$defs/Brand"

validate_json_schema(schema)
```

    Schema is valid according to JSON Schema 2020-12 specification.

<details>
<summary>
<code>brand-schema.json</code>
</summary>

``` python
import json
from pathlib import Path

with Path(".").joinpath("brand.schema.json").open("w") as f:
    f.write(json.dumps(schema, indent=2))

print(json.dumps(schema, indent=2))
```

    {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "$defs": {
        "BrandMeta": {
          "object": {
            "properties": {
              "name": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "object": {
                      "properties": {
                        "full": {
                          "type": "string"
                        },
                        "short": {
                          "type": "string"
                        }
                      }
                    }
                  }
                ]
              },
              "link": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "object": {
                      "properties": {
                        "home": {
                          "type": "string"
                        },
                        "mastodon": {
                          "type": "string"
                        },
                        "github": {
                          "type": "string"
                        },
                        "linkedin": {
                          "type": "string"
                        },
                        "twitter": {
                          "type": "string"
                        },
                        "facebook": {
                          "type": "string"
                        }
                      }
                    }
                  }
                ]
              }
            }
          }
        },
        "BrandStringLightDark": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "object": {
                "properties": {
                  "light": {
                    "type": "string"
                  },
                  "dark": {
                    "type": "string"
                  }
                }
              }
            }
          ]
        },
        "BrandLogo": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "object": {
                "properties": {
                  "with": {
                    "object": {
                      "properties": {}
                    }
                  },
                  "small": {
                    "$ref": "#/$defs/BrandStringLightDark"
                  },
                  "medium": {
                    "$ref": "#/$defs/BrandStringLightDark"
                  },
                  "large": {
                    "$ref": "#/$defs/BrandStringLightDark"
                  }
                }
              }
            }
          ]
        },
        "BrandColorValue": {
          "type": "string"
        },
        "BrandColor": {
          "object": {
            "properties": {
              "with": {
                "object": {
                  "properties": {}
                }
              },
              "foreground": {
                "$ref": "#/$defs/BrandColorValue"
              },
              "background": {
                "$ref": "#/$defs/BrandColorValue"
              },
              "primary": {
                "$ref": "#/$defs/BrandColorValue"
              },
              "secondary": {
                "$ref": "#/$defs/BrandColorValue"
              },
              "tertiary": {
                "$ref": "#/$defs/BrandColorValue"
              },
              "success": {
                "$ref": "#/$defs/BrandColorValue"
              },
              "info": {
                "$ref": "#/$defs/BrandColorValue"
              },
              "warning": {
                "$ref": "#/$defs/BrandColorValue"
              },
              "danger": {
                "$ref": "#/$defs/BrandColorValue"
              },
              "light": {
                "$ref": "#/$defs/BrandColorValue"
              },
              "dark": {
                "$ref": "#/$defs/BrandColorValue"
              },
              "emphasis": {
                "$ref": "#/$defs/BrandColorValue"
              },
              "link": {
                "$ref": "#/$defs/BrandColorValue"
              }
            }
          }
        },
        "BrandMaybeNamedColor": {
          "anyOf": [
            {
              "$ref": "#/$defs/BrandNamedThemeColor"
            },
            {
              "type": "string"
            }
          ]
        },
        "BrandNamedThemeColor": {
          "enum": [
            "foreground",
            "background",
            "primary",
            "secondary",
            "tertiary",
            "success",
            "info",
            "warning",
            "danger",
            "light",
            "dark",
            "emphasis",
            "link"
          ]
        },
        "BrandTypography": {
          "object": {
            "properties": {
              "with": {
                "$ref": "#/$defs/BrandFont"
              },
              "base": {
                "$ref": "#/$defs/BrandTypographyOptions"
              },
              "headings": {
                "$ref": "#/$defs/BrandTypographyOptionsNoSize"
              },
              "monospace": {
                "$ref": "#/$defs/BrandTypographyOptions"
              },
              "emphasis": {
                "object": {
                  "properties": {
                    "weight": {
                      "$ref": "#/$defs/BrandFontWeight"
                    },
                    "color": {
                      "$ref": "#/$defs/BrandMaybeNamedColor"
                    },
                    "background-color": {
                      "$ref": "#/$defs/BrandMaybeNamedColor"
                    }
                  }
                }
              },
              "link": {
                "object": {
                  "properties": {
                    "weight": {
                      "$ref": "#/$defs/BrandFontWeight"
                    },
                    "decoration": {
                      "type": "string"
                    },
                    "color": {
                      "$ref": "#/$defs/BrandMaybeNamedColor"
                    },
                    "background-color": {
                      "$ref": "#/$defs/BrandMaybeNamedColor"
                    }
                  }
                }
              }
            }
          }
        },
        "BrandTypographyOptions": {
          "object": {
            "properties": {
              "family": {
                "type": "string"
              },
              "size": {
                "type": "string"
              },
              "line-height": {
                "type": "string"
              },
              "weight": {
                "$ref": "#/$defs/BrandFontWeight"
              },
              "style": {
                "$ref": "#/$defs/BrandFontStyle"
              },
              "color": {
                "$ref": "#/$defs/BrandMaybeNamedColor"
              },
              "background-color": {
                "$ref": "#/$defs/BrandMaybeNamedColor"
              }
            }
          }
        },
        "BrandTypographyOptionsNoSize": {
          "object": {
            "properties": {
              "family": {
                "type": "string"
              },
              "line-height": {
                "type": "string"
              },
              "weight": {
                "$ref": "#/$defs/BrandFontWeight"
              },
              "style": {
                "$ref": "#/$defs/BrandFontStyle"
              },
              "color": {
                "$ref": "#/$defs/BrandMaybeNamedColor"
              },
              "background-color": {
                "$ref": "#/$defs/BrandMaybeNamedColor"
              }
            }
          }
        },
        "BrandFont": {
          "type": "array",
          "items": {
            "anyOf": [
              {
                "$ref": "#/$defs/BrandFontGoogle"
              },
              {
                "$ref": "#/$defs/BrandFontFile"
              },
              {
                "$ref": "#/$defs/BrandFontFamily"
              }
            ]
          }
        },
        "BrandFontWeight": {
          "enum": [
            100,
            200,
            300,
            400,
            500,
            600,
            700,
            800,
            900
          ]
        },
        "BrandFontStyle": {
          "enum": [
            "normal",
            "italic"
          ]
        },
        "BrandFontGoogle": {
          "object": {
            "properties": {
              "google": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "object": {
                      "properties": {
                        "family": {
                          "type": "string"
                        },
                        "weight": {
                          "anyOf": [
                            {
                              "type": "array",
                              "items": {
                                "$ref": "#/$defs/BrandFontWeight"
                              }
                            },
                            {
                              "$ref": "#/$defs/BrandFontWeight"
                            }
                          ]
                        },
                        "style": {
                          "anyOf": [
                            {
                              "type": "array",
                              "items": {
                                "$ref": "#/$defs/BrandFontStyle"
                              }
                            },
                            {
                              "$ref": "#/$defs/BrandFontStyle"
                            }
                          ]
                        },
                        "display": {
                          "enum": [
                            "auto",
                            "block",
                            "swap",
                            "fallback",
                            "optional"
                          ]
                        }
                      }
                    }
                  }
                ]
              }
            }
          }
        },
        "BrandFontFile": {
          "object": {
            "properties": {
              "family": {
                "type": "string"
              },
              "files": {
                "anyOf": [
                  {
                    "type": "array",
                    "items": {
                      "anyOf": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "string"
                        }
                      ]
                    }
                  },
                  {
                    "anyOf": [
                      {
                        "type": "string"
                      },
                      {
                        "type": "string"
                      }
                    ]
                  }
                ]
              }
            }
          }
        },
        "BrandFontFamily": {
          "type": "string"
        },
        "Brand": {
          "object": {
            "properties": {
              "meta": {
                "$ref": "#/$defs/BrandMeta"
              },
              "logo": {
                "$ref": "#/$defs/BrandLogo"
              },
              "color": {
                "$ref": "#/$defs/BrandColor"
              },
              "typography": {
                "$ref": "#/$defs/BrandTypography"
              },
              "defaults": {
                "type": "object"
              }
            }
          }
        }
      },
      "$ref": "#/$defs/Brand"
    }

</details>
