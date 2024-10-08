# Tests for parsing a page
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestFrPage(TestCase):
    maxDiff = None

    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"),
            WiktionaryConfig(
                dump_file_lang_code="fr",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_fr_parse_page(self):
        # https://fr.wiktionary.org/wiki/anthracite
        self.wxr.wtp.add_page(
            "Modèle:langue",
            10,
            "{{#switch: {{{1}}} | fr = Français | en = Anglais }}",
        )
        self.wxr.wtp.add_page(
            "Modèle:S",
            10,
            """{{#switch: {{{1}}}
| étymologie = Étymologie
| nom = Nom commun[[Catégorie:Noms communs en {{{2}}}]]
| adjectif = Adjectif[[Catégorie:Adjectifs en {{{2}}}]]
}}""",
        )
        self.wxr.wtp.add_page("Modèle:roches", 10, "''(Pétrographie)''")
        self.wxr.wtp.add_page("Modèle:indénombrable", 10, "''(Indénombrable)''")

        page_data = parse_page(
            self.wxr,
            "anthracite",
            """== {{langue|fr}} ==
=== {{S|étymologie}} ===
: (1549) Du latin anthracites.

=== {{S|nom|fr}} ===
# {{roches|fr}} [[variété|Variété]] de [[charbon de terre]], à [[reflet]] [[métallique]] et à [[combustion]] [[lent]]e.

=== {{S|adjectif|fr}} ===
# De couleur anthracite, gris très foncé, du nom de la variété de charbon du même nom.

=== {{S|références}} ===
* {{Import:DAF8}}

[[Catégorie:Couleurs noires en français]]
[[Catégorie:Adjectifs invariables en français]]
[[Catégorie:Jurons du capitaine Haddock en français]]
[[Catégorie:Couleurs grises en français]]

== {{langue|en}} ==

=== {{S|étymologie}} ===
: Du latin anthracites.

=== {{S|nom|en}} ===
# {{indénombrable|en}} [[anthracite#fr|Anthracite]].""",  # noqa: E501
        )
        self.assertEqual(
            page_data,
            [
                {
                    "categories": [
                        "Noms communs en fr",
                        "Couleurs noires en français",
                        "Adjectifs invariables en français",
                        "Jurons du capitaine Haddock en français",
                        "Couleurs grises en français",
                    ],
                    "lang": "Français",
                    "lang_code": "fr",
                    "pos": "noun",
                    "pos_title": "Nom commun",
                    "word": "anthracite",
                    "senses": [
                        {
                            "glosses": [
                                "Variété de charbon de terre, à reflet "
                                "métallique et à combustion lente."
                            ],
                            "topics": ["petrography"],
                        }
                    ],
                    "etymology_texts": ["(1549) Du latin anthracites."],
                },
                {
                    "categories": [
                        "Adjectifs en fr",
                        "Couleurs noires en français",
                        "Adjectifs invariables en français",
                        "Jurons du capitaine Haddock en français",
                        "Couleurs grises en français",
                    ],
                    "lang": "Français",
                    "lang_code": "fr",
                    "pos": "adj",
                    "pos_title": "Adjectif",
                    "word": "anthracite",
                    "senses": [
                        {
                            "glosses": [
                                "De couleur anthracite, gris très foncé, "
                                "du nom de la variété de charbon du même nom."
                            ]
                        }
                    ],
                    "etymology_texts": ["(1549) Du latin anthracites."],
                },
                {
                    "categories": ["Noms communs en en"],
                    "lang": "Anglais",
                    "lang_code": "en",
                    "pos": "noun",
                    "pos_title": "Nom commun",
                    "word": "anthracite",
                    "senses": [
                        {
                            "glosses": ["Anthracite."],
                            "tags": ["uncountable"],
                        }
                    ],
                    "etymology_texts": ["Du latin anthracites."],
                },
            ],
        )

    def test_pos_under_etymology_section(self):
        # https://fr.wiktionary.org/wiki/Deutsche
        self.wxr.wtp.add_page("Modèle:langue", 10, "Allemand")
        self.wxr.wtp.add_page(
            "Modèle:substantivation de",
            10,
            "Substantivation de l’adjectif deutsch",
        )
        self.wxr.wtp.add_page(
            "Modèle:S",
            10,
            """{{#switch: {{{1}}}
| étymologie = Étymologie
| nom = Nom commun
}} {{{num|}}}""",
        )
        page_data = parse_page(
            self.wxr,
            "Deutsche",
            """== {{langue|de}} ==
=== {{S|étymologie}} ===
: {{substantivation de|type=adjectif|deutsch|de}}

==== {{S|nom|de|num=1}} ====
# Allemand, la langue allemande, langue indo-européenne germanique.""",
        )
        self.assertEqual(
            page_data,
            [
                {
                    "word": "Deutsche",
                    "lang": "Allemand",
                    "lang_code": "de",
                    "pos": "noun",
                    "pos_title": "Nom commun 1",
                    "etymology_texts": [
                        "Substantivation de l’adjectif deutsch"
                    ],
                    "senses": [
                        {
                            "glosses": [
                                "Allemand, la langue allemande, langue "
                                "indo-européenne germanique."
                            ]
                        }
                    ],
                }
            ],
        )

    def test_level4_etymology_notes_section(self):
        # shouldn't add no-gloss sense data
        self.wxr.wtp.add_page("Modèle:langue", 10, "Anglais")
        self.wxr.wtp.add_page(
            "Modèle:substantivation de",
            10,
            "Substantivation de l’adjectif deutsch",
        )
        self.wxr.wtp.add_page(
            "Modèle:S",
            10,
            """{{#switch: {{{1}}}
| étymologie = Étymologie
| suffixe = Suffixe
}} {{{num|}}}""",
        )
        page_data = parse_page(
            self.wxr,
            "-ly",
            """== {{langue|en}} ==
=== {{S|étymologie}} ===
: Du vieil anglais -lich, même sens.

==== {{S|notes}} ====
note

=== {{S|suffixe|en}} ===
# gloss""",
        )
        self.assertEqual(
            page_data,
            [
                {
                    "word": "-ly",
                    "lang": "Anglais",
                    "lang_code": "en",
                    "pos": "suffix",
                    "pos_title": "Suffixe",
                    "etymology_texts": ["Du vieil anglais -lich, même sens."],
                    "notes": ["note"],
                    "tags": ["morpheme"],
                    "senses": [{"glosses": ["gloss"]}],
                }
            ],
        )
