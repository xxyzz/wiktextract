from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pt.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPtHeadLine(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        conf = WiktionaryConfig(
            dump_file_lang_code="pt",
            capture_language_codes=None,
        )
        self.wxr = WiktextractContext(
            Wtp(
                lang_code="pt",
                parser_function_aliases=conf.parser_function_aliases,
            ),
            conf,
        )

    def test_gramática_template(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        self.wxr.wtp.add_page("Predefinição:g", 10, "''masculino''")
        data = parse_page(
            self.wxr,
            "cão",
            """={{-pt-}}=
==Adjetivo==
{{oxítona|cão}}, {{g|m}}
# [[cruel]]""",
        )
        self.assertEqual(data[0]["tags"], ["masculine"])