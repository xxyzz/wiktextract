import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry


def extract_translation_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name == "외국어":
            extract_translation_template(wxr, word_entry, t_node)


def extract_translation_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
) -> None:
    # https://ko.wiktionary.org/wiki/틀:외국어
    for key in [1, 2]:
        arg_value = t_node.template_parameters.get(key, [])
        parse_arg = wxr.wtp.parse(wxr.wtp.node_to_wikitext(arg_value))
        for list_item in parse_arg.find_child_recursively(NodeKind.LIST_ITEM):
            extract_translation_list_item(wxr, word_entry, list_item)


def extract_translation_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
) -> None:
    lang_code = "unknown"
    lang_name = "unknown"
    for node in list_item.children:
        if isinstance(node, str) and lang_name == "unknown":
            m = re.search(r"\((\w+)\):", node)
            if m is not None:
                lang_code = m.group(1)
                lang_name = node[: m.start()].strip()
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if word != "":
                word_entry.translations.append(
                    Translation(lang=lang_name, lang_code=lang_code, word=word)
                )
        elif isinstance(node, str) and "(" in node and ")" in node:
            text = ""
            brackets = 0
            for c in node:
                if c == "(":
                    brackets += 1
                elif c == ")":
                    brackets -= 1
                    if (
                        brackets == 0
                        and text.strip() != ""
                        and len(word_entry.translations) > 0
                    ):
                        text = text.strip()
                        if re.search(r"[a-z]", text):
                            word_entry.translations[-1].roman = text
                        else:
                            word_entry.translations[-1].raw_tags.append(text)
                        text = ""
                elif brackets > 0:
                    text += c