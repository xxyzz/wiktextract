from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import extract_example_list_item
from .models import Sense, WordEntry
from .section_titles import POS_DATA
from .tag_form_line import extract_tag_form_line_nodes
from .tags import translate_raw_tags

POS_SUBSECTION_TEMPLATES = frozenset(
    [
        # https://it.wiktionary.org/wiki/Categoria:Template_per_i_verbi
        "-participio passato-",
        "-participio presente-",
        "Ausiliare",
        "Deponente",
        "Intransitivo",
        "Medio",
        "Passivo",
        "Reciproco",
        "Riflessivo",
        "riflessivo",
        "Transitivo",
        # https://it.wiktionary.org/wiki/Categoria:Template_vocabolo
        "Attivo",
        "attivo",
        "Inpr",
        "inpr",
        "Riflpr",
    ]
)


def add_new_pos_data(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    pos_title: str,
) -> None:
    page_data.append(base_data.model_copy(deep=True))
    page_data[-1].pos_title = pos_title
    pos_data = POS_DATA[pos_title]
    page_data[-1].pos = pos_data["pos"]
    page_data[-1].tags.extend(pos_data.get("tags", []))
    for link_node in level_node.find_child(NodeKind.LINK):
        clean_node(wxr, page_data[-1], link_node)


def extract_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    pos_title: str,
) -> None:
    add_new_pos_data(wxr, page_data, base_data, level_node, pos_title)
    first_gloss_list_index = len(level_node.children)
    for index, node in enumerate(level_node.children):
        if (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.LIST
            and node.sarg.startswith("#")
            and node.sarg.endswith("#")
        ):
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, page_data[-1], list_item)
            if index < first_gloss_list_index:
                first_gloss_list_index = index
        elif (
            isinstance(node, TemplateNode)
            and node.template_name in POS_SUBSECTION_TEMPLATES
        ):
            if len(page_data[-1].senses) > 0:
                add_new_pos_data(
                    wxr, page_data, base_data, level_node, pos_title
                )
            raw_tag = clean_node(wxr, page_data[-1], node).strip("= \n")
            page_data[-1].raw_tags.append(raw_tag)

    extract_tag_form_line_nodes(
        wxr, page_data[-1], level_node.children[:first_gloss_list_index]
    )


def extract_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
) -> None:
    gloss_nodes = []
    sense = Sense()
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            t_str = clean_node(wxr, sense, node)
            if t_str.startswith("(") and t_str.endswith(")"):
                sense.raw_tags.append(t_str.strip("()"))
            else:
                gloss_nodes.append(t_str)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            if (
                node.sarg.endswith(":")
                and len(sense.examples) > 0
                and sense.examples[-1].translation == ""
            ):
                for tr_list_item in node.find_child(NodeKind.LIST_ITEM):
                    sense.examples[-1].translation = clean_node(
                        wxr, sense, tr_list_item.children
                    )
            elif node.sarg.endswith(("*", ":")):
                for example_list_item in node.find_child(NodeKind.LIST_ITEM):
                    extract_example_list_item(
                        wxr, sense, example_list_item, word_entry.lang_code
                    )
        else:
            gloss_nodes.append(node)
    gloss_str = clean_node(wxr, sense, gloss_nodes)
    if gloss_str != "":
        sense.glosses.append(gloss_str)
        translate_raw_tags(sense)
        word_entry.senses.append(sense)