import re

from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    NodeKind,
    TemplateNode,
    WikiNode,
    WikiNodeChildrenList,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import EXAMPLE_TEMPLATES, process_example_template
from .linkage import process_semantics_template
from .models import Linkage, Sense, WordEntry
from .section_titles import LINKAGE_TITLES
from .tags import translate_raw_tags

IGNORED_TEMPLATES = {"нужен перевод", "??", "?", "Нужен перевод"}

TAG_GLOSS_TEMPLATES = {
    "многокр.": "iterative",
    "нареч.": "adverb",
    "наречие": "adverb",  # redirect to "нареч."
    "однокр.": "semelefactive",
    "превосх.": "superlative",
    "прич.": "participle",
    "сокр.": "abbreviation",
    "сравн.": "comparative",
    "страд.": "passive",
    "счётн.": "numeral",
}


def extract_gloss(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: WikiNode
) -> None:
    has_gloss_list = False
    for list_node in level_node.find_child(NodeKind.LIST):
        for sense_index, list_item in enumerate(
            list_node.find_child(NodeKind.LIST_ITEM), 1
        ):
            process_gloss_list_item(wxr, word_entry, list_item, sense_index)
        has_gloss_list = True
    if not has_gloss_list:
        node = wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(
                list(level_node.invert_find_child(LEVEL_KIND_FLAGS))
            )
        )
        process_gloss_list_item(wxr, word_entry, node, 1)


def process_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    sense_index: int,
    parent_sense: Sense | None = None,
) -> None:
    sense = (
        Sense() if parent_sense is None else parent_sense.model_copy(deep=True)
    )
    gloss_nodes = []
    for child in list_item.children:
        if isinstance(child, TemplateNode):
            if child.template_name in EXAMPLE_TEMPLATES:
                process_example_template(wxr, sense, child)
            elif child.template_name == "семантика":
                process_semantics_template(wxr, word_entry, child, sense_index)
            elif child.template_name in TAG_GLOSS_TEMPLATES:
                sense.tags.append(TAG_GLOSS_TEMPLATES[child.template_name])
                gloss_nodes.append(child)
            elif (
                child.template_name.endswith(".")
                or child.template_name == "помета"
            ):
                # Assume node is tag template
                raw_tag = clean_node(wxr, sense, child)
                if raw_tag != "":
                    sense.raw_tags.append(raw_tag)
            elif child.template_name == "значение":
                process_meaning_template(wxr, sense, word_entry, child)
            elif child.template_name.lower() not in IGNORED_TEMPLATES:
                gloss_nodes.append(child)
        elif not (isinstance(child, WikiNode) and child.kind == NodeKind.LIST):
            gloss_nodes.append(child)

    remove_obsolete_leading_nodes(gloss_nodes)
    gloss = clean_node(wxr, sense, gloss_nodes)
    if len(gloss) > 0:
        sense.glosses.append(gloss)
    if len(sense.glosses) > 0:
        translate_raw_tags(sense)
        word_entry.senses.append(sense)

    for child_list in list_item.find_child(NodeKind.LIST):
        for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
            process_gloss_list_item(
                wxr, word_entry, child_list_item, sense_index, sense
            )


def remove_obsolete_leading_nodes(nodes: WikiNodeChildrenList):
    while (
        nodes
        and isinstance(nodes[0], str)
        and nodes[0].strip() in ["", "и", "или", ",", ".", ";", ":"]
    ):
        nodes.pop(0)


def process_meaning_template(
    wxr: WiktextractContext,
    sense: Sense | None,
    word_entry: WordEntry,
    template_node: TemplateNode,
) -> Sense:
    # https://ru.wiktionary.org/wiki/Шаблон:значение
    if sense is None:
        sense = Sense()

    gloss = ""
    for param_name, param_value in template_node.template_parameters.items():
        if param_name == "определение":
            gloss = clean_node(wxr, None, param_value)
            if len(gloss) > 0:
                sense.glosses.append(gloss)
        elif param_name == "пометы":
            raw_tag = clean_node(wxr, None, param_value)
            if len(raw_tag) > 0:
                sense.raw_tags.append(raw_tag)
        elif param_name == "примеры" and isinstance(param_value, list):
            for t_node in param_value:
                if isinstance(t_node, TemplateNode):
                    process_example_template(wxr, sense, t_node)
        elif param_name in LINKAGE_TITLES:
            linkage_type = LINKAGE_TITLES[param_name]
            if isinstance(param_value, str) and len(param_value.strip()) > 0:
                for linkage_word in re.split(r",|;", param_value):
                    linkage_word = linkage_word.strip()
                    if len(linkage_word) > 0 and linkage_word != "-":
                        linkage_list = getattr(word_entry, linkage_type)
                        linkage_list.append(
                            Linkage(word=linkage_word, sense=gloss)
                        )
            elif isinstance(param_value, list):
                for param_node in param_value:
                    if (
                        isinstance(param_node, WikiNode)
                        and param_node.kind == NodeKind.LINK
                    ):
                        linkage_word = clean_node(wxr, None, param_node)
                        if len(linkage_word) > 0:
                            linkage_list = getattr(word_entry, linkage_type)
                            linkage_list.append(
                                Linkage(word=linkage_word, sense=gloss)
                            )

    if len(sense.glosses) > 0:
        translate_raw_tags(sense)

    clean_node(wxr, sense, template_node)
    return sense
