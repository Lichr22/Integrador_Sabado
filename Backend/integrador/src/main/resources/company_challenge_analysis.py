import json
import re
import statistics
import sys
import unicodedata


def clean_text(value):
    if value is None:
        return ""
    normalized = str(value)
    for _ in range(2):
        if not any(marker in normalized for marker in ("Ã", "Â", "â€")):
            break
        try:
            repaired = normalized.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if repaired == normalized:
            break
        normalized = repaired
    normalized = unicodedata.normalize("NFKC", normalized)
    normalized = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Cf"
    )
    return re.sub(r"\s+", " ", normalized).strip()


def normalize_key(value):
    normalized = unicodedata.normalize("NFKD", clean_text(value).casefold())
    return "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )


def analyze(payload):
    companies = {}
    for company in payload.get("empresas", []):
        company_id = str(company.get("id", "")).strip()
        if not company_id:
            continue

        raw_name = company.get("nombre")
        name = clean_text(raw_name)
        if not name:
            name = f"Empresa sin nombre ({company_id[:8]})"
        companies[company_id] = {
            "empresaId": company_id,
            "nombre": name,
            "retos": 0,
            "retosAbiertos": 0,
            "nombreCorregido": name != (str(raw_name) if raw_name is not None else ""),
        }

    unassigned_challenges = 0
    total_challenges = 0
    open_challenges = 0
    for challenge in payload.get("retos", []):
        total_challenges += 1
        company_id = str(challenge.get("id_empresa") or "").strip()
        company = companies.get(company_id)
        if company is None:
            unassigned_challenges += 1
            continue

        company["retos"] += 1
        if normalize_key(challenge.get("estado")) == "abierto":
            company["retosAbiertos"] += 1
            open_challenges += 1

    company_rows = list(companies.values())
    counts = [company["retos"] for company in company_rows]
    normalized_names = {}
    for company in company_rows:
        normalized_names.setdefault(normalize_key(company["nombre"]), []).append(
            company["empresaId"]
        )
    duplicate_name_groups = [
        ids for ids in normalized_names.values() if len(ids) > 1
    ]

    company_rows.sort(
        key=lambda company: (
            -company["retos"],
            normalize_key(company["nombre"]),
            company["empresaId"],
        )
    )
    for company in company_rows:
        company["porcentaje"] = (
            round(company["retos"] * 100 / total_challenges, 1)
            if total_challenges
            else 0.0
        )

    leading_company = company_rows[0] if company_rows and company_rows[0]["retos"] else None
    return {
        "empresas": company_rows,
        "estadisticas": {
            "totalRetos": total_challenges,
            "retosAbiertos": open_challenges,
            "totalEmpresas": len(company_rows),
            "empresasConRetos": sum(count > 0 for count in counts),
            "empresasSinRetos": sum(count == 0 for count in counts),
            "promedioRetos": round(statistics.mean(counts), 2) if counts else 0,
            "medianaRetos": statistics.median(counts) if counts else 0,
            "desviacionEstandar": round(statistics.pstdev(counts), 2) if counts else 0,
            "maxRetos": max(counts, default=0),
            "empresaLider": (
                {
                    "empresaId": leading_company["empresaId"],
                    "nombre": leading_company["nombre"],
                    "retos": leading_company["retos"],
                }
                if leading_company
                else None
            ),
            "retosSinEmpresa": unassigned_challenges,
            "nombresCorregidos": sum(
                company["nombreCorregido"] for company in company_rows
            ),
            "gruposConNombreDuplicado": len(duplicate_name_groups),
        },
    }


def main():
    try:
        result = analyze(json.load(sys.stdin.buffer))
        output = json.dumps(result, ensure_ascii=False, allow_nan=False).encode("utf-8")
        sys.stdout.buffer.write(output + b"\n")
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"No se pudo analizar la distribución de retos: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
