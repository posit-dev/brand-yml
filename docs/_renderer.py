from __future__ import annotations

import re
from typing import Optional, Union

from griffe import (
    Alias,
    DocstringAttribute,
    DocstringParameter,
    DocstringSectionAttributes,
    DocstringSectionParameters,
    DocstringSectionText,
    Expr,
    ExprName,
    Function,
    Object,
)
from plum import dispatch
from quartodoc import MdRenderer, layout
from quartodoc.pandoc.blocks import DefinitionList
from quartodoc.renderers.base import convert_rst_link_to_md
from quartodoc.renderers.md_renderer import sanitize


class Renderer(MdRenderer):
    style = "brand.yml"

    @dispatch
    def render(self, el: DocstringSectionAttributes):
        rows = list(map(self.render, el.value))

        return str(DefinitionList(rows))

    @dispatch
    def render(self, el: DocstringAttribute):
        if el.name == "model_config":
            return

        name = sanitize(el.name)
        annotation = self.render_annotation(el.annotation)

        return (name, f"{annotation}\n\n{el.description or ''}")

    @dispatch
    def render_annotation(self, el: None):
        return ""

    @dispatch
    def render_annotation(self, el: Expr):
        # an expression is essentially a list[ExprName | str]
        # e.g. Optional[TagList]
        #   -> [Name(source="Optional", ...), "[", Name(...), "]"]

        return "".join(map(self.render_annotation, el))

    @dispatch
    def render_annotation(self, el: ExprName):
        # e.g. Name(source="Optional", full="typing.Optional")
        return f"[{el.name}](`{el.canonical_path}`)"

    @dispatch
    def render(self, el: Union[layout.DocClass, layout.DocModule]):
        res = super().render(el)
        if not isinstance(res, str):
            return res

        res = res.split("\n")
        final = []
        for i, line in enumerate(res):
            if line != "" or i == len(res) - 1 or i == 0:
                final += [line]
                continue

            if res[i - 1].endswith("|") and res[i + 1].startswith("|"):
                continue

            final += [line]

        final = "\n".join(final)

        # remove empty attributes section
        final = re.sub(
            r"##* Attributes\s*\n\| Name \| Description \|\s*\n\| -* \| -* \|\n\n",
            "",
            final,
        )
        return final

    @dispatch
    def summarize(
        self, el: layout.Doc, path: Optional[str] = None, shorten: bool = False
    ):
        if el.name == "model_config":
            return ""
        return super().summarize(el)

    @dispatch
    # Overload of `quartodoc.renderers.md_renderer` to fix bug where the descriptions
    # are cut off and never display other places. Fixing by always displaying the
    # documentation.
    def summarize(self, obj: Union[Object, Alias]) -> str:
        # get high-level description
        doc = obj.docstring
        if doc is None:
            docstring_parts = []
        else:
            docstring_parts = doc.parsed

        if len(docstring_parts) and isinstance(
            docstring_parts[0], DocstringSectionText
        ):
            description = docstring_parts[0].value

            # # ## Approach: Always return the full description!
            # return description

            parts = description.split("\n")

            # Alternative: Add take the first paragraph as the description summary
            short_parts: list[str] = []
            # Capture the first paragraph (lines until first empty line)
            for part in parts:
                if part.strip() == "":
                    break
                short_parts.append(part)

            short = " ".join(short_parts)
            short = convert_rst_link_to_md(short)

            return short

        return ""

    # Consolidate the parameter type info into a single column
    @dispatch
    def render(self, el: DocstringParameter):
        param = f'<span class="parameter-name">{el.name}</span>'
        annotation = self.render_annotation(el.annotation)
        if annotation:
            param = f'{param}<span class="parameter-annotation-sep">:</span> <span class="parameter-annotation">{annotation}</span>'
        if el.default:
            param = f'{param} <span class="parameter-default-sep">=</span> <span class="parameter-default">{el.default}</span>'

        # Wrap everything in a code block to allow for links
        param = "<code>" + param + "</code>"

        return (param, el.description)

    @dispatch
    def render(self, el: DocstringSectionParameters):
        rows = list(map(self.render, el.value))
        # rows is a list of tuples of (<parameter>, <description>)

        return str(DefinitionList(rows))

    @dispatch
    def signature(self, el: Function, source: Optional[Alias] = None):
        if el.name == "__call__":
            # Ex: experimental.ui._card.ImgContainer.__call__(self, *args: Tag) -> Tagifiable
            sig = super().signature(el, source)

            # Remove leading function name (before `__call__`) and `self` parameter
            # Ex: __call__(*args: Tag) -> Tagifiable
            sig = re.sub(r"[^`\s]*__call__\(self, ", "__call__(", sig, count=1)

            return sig

        # Not a __call__ Function, so render as normal.
        return super().signature(el, source)
