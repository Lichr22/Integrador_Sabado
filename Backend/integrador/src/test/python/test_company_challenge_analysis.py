import importlib.util
import io
import json
import pathlib
import sys
import unittest
from unittest import mock


SCRIPT = (
    pathlib.Path(__file__).parents[2]
    / "main"
    / "resources"
    / "company_challenge_analysis.py"
)
SPEC = importlib.util.spec_from_file_location("company_challenge_analysis", SCRIPT)
ANALYSIS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANALYSIS)


class CompanyChallengeAnalysisTests(unittest.TestCase):
    def test_repairs_mojibake_in_company_names(self):
        expected = "Pinzón, Gómez and Ayala"
        mojibake = expected.encode("utf-8").decode("cp1252")
        self.assertEqual(
            ANALYSIS.clean_text(mojibake),
            expected,
        )

    def test_cleans_labels_and_counts_challenges_by_company_id(self):
        company_name = "Compañía Norte"
        mojibake_name = company_name.encode("utf-8").decode("cp1252")
        result = ANALYSIS.analyze(
            {
                "empresas": [
                    {"id": "company-a", "nombre": f"  {mojibake_name}   "},
                    {"id": "company-b", "nombre": company_name},
                    {"id": "missing", "nombre": "   "},
                ],
                "retos": [
                    {"id_empresa": "company-a", "estado": " ABIERTO "},
                    {"id_empresa": "company-a", "estado": "Cerrado"},
                    {"id_empresa": "unknown-company", "estado": "abierto"},
                ],
            }
        )

        self.assertEqual(result["estadisticas"]["totalRetos"], 3)
        self.assertEqual(result["estadisticas"]["retosAbiertos"], 1)
        self.assertEqual(result["estadisticas"]["retosSinEmpresa"], 1)
        self.assertEqual(result["estadisticas"]["empresasSinRetos"], 2)
        self.assertEqual(result["estadisticas"]["gruposConNombreDuplicado"], 1)
        companies = {company["empresaId"]: company for company in result["empresas"]}
        self.assertEqual(companies["company-a"]["nombre"], "Compañía Norte")
        self.assertTrue(companies["company-a"]["nombreCorregido"])
        self.assertEqual(companies["company-a"]["retos"], 2)
        self.assertEqual(companies["company-a"]["retosAbiertos"], 1)
        self.assertEqual(companies["missing"]["nombre"], "Empresa sin nombre (missing)")

    def test_handles_empty_input_without_division_errors(self):
        result = ANALYSIS.analyze({"empresas": [], "retos": []})

        self.assertEqual(result["empresas"], [])
        self.assertEqual(result["estadisticas"]["promedioRetos"], 0)
        self.assertEqual(result["estadisticas"]["medianaRetos"], 0)
        self.assertIsNone(result["estadisticas"]["empresaLider"])

    def test_clean_text_handles_none_spaces_and_invisible_characters(self):
        self.assertEqual(ANALYSIS.clean_text(None), "")
        self.assertEqual(ANALYSIS.clean_text("  Acme \n\t S.A.S  "), "Acme S.A.S")
        self.assertEqual(ANALYSIS.clean_text("Ac​me"), "Acme")

    def test_normalize_key_ignores_case_and_accents(self):
        self.assertEqual(ANALYSIS.normalize_key("  ABIERTO "), "abierto")
        self.assertEqual(
            ANALYSIS.normalize_key("Compañía Norte"),
            ANALYSIS.normalize_key("compania norte"),
        )

    def test_computes_statistics_percentages_and_leader(self):
        result = ANALYSIS.analyze(
            {
                "empresas": [
                    {"id": "a", "nombre": "Beta"},
                    {"id": "b", "nombre": "Alfa"},
                    {"id": "c", "nombre": "Gamma"},
                ],
                "retos": [
                    {"id_empresa": "a", "estado": "Abierto"},
                    {"id_empresa": "a", "estado": "Abierto"},
                    {"id_empresa": "a", "estado": "Cerrado"},
                    {"id_empresa": "b", "estado": "Cerrado"},
                ],
            }
        )

        stats = result["estadisticas"]
        self.assertEqual(stats["totalEmpresas"], 3)
        self.assertEqual(stats["empresasConRetos"], 2)
        self.assertEqual(stats["promedioRetos"], 1.33)
        self.assertEqual(stats["medianaRetos"], 1)
        self.assertEqual(stats["desviacionEstandar"], 1.25)
        self.assertEqual(stats["maxRetos"], 3)
        self.assertEqual(
            stats["empresaLider"], {"empresaId": "a", "nombre": "Beta", "retos": 3}
        )
        self.assertEqual(
            [company["empresaId"] for company in result["empresas"]], ["a", "b", "c"]
        )
        self.assertEqual(
            [company["porcentaje"] for company in result["empresas"]], [75.0, 25.0, 0.0]
        )

    def test_companies_with_same_challenges_are_sorted_by_name(self):
        result = ANALYSIS.analyze(
            {
                "empresas": [
                    {"id": "z", "nombre": "Zeta"},
                    {"id": "m", "nombre": "Ómicron"},
                    {"id": "a", "nombre": "alfa"},
                ],
                "retos": [],
            }
        )

        self.assertEqual(
            [company["nombre"] for company in result["empresas"]],
            ["alfa", "Ómicron", "Zeta"],
        )

    def test_skips_companies_without_id(self):
        result = ANALYSIS.analyze(
            {"empresas": [{"id": "  ", "nombre": "Sin ID"}, {"nombre": "Tampoco"}]}
        )

        self.assertEqual(result["empresas"], [])
        self.assertEqual(result["estadisticas"]["totalRetos"], 0)

    def test_main_reads_stdin_and_writes_json(self):
        stdin = io.TextIOWrapper(
            io.BytesIO(
                json.dumps(
                    {"empresas": [{"id": "a", "nombre": "Acme"}], "retos": []}
                ).encode("utf-8")
            )
        )
        stdout = io.TextIOWrapper(io.BytesIO())

        with mock.patch.object(sys, "stdin", stdin), mock.patch.object(sys, "stdout", stdout):
            exit_code = ANALYSIS.main()
            output = json.loads(stdout.buffer.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["empresas"][0]["nombre"], "Acme")

    def test_main_reports_invalid_json_with_exit_code_2(self):
        stdin = io.TextIOWrapper(io.BytesIO(b"esto no es json"))
        stderr = io.StringIO()

        with mock.patch.object(sys, "stdin", stdin), mock.patch.object(sys, "stderr", stderr):
            exit_code = ANALYSIS.main()

        self.assertEqual(exit_code, 2)
        self.assertIn("No se pudo analizar", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
