from wikitextprocessor import NodeKind, TemplateArgs, TemplateNode, WikiNode
from wikitextprocessor.parser import LEVEL_KIND_FLAGS

from wiktextract import WiktextractContext
from wiktextract.page import clean_node

from .models import Example, Form, Linkage, Sense, WordEntry
from .section_titles import POS_HEADINGS
from .table import parse_pos_table
from .tags_utils import convert_tags_in_sense
from .text_utils import (
    POS_ENDING_NUMBER_RE,
    POS_TEMPLATE_NAMES,
    STRIP_PUNCTUATION,
)

# from wiktextract.wxr_logging import logger


def remove_duplicate_forms(
    wxr: WiktextractContext, forms: list[Form]
) -> list[Form]:
    if not forms:
        return []
    new_forms = []
    for i, form in enumerate(forms):
        for comp in forms[i + 1 :]:
            if (
                form.form == comp.form
                and form.tags == comp.tags
                and form.raw_tags == comp.raw_tags
            ):
                break
                #  basically "continue" in our case, but this will not trigger
                # the follow else-block
        else:
            # No duplicates found in for loop (exited without breaking)
            new_forms.append(form)
    if len(forms) > len(new_forms):
        # wxr.wtp.debug("Found duplicate forms", sortid="simple/pos/32")
        return new_forms
    return forms


ExOrSense = Sense | Example

IGNORED_GLOSS_TEMPLATES = ("exstub",)


def parse_gloss(
    wxr: WiktextractContext, parent_sense: Sense, contents: list[str | WikiNode]
) -> bool:
    """Take what is preferably a line of text and extract tags and a gloss from
        it. The data is inserted into parent_sense, and for recursion purposes
        we return a boolean that tells whether there was any gloss text in a
        lower node."""
    if len(contents) == 0:
        return False

    template_tags: list[str] = []
    found_template = False
    synonyms: list[Linkage] = []
    antonyms: list[Linkage] = []

    def gloss_template_fn(name: str, ht: TemplateArgs) -> str | None:
        if name in ("synonyms", "synonym", "syn"):
            for syn in ht.values():
                if not syn:
                    continue
                synonyms.append(
                    Linkage(word=clean_node(wxr, parent_sense, syn))
                )
            return ""
        if name in ("antonyms", "antonym", "ant"):
            for ant in ht.values():
                if not ant:
                    continue
                antonyms.append(
                    Linkage(word=clean_node(wxr, parent_sense, ant))
                )
            return ""

        if name in IGNORED_GLOSS_TEMPLATES:
            return ""

        return None

    for i, tnode in enumerate(contents):
        if (
            isinstance(tnode, str)
            and tnode.strip(STRIP_PUNCTUATION)
            or not isinstance(tnode, (TemplateNode, str))
        ):
            break
        if isinstance(tnode, TemplateNode):
            if tnode.template_name == "exstub":
                parent_sense.raw_tags.append("no-gloss")
                return False
            tag_text = clean_node(
                wxr, parent_sense, tnode, template_fn=gloss_template_fn
            )
            if tag_text.endswith((")", "]")):
                # Simple wiktionary is pretty good at making these templates
                # have brackets
                tag_text = tag_text.strip(STRIP_PUNCTUATION)
                if tag_text:
                    found_template = True
                    template_tags.append(tag_text)
            else:
                # looks like normal text, so probably something {{plural of}}.
                break
    # else for the for loop: if we never break
    else:
        # If we never break, that means the last item was a tag.
        i += 1

    if found_template is True:
        contents = contents[i:]

    text = clean_node(
        wxr, parent_sense, contents, template_fn=gloss_template_fn
    )

    if len(synonyms) > 0:
        parent_sense.synonyms = synonyms

    if len(antonyms) > 0:
        parent_sense.antonyms = antonyms

    if len(template_tags) > 0:
        parent_sense.raw_tags.extend(template_tags)

    if len(text) > 0:
        parent_sense.glosses.append(text)
        return True

    return False


def recurse_glosses1(
    wxr: WiktextractContext,
    parent_sense: Sense,
    node: WikiNode,
) -> list[ExOrSense]:
    ret: list[ExOrSense] = []
    found_gloss = False

    if node.kind == NodeKind.LIST:
        for child in node.children:
            if isinstance(child, str):
                # This should never happen
                wxr.wtp.error(
                    f"str {child=} is direct child of NodeKind.LIST",
                    sortid="simple/pos/44",
                )
                continue
            ret.extend(
                recurse_glosses1(wxr, parent_sense.model_copy(deep=True), child)
            )
    if node.kind == NodeKind.LIST_ITEM:
        contents = []
        sublists = []
        broke_out = False
        for i, c in enumerate(node.children):
            if isinstance(c, WikiNode) and c.kind == NodeKind.LIST:
                broke_out = True
                break
            contents.append(c)
        if broke_out is True:
            sublists = node.children[i:]

        if node.sarg.endswith((":", "*")) and node.sarg not in (":", "*"):
            # This is either a quotation or example
            # != ":" filters out lines that are usually notes or random
            # stuff not inside gloss lists; see "dare"
            text = clean_node(
                wxr, parent_sense, contents
            )  # clean_node strip()s
            example = Example(text=text)
            # logger.debug(f"{wxr.wtp.title}/example\n{text}")
            # We will not bother with subglosses for example entries;
            # XXX do something about it if it becomes relevant
            return [example]
        elif node.sarg == ":":
            return []

        found_gloss = parse_gloss(wxr, parent_sense, contents)

        for sl in sublists:
            if not (isinstance(sl, WikiNode) and sl.kind == NodeKind.LIST):
                # Should not happen
                wxr.wtp.error(
                    f"Sublist is not NodeKind.LIST: {sublists=!r}",
                    sortid="simple/pos/82",
                )
                continue
            for r in recurse_glosses1(
                wxr, parent_sense.model_copy(deep=True), sl
            ):
                if isinstance(r, Example):
                    parent_sense.examples.append(r)
                else:
                    ret.append(r)

    if len(ret) > 0:
        # the recursion returned actual senses from below, so we will
        # ignore everything else (incl. any example data that might have
        # been given to parent_sense) and return that instead.
        # XXX if this becomes relevant, add the example data to a returned
        # subsense instead?
        return ret

    if found_gloss is True or "no-gloss" in parent_sense.raw_tags:
        return [parent_sense]

    return []


def recurse_glosses(
    wxr: WiktextractContext, node: WikiNode, data: WordEntry
) -> list[Sense]:
    base_sense = Sense()
    ret = []

    for r in recurse_glosses1(wxr, base_sense, node):
        if isinstance(r, Example):
            wxr.wtp.error(
                f"Example() has bubbled to recurse_glosses: {r.json()}",
                sortid="simple/pos/glosses",
            )
            continue
        convert_tags_in_sense(r)
        ret.append(r)

    if len(ret) > 0:
        return ret

    return []


def process_pos(
    wxr: WiktextractContext,
    node: WikiNode,
    data: WordEntry,
    # the "noun" in "Noun 2"
    pos_title: str,
    # the "2" in "Noun 2"
    pos_num: int = -1,
) -> WordEntry | None:
    """Process a part-of-speech section, like 'Noun'. `base_data` provides basic
    data common with other POS sections, like pronunciation or etymology."""

    pos_meta = POS_HEADINGS[pos_title]
    data.pos = pos_meta["pos"]
    data.pos_num = pos_num

    # Sound data associated with this POS might be coming from a shared
    # section, in which case we've tried to tag the sound data with its
    # pos name + number if possible. Filter out stuff that doesn't fit.
    new_sounds = []
    for sound in data.sounds:
        if len(sound.poses) == 0:
            # Sound data not tagged with any specific pos section, so add it
            new_sounds.append(sound)
        else:
            for sound_pos in sound.poses:
                m = POS_ENDING_NUMBER_RE.search(sound_pos)
                if m is not None:
                    s_num = int(m.group(1).strip())
                    s_pos = sound_pos[: m.start()].strip().lower()
                else:
                    s_pos = sound_pos.strip().lower()
                    s_num = -1
                sound_meta = POS_HEADINGS[s_pos]
                s_pos = sound_meta["pos"]
                if s_pos == data.pos and s_num == data.pos_num:
                    new_sounds.append(sound)
    data.sounds = new_sounds

    pos_contents = list(node.invert_find_child(LEVEL_KIND_FLAGS))

    if len(pos_contents) == 0:
        wxr.wtp.error(
            "No body for Part-of-speech section.", sortid="simple/pos/271"
        )
        data.senses.append(Sense(tags=["no-gloss"]))
        return data

    # check POS templates at the start of the section (Simple English specific)
    template_tags: list[str] = []
    template_forms: list[Form] = []

    # Typically, a Wiktionary has a word head before glosses, which contains
    # the main form of the word (usually same as the title of the article)
    # and common other forms of the word, plus qualifiers and other data
    # like that; however, for Simple English Wiktionary the format is to
    # have a table (or two, if there's variations) containing the word's
    # conjugation or declension, so we don't have to actually parse the
    # head here.
    for i, child in enumerate(pos_contents):
        if isinstance(child, str) and not child.strip():
            # Ignore whitespace
            continue
        # TemplateNode is a subclass of WikiNode; not all kinds of nodes have
        # a subclass, but TemplateNode is handy.
        if (
            isinstance(child, TemplateNode)
            and child.template_name in POS_TEMPLATE_NAMES
        ):
            if child.template_name not in pos_meta["templates"]:
                wxr.wtp.debug(
                    f"Template {child.template_name} "
                    f"found under {pos_title}",
                    sortid="simple/pos/93",
                )
            elif ttags := pos_meta["templates"][child.template_name]:
                # Some templates have associated tags:
                # `irrnoun` -> ["irregular"]
                template_tags.extend(ttags)
            if forms := parse_pos_table(wxr, child, data):
                template_forms.extend(forms)
            else:
                wxr.wtp.warning(
                    f"POS template '{child.template_name}' did "
                    "not have any forms.",
                    sortid="simple/pos/129",
                )
        else:
            break

    template_tags = list(set(template_tags))
    data.forms.extend(template_forms)
    data.forms = remove_duplicate_forms(wxr, data.forms)
    data.tags.extend(template_tags)

    # parts = []
    found_list = False
    got_senses = False
    for child in pos_contents[i:]:
        # Wiktionaries handle glosses the usual way: with numbered lists.
        # Each list entry is a gloss, sometimes with subglosses, but with
        # Simple English Wiktionary that seems rare.
        # logger.debug(f"{child}")
        if isinstance(child, WikiNode) and child.kind == NodeKind.LIST:
            senses = recurse_glosses(wxr, child, data)
            found_list = True
            if len(senses) > 0:
                got_senses = True
                data.senses.extend(senses)

    if not got_senses and found_list:
        wxr.wtp.error(
            "POS had a list, but the list did not return senses.",
            sortid="simple/pos/313",
        )

    # If there is not list, clump everything into one gloss.
    if not found_list:
        sense = Sense()
        found_gloss = parse_gloss(wxr, sense, pos_contents[i:])
        if found_gloss is True or len(sense.raw_tags) > 0:
            convert_tags_in_sense(sense)
            if len(sense.glosses) == 0 and "no-gloss" not in sense.tags:
                sense.tags.append("no-gloss")
            data.senses.append(sense)

    if len(data.senses) == 0:
        data.senses.append(Sense(tags=["no-gloss"]))

    return data
