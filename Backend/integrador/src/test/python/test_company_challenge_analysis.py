import importlib.util
import pathlib
import unittest


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


if __name__ == "__main__":
    unittest.main()
