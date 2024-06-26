from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry
from .util import append_base_data


def extract_etymology(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    from .example import extract_template_zh_x
    from .page import parse_section

    etymology_nodes = []
    level_node_index = len(level_node.children)
    for next_level_index, next_level_node in level_node.find_child(
        LEVEL_KIND_FLAGS, True
    ):
        level_node_index = next_level_index
        break
    for etymology_node in level_node.children[:level_node_index]:
        if (
            isinstance(etymology_node, TemplateNode)
            and etymology_node.template_name == "zh-x"
        ):
            for example_data in extract_template_zh_x(wxr, etymology_node):
                base_data.etymology_examples.append(example_data)
            clean_node(wxr, page_data[-1], etymology_node)
        elif (
            isinstance(etymology_node, WikiNode)
            and etymology_node.kind == NodeKind.LIST
        ):
            has_zh_x = False
            for template_node in etymology_node.find_child_recursively(
                NodeKind.TEMPLATE
            ):
                if template_node.template_name == "zh-x":
                    has_zh_x = True
                    for example_data in extract_template_zh_x(
                        wxr, template_node
                    ):
                        base_data.etymology_examples.append(example_data)
                    clean_node(wxr, page_data[-1], template_node)
            if not has_zh_x:
                etymology_nodes.append(etymology_node)
        else:
            etymology_nodes.append(etymology_node)

    etymology_text = clean_node(wxr, page_data[-1], etymology_nodes)
    if len(etymology_text) > 0:
        base_data.etymology_text = etymology_text
        append_base_data(page_data, "etymology_text", etymology_text, base_data)
        page_data[-1].etymology_examples = base_data.etymology_examples

    if level_node_index < len(level_node.children):
        parse_section(
            wxr, page_data, base_data, level_node.children[level_node_index:]
        )
