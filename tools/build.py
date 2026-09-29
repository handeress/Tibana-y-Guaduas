"""Genera index.html (página pública del cliente) a partir de un JSON exportado del maestro.

Uso: python3 tools/build.py datos.json ["Nombre del proyecto"]
datos.json = {"corte": "AAAA-MM-DD", "presupuesto": n,
              "compras": [{"id","fecha","proveedor","concepto","categoria","total","descuento"}],
              "pagos":   [{"compraId","valor"}]}
Solo se publican fecha, concepto, proveedor, frente, valor y pagado.
Nunca se publican referencias bancarias, medios de pago, soportes ni notas internas.
"""
import json, sys, pathlib

FRENTES = {
    "Cubiertas y pérgolas": "Cubierta y pérgola",
    "Materiales": "Baños, cocina y obra gris",
    "Otros gastos": "Otros",
    "Estufas": "Baños, cocina y obra gris",
    "Electricidad e iluminación": "Electricidad e iluminación",
    "Madera": "Carpintería y madera",
    "Cerramientos": "Carpintería y madera",
    "Mobiliario": "Muebles",
    "Metal": "Metal",
    "Mano de obra": "Mano de obra",
}

root = pathlib.Path(__file__).resolve().parent.parent
d = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
DEF = "Tibaná y Guaduas"
PROYECTO = sys.argv[2] if len(sys.argv) > 2 else DEF
# Solo se publica este proyecto; las compras sin campo proyecto pertenecen a Tibaná y Guaduas.
d["compras"] = [c for c in d["compras"] if c.get("proyecto", DEF) == PROYECTO]
ids = {c["id"] for c in d["compras"]}
d["pagos"] = [p for p in d["pagos"] if p["compraId"] in ids]
pagado = {}
for p in d["pagos"]:
    pagado[p["compraId"]] = pagado.get(p["compraId"], 0) + p["valor"]

def fecha(s):
    y, m, dd = s.split("-")
    return f"{dd}/{m}/{y}"

compras = []
for c in sorted(d["compras"], key=lambda x: (x["fecha"], x["id"])):
    compras.append({
        "f": fecha(c["fecha"]),
        "c": c["concepto"],
        "p": c["proveedor"],
        "t": c["total"] - c.get("descuento", 0),
        "pg": pagado.get(c["id"], 0),
        "cat": FRENTES.get(c.get("categoria"), "Otros") if PROYECTO == DEF else {"Otros gastos": "Otros"}.get(c.get("categoria"), c.get("categoria") or "Otros"),
    })

data = {"corte": d["corte"], "presupuesto": d.get("presupuesto"), "compras": compras}
if d.get("presupuestoDetalle"):
    data["presupuestoDetalle"] = d["presupuestoDetalle"]
tpl = (root / "tools" / "template.html").read_text(encoding="utf-8")
out = tpl.replace("__PROYECTO__", PROYECTO).replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
(root / "index.html").write_text(out, encoding="utf-8")
print(f"index.html ({PROYECTO}): {len(compras)} compras, corte {d['corte']}")
