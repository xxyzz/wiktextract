from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Example, WordEntry


def extract_etymology_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    from .example import extract_template_zh_x

    etymology_nodes = []
    level_node_index = len(level_node.children)
    for next_level_index, next_level_node in level_node.find_child(
        LEVEL_KIND_FLAGS, True
    ):
        level_node_index = next_level_index
        break
    for etymology_node in level_node.children[:level_node_index]:
        if isinstance(
            etymology_node, TemplateNode
        ) and etymology_node.template_name in ["zh-x", "zh-q"]:
            for example_data in extract_template_zh_x(
                wxr, etymology_node, Example()
            ):
                base_data.etymology_examples.append(example_data)
            clean_node(wxr, base_data, etymology_node)
        elif isinstance(
            etymology_node, TemplateNode
        ) and etymology_node.template_name.lower() in [
            "rfe",  # missing etymology
            "zh-forms",
            "zh-wp",
            "wp",
            "wikipedia",
        ]:
            pass
        elif (
            isinstance(etymology_node, WikiNode)
            and etymology_node.kind == NodeKind.LIST
        ):
            has_zh_x = False
            for template_node in etymology_node.find_child_recursively(
                NodeKind.TEMPLATE
            ):
                if template_node.template_name in ["zh-x", "zh-q"]:
                    has_zh_x = True
                    for example_data in extract_template_zh_x(
                        wxr, template_node, Example()
                    ):
                        base_data.etymology_examples.append(example_data)
                    clean_node(wxr, base_data, template_node)
            if not has_zh_x:
                etymology_nodes.append(etymology_node)
        elif isinstance(
            etymology_node, TemplateNode
        ) and etymology_node.template_name in [
            "ja-see",
            "ja-see-kango",
            "zh-see",
        ]:
            from .page import process_soft_redirect_template

            page_data.append(base_data.model_copy(deep=True))
            process_soft_redirect_template(wxr, etymology_node, page_data[-1])
        else:
            etymology_nodes.append(etymology_node)

    etymology_text = clean_node(wxr, base_data, etymology_nodes)
    if len(etymology_text) > 0:
        base_data.etymology_text = etymology_text
