import re

from mediawiki_langcodes import name_to_code
from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Descendant, Linkage, Translation, WordEntry
from .tags import translate_raw_tags
from .utils import extract_sense_index


def extract_linkages(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
) -> None:
    linkage_list = []
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        process_linkage_list_item(wxr, list_item, linkage_list, linkage_type)
    getattr(word_entry, linkage_type).extend(linkage_list)


def process_linkage_list_item(
    wxr: WiktextractContext,
    list_item_node: WikiNode,
    linkage_list: list[Linkage],
    linkage_type: str,
) -> None:
    sense_idx = ""
    raw_tags = []
    after_dash = False
    note_nodes = []
    for child in list_item_node.children:
        if after_dash:
            note_nodes.append(child)
        elif isinstance(child, str):
            if child.startswith("["):
                sense_idx, _ = extract_sense_index(child)
            elif "," in child or ";" in child:
                raw_tags.clear()
            if linkage_type == "expressions" and contains_dash(child):
                after_dash = True
                note_nodes.append(child)
        elif isinstance(child, WikiNode) and child.kind == NodeKind.ITALIC:
            raw_tag = clean_node(wxr, None, child)
            if raw_tag.endswith(":"):
                raw_tags.append(raw_tag.strip(": "))
            else:
                for link_node in child.find_child(NodeKind.LINK):
                    link_text = clean_node(wxr, None, link_node)
                    if link_text != "":
                        linkage = Linkage(
                            word=link_text,
                            sense_index=sense_idx,
                            raw_tags=raw_tags,
                        )
                        translate_raw_tags(linkage)
                        linkage_list.append(linkage)
        elif isinstance(child, TemplateNode) and child.template_name.endswith(
            "."
        ):
            raw_tag = clean_node(wxr, None, child)
            raw_tag = raw_tag.strip(",: ")
            if raw_tag != "":
                raw_tags.append(raw_tag)
        elif isinstance(child, WikiNode) and child.kind == NodeKind.LINK:
            word = clean_node(wxr, None, child)
            if not word.startswith("Verzeichnis:") and len(word) > 0:
                # https://de.wiktionary.org/wiki/Wiktionary:Verzeichnis
                # ignore index namespace links
                linkage = Linkage(
                    word=word, sense_index=sense_idx, raw_tags=raw_tags
                )
                translate_raw_tags(linkage)
                linkage_list.append(linkage)

    if len(note_nodes) > 0 and len(linkage_list) > 0:
        linkage_list[-1].note = clean_node(wxr, None, note_nodes).strip(
            "–—―‒- "
        )


def contains_dash(text: str) -> bool:
    return re.search(r"[–—―‒-]", text) is not None


def extract_descendant_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_descendant_list_item(wxr, word_entry, list_item)


def extract_descendant_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
) -> None:
    lang_name = "unknown"
    lang_code = "unknown"
    sense_index = ""
    for node in list_item.children:
        if isinstance(node, str) and node.strip().startswith("["):
            sense_index, _ = extract_sense_index(node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
            node_str = clean_node(wxr, None, node)
            if node_str.endswith(":"):
                lang_name = node_str.strip(": ")
                lang_code = name_to_code(lang_name, "de") or "unknown"
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            node_str = clean_node(wxr, None, node)
            if node != "":
                word_entry.descendants.append(
                    Descendant(
                        lang=lang_name,
                        lang_code=lang_code,
                        word=node_str,
                        sense_index=sense_index,
                    )
                )
        elif isinstance(node, TemplateNode) and node.template_name.startswith(
            "Ü"
        ):
            from .translation import process_u_template

            tr_data = Translation(lang=lang_name, lang_code=lang_code)
            process_u_template(wxr, tr_data, node)
            if tr_data.word != "":
                word_entry.descendants.append(
                    Descendant(
                        lang=tr_data.lang,
                        lang_code=tr_data.lang_code,
                        word=tr_data.word,
                        roman=tr_data.roman,
                        sense_index=sense_index,
                    )
                )
