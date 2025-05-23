from wikitextprocessor import Page, Wtp

SECTION_TITLE_TEMPLATES = {
    "Templat:crh",
    "Templat:eo-kn",
    "Templat:lnd",
    "Templat:ms-kkt",
    "Templat:ms-kt",
}


def analyze_template(wtp: Wtp, page: Page) -> tuple[set[str], bool]:
    return set(), page.title in SECTION_TITLE_TEMPLATES
