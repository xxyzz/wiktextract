from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pt.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPtForm(TestCase):
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

    def test_flex_pt_subst_completa(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        self.wxr.wtp.add_page(
            "Predefinição:flex.pt.subst.completa",
            10,
            """{|
|-
! style="background:#f4f4f4;" rowspan="2" |
! style="background:#ffffe0;" colspan="2" | [[masculino|Masculino]]
! style="background:#ffffe0;" colspan="2" | [[feminino|Feminino]]
! style="background:#ffffe0;" rowspan="2" | [[coletivo|Coletivo]]
|-
! style="background:#ffffe0;" | [[singular|Singular]]
! style="background:#ffffe0;" | [[plural|Plural]]
! style="background:#ffffe0;" | [[singular|Singular]]
! style="background:#ffffe0;" | [[plural|Plural]]
|-
! style="background:#f4f4f4;" | [[normal|Normal]]
| [[cão]]
| [[cães#Português|cães]]
| [[cadela#Português|cadela]]
| [[cadelas#Português|<span style="color:black">cadelas</span>]]
| rowspan="3" | [[matilha#Português|matilha]]
|}""",
        )
        self.wxr.wtp.add_page("Predefinição:AFI", 10, "{{{1}}}")
        data = parse_page(
            self.wxr,
            "cão",
            """={{-pt-}}=
==Substantivo==
# animal
{{flex.pt.subst.completa
|ms=cão|mp=cães|fs=cadela|fp=cadelas
|msa=canzarrão|mpa=canzarrões|fsa=cadelona|fpa=cadelonas
|msd=cãozinho|mpd=cãezinhos|fsd=cadelinha|fpd=cadelinhas
|col=matilha}}""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "cães", "tags": ["standard", "masculine", "plural"]},
                {
                    "form": "cadela",
                    "tags": ["standard", "feminine", "singular"],
                },
                {"form": "cadelas", "tags": ["standard", "feminine", "plural"]},
                {"form": "matilha", "tags": ["standard", "collective"]},
            ],
        )

    def test_slash_cell(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        self.wxr.wtp.add_page(
            "Predefinição:flex.pt.subst.completa",
            10,
            """{|
|-
! style="background:#f4f4f4;" rowspan="2" |
! style="background:#ffffe0;" colspan="2" | [[masculino|Masculino]]
! style="background:#ffffe0;" colspan="2" | [[feminino|Feminino]]
! style="background:#ffffe0;" rowspan="2" | [[coletivo|Coletivo]]
|-
! style="background:#ffffe0;" | [[singular|Singular]]
! style="background:#ffffe0;" | [[plural|Plural]]
! style="background:#ffffe0;" | [[singular|Singular]]
! style="background:#ffffe0;" | [[plural|Plural]]
|-
! style="background:#f4f4f4;" | [[normal|Normal]]
| style="background:#ffffff; text-align:center;" | [[parvo]]
| style="background:#ffffff; text-align:center;" | [[parvos#Português|<span style="color:black">parvos</span>]]
| style="background:#ffffff; text-align:center;" | [[parva#Português|parva]] / [[párvoa#Português|<span style="color:black">párvoa</span>]]
| style="background:#ffffff; text-align:center;" | [[parvas#Português|<span style="color:black">parvas</span>]] / [[párvoas#Português|<span style="color:black">párvoas</span>]]
| style="background:#ffffff; text-align:center;" rowspan="3" | [[-#Português|-]]
|}""",
        )
        data = parse_page(
            self.wxr,
            "parvo",
            """={{-pt-}}=
==Substantivo==
{{flex.pt.subst.completa
|alinhamento=left
|ms=parvo
|msa=parvalhão|msa2=parvoalho|msa3=parvoeirão
|msd=parvinho
|mp=parvos
|mpa=parvalhões|mpa2=parvoalhos|mpa3=parvoeirões
|mpd=parvinhos
|fs=parva|fs2=párvoa
|fsa=parvalhona|fsa2=parvoalha|fsa3=parvoeirona
|fsd=parvinha
|fp=parvas|fp2=párvoas
|fpa=parvalhonas|fpa2=parvoalhas|fpa3=pavoeironas
|fpd=parvinhas
|col=-
}}
# [[pessoa]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "parvos", "tags": ["standard", "masculine", "plural"]},
                {
                    "form": "parva",
                    "tags": ["standard", "feminine", "singular"],
                },
                {
                    "form": "párvoa",
                    "tags": ["standard", "feminine", "singular"],
                },
                {"form": "parvas", "tags": ["standard", "feminine", "plural"]},
                {"form": "párvoas", "tags": ["standard", "feminine", "plural"]},
            ],
        )