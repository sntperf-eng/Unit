# -*- coding: utf-8 -*-
"""
Générateur + vérificateur du planning des assistantes dentaires — Septembre 2026.

Principe (v2) : TOUT LE MONDE travaille son plein temps. On n'ajoute AUCUN repos
au-delà des jours OFF demandés :
  - Soraya : OFF tous les vendredis (congé parental) et jamais le samedi.
  - Inès  : 1 jour OFF / semaine.
  - Aytana : 1 jour OFF / semaine (toujours différent de celui d'Inès).
  - Laura et Lora travaillent tous les jours ouvrés (lun-ven).
Il peut donc y avoir une assistante « Renfort » en plus certains jours : c'est voulu.

Modèle horaire :
  - Journée complète = 7h36 net (09h00-17h06, 09h30-17h36 ou 10h00-18h06).
  - Lora : 6h48/jour → créneau 09h00-16h18.
  - Samedi : 09h30-13h30 = 4h. Vendredi 25 (exception Dr Rami) : 10h00-13h00 = 3h.
"""
import datetime

ASSISTANTS = ["Laura", "Soraya", "Lora", "Ines", "Aytana"]

HOR = {
    "R": "10h00-18h06", "Z": "09h30-17h36", "M": "09h00-17h06",
    "ACC": "09h00-17h06", "REN": "09h30-17h36", "SAT": "09h30-13h30",
    "RAM_AM": "10h00-13h00",
}
HLABEL = {"R": "Rami", "Z": "Zied", "M": "Majdi", "ACC": "Accueil",
          "REN": "Renfort", "SAT": "Samedi", "RAM_AM": "Rami"}
HOURS = {"R": 7.6, "Z": 7.6, "M": 7.6, "ACC": 7.6, "REN": 7.6,
         "SAT": 4.0, "RAM_AM": 3.0}
LORA_HOR = "09h00-16h18"
LORA_HOURS = 6.8

# --- Présence des dentistes nécessitant une assistante -------------------
def rami_present(d):
    if d == datetime.date(2026, 9, 25):
        return "AM"
    return d.weekday() in (0, 1, 2, 3)

def zied_present(d):
    return d.weekday() in (0, 1, 2, 3, 4)

def majdi_present(d):
    wd, day = d.weekday(), d.day
    if wd == 0:
        return day in (14, 28)
    if wd == 1:
        return False
    if wd == 2:
        return True
    if wd == 3:
        return day in (10, 24)
    if wd == 4:
        return True
    return False

# --- Jours OFF (les SEULS autorisés en dehors des week-ends) --------------
AYTANA_OFF = {datetime.date(2026, 9, x) for x in (4, 10, 16, 22, 28)}
INES_OFF   = {datetime.date(2026, 9, x) for x in (3, 8, 14, 24, 29)}
# Rami confié occasionnellement à Soraya (variété, sans casser les binômes)
SORAYA_RAMI = {15, 17}

SAT = {
    datetime.date(2026, 9, 5): "Laura",
    datetime.date(2026, 9, 12): "Lora",
    datetime.date(2026, 9, 19): "Aytana",
    datetime.date(2026, 9, 26): "Ines",
}

def open_days():
    return [datetime.date(2026, 9, x) for x in range(1, 31)
            if datetime.date(2026, 9, x).weekday() != 6]

def working_today(a, d):
    """Renvoie True si l'assistante a est censée travailler ce jour ouvré."""
    if d.weekday() == 5:               # samedi : uniquement la personne de rotation
        return SAT[d] == a
    if a == "Soraya" and d.weekday() == 4:
        return False                    # congé parental le vendredi
    if a == "Ines" and d in INES_OFF:
        return False
    if a == "Aytana" and d in AYTANA_OFF:
        return False
    return True                         # Laura, Lora, et les autres : plein temps

# --- Construction des affectations ---------------------------------------
def build():
    plan = {}
    acc_count = {a: 0 for a in ASSISTANTS}
    for d in open_days():
        roles = {a: "OFF" for a in ASSISTANTS}

        if d.weekday() == 5:
            roles[SAT[d]] = "SAT"
            plan[d] = roles
            continue

        present = [a for a in ASSISTANTS if working_today(a, d)]
        chair = {}

        # Zied : Aytana, sinon Laura
        if zied_present(d):
            chair["Aytana" if "Aytana" in present else "Laura"] = "Z"

        # Rami : Soraya (occasionnel) / Inès (si Laura déjà chez Zied) / Laura
        # Le 25/09, Rami ne travaille que le matin -> rôle RAM_AM (10h00-13h00).
        if rami_present(d):
            ram = "RAM_AM" if d == datetime.date(2026, 9, 25) else "R"
            if d.day in SORAYA_RAMI and "Soraya" in present:
                chair["Soraya"] = ram
            elif "Laura" in chair:
                chair["Ines"] = ram
            else:
                chair["Laura"] = ram

        # Majdi : Lora
        if majdi_present(d):
            chair["Lora"] = "M"

        # Accueil : parmi les présentes non affectées au fauteuil, la moins chargée
        remaining = [a for a in present if a not in chair]
        pref = {"Soraya": 0, "Ines": 1, "Lora": 2, "Laura": 3, "Aytana": 4}
        remaining.sort(key=lambda a: (acc_count[a], pref[a]))
        acc = remaining[0]
        chair[acc] = "ACC"
        acc_count[acc] += 1

        # Le reste des présentes = Renfort
        for a in remaining[1:]:
            chair[a] = "REN"

        roles.update(chair)
        plan[d] = roles
    return plan

# --- Vérification --------------------------------------------------------
def verify(plan):
    errs = []
    for d in open_days():
        roles = plan[d]
        if d.weekday() == 5:
            present = [a for a, r in roles.items() if r != "OFF"]
            if present != [SAT[d]]:
                errs.append(f"{d}: samedi doit être {SAT[d]} seul, a {present}")
            if roles["Soraya"] != "OFF":
                errs.append(f"{d}: Soraya travaille un samedi")
            continue

        # couverture : chaque dentiste présent + exactement 1 accueil
        if rami_present(d) and "R" not in roles.values() and "RAM_AM" not in roles.values():
            errs.append(f"{d}: Rami présent, non couvert")
        if zied_present(d) and "Z" not in roles.values():
            errs.append(f"{d}: Zied présent, non couvert")
        if majdi_present(d) and "M" not in roles.values():
            errs.append(f"{d}: Majdi présent, non couvert")
        if list(roles.values()).count("ACC") != 1:
            errs.append(f"{d}: il faut exactement 1 accueil")

        # présences attendues = plein temps sauf jours OFF autorisés
        for a in ASSISTANTS:
            should = working_today(a, d)
            works = roles[a] != "OFF"
            if should != works:
                errs.append(f"{d}: {a} devrait {'travailler' if should else 'être OFF'}")

        # binômes habituels
        for a, r in roles.items():
            if r in ("R", "RAM_AM") and a not in ("Laura", "Ines", "Soraya"):
                errs.append(f"{d}: {a} avec Rami (habitude La/In/So)")
            if r == "Z" and a not in ("Aytana", "Laura"):
                errs.append(f"{d}: {a} avec Zied (habitude Ay/La)")
            if r == "M" and a != "Lora":
                errs.append(f"{d}: {a} avec Majdi (habitude Lora)")

    if AYTANA_OFF & INES_OFF:
        errs.append("Inès et Aytana partagent un jour OFF")

    # 1 jour OFF / semaine pour Inès et Aytana
    for wk in sorted({d.isocalendar()[1] for d in open_days()}):
        wdays = [d for d in open_days() if d.isocalendar()[1] == wk and d.weekday() < 5]
        if not wdays:
            continue
        for name, offs in (("Ines", INES_OFF), ("Aytana", AYTANA_OFF)):
            n = len([d for d in wdays if d in offs])
            if n != 1 and len(wdays) >= 4:
                errs.append(f"S{wk} {name}: {n} jour(s) OFF (attendu 1)")

    for d in open_days():
        if majdi_present(d) and plan[d]["Lora"] != "M":
            errs.append(f"{d}: Majdi présent mais Lora non affectée")
    return errs

# --- Récapitulatif -------------------------------------------------------
def recap(plan):
    keys = ("jours", "heures", "acc", "rami", "zied", "majdi", "ren", "sam")
    stats = {a: {k: 0 for k in keys} for a in ASSISTANTS}
    for a in ASSISTANTS:
        stats[a]["heures"] = 0.0
    for d in open_days():
        for a, r in plan[d].items():
            if r == "OFF":
                continue
            s = stats[a]
            s["jours"] += 1
            s["heures"] += LORA_HOURS if (a == "Lora" and r != "SAT") else HOURS[r]
            if r == "ACC": s["acc"] += 1
            if r in ("R", "RAM_AM"): s["rami"] += 1
            if r == "Z": s["zied"] += 1
            if r == "M": s["majdi"] += 1
            if r == "REN": s["ren"] += 1
            if r == "SAT": s["sam"] += 1
    return stats

def hhmm(h):
    m = round(h * 60)
    return f"{m//60}h{m%60:02d}"

JOURS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

# --- Rendu Markdown ------------------------------------------------------
def cell(a, r):
    if r == "OFF":
        return "OFF"
    if r == "SAT":
        return f"{HOR['SAT']} — Samedi"
    time = LORA_HOR if (a == "Lora" and r != "SAT") else HOR[r]
    suffix = " (matin)" if r == "RAM_AM" else ""
    return f"{time} — {HLABEL[r]}{suffix}"

def render(plan, stats, errs):
    disp = {"Ines": "Inès"}
    out = ["# Planning des assistantes dentaires — Septembre 2026\n"]
    out.append("_Cabinet ouvert du lundi au samedi (fermé le dimanche). "
               "Samedi : matin uniquement (09h30-13h30), une seule assistante._\n")
    out.append("| Date | Jour | Laura | Soraya | Lora | Inès | Aytana |")
    out.append("|------|------|-------|--------|------|------|--------|")
    for d in open_days():
        row = [f"{d.day:02d}/09", JOURS_FR[d.weekday()]]
        for a in ["Laura", "Soraya", "Lora", "Ines", "Aytana"]:
            row.append(cell(a, plan[d][a]))
        out.append("| " + " | ".join(row) + " |")
    out.append("\n## Récapitulatif par assistante\n")
    out.append("| Assistante | Jours | Heures | Accueil | Rami | Zied | Majdi | Renfort | Samedis |")
    out.append("|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")
    for a in ["Laura", "Soraya", "Lora", "Ines", "Aytana"]:
        s = stats[a]
        out.append(f"| {disp.get(a,a)} | {s['jours']} | {hhmm(s['heures'])} | "
                   f"{s['acc']} | {s['rami']} | {s['zied']} | {s['majdi']} | "
                   f"{s['ren']} | {s['sam']} |")
    out.append("\n## Vérification automatique des contraintes\n")
    out.append("✅ **Toutes les contraintes sont respectées.**" if not errs
               else "❌ Anomalies :\n" + "\n".join(f"- {e}" for e in errs))
    out.append("\n## Règles appliquées\n")
    out.append("- **Plein temps pour toutes** : aucun repos ajouté hors des jours OFF "
               "demandés. Une assistante peut être en **Renfort** (soutien polyvalent) "
               "en plus les jours bien pourvus — c'est assumé.")
    out.append("- **Jours OFF** : Soraya tous les vendredis + samedis ; Aytana les 04, "
               "10, 16, 22, 28/09 ; Inès les 03, 08, 14, 24, 29/09 (toujours distincts).")
    out.append("- **Binômes** : Laura↔Rami, Aytana↔Zied, Lora↔Majdi (les 13 jours de Majdi). "
               "Le jour OFF d'Aytana, Laura passe chez Zied et Inès prend Rami.")
    out.append("- **Samedis** : Laura (05), Lora (12), Aytana (19), Inès (26).")
    return "\n".join(out)

# --- Rendu HTML ----------------------------------------------------------
ROLE_CLASS = {"R": "rami", "Z": "zied", "M": "majdi", "ACC": "accueil",
              "REN": "renfort", "SAT": "samedi", "RAM_AM": "rami"}
ROLE_NAME = {"R": "Dr Rami", "Z": "Dr Zied", "M": "Dr Majdi", "ACC": "Accueil",
             "REN": "Renfort", "SAT": "Samedi", "RAM_AM": "Dr Rami"}
DOMINANT = {"Laura": ("rami", "Dr Rami"), "Soraya": ("accueil", "Accueil"),
            "Lora": ("majdi", "Dr Majdi"), "Ines": ("accueil", "Accueil"),
            "Aytana": ("zied", "Dr Zied")}
CONTRAT = {"Laura": "38h", "Soraya": "38h", "Lora": "34h",
           "Ines": "30h", "Aytana": "30h"}

def html_cell(a, r):
    if r == "OFF":
        return '<td class="c"><span class="off">Repos</span></td>'
    cls, name = ROLE_CLASS[r], ROLE_NAME[r]
    time = LORA_HOR if (a == "Lora" and r != "SAT") else HOR[r]
    tag = ' <span class="tag">matin</span>' if r == "RAM_AM" else ""
    return (f'<td class="c"><span class="chip {cls}">'
            f'<span class="role">{name}{tag}</span>'
            f'<span class="time">{time}</span></span></td>')

def render_html(plan, stats, errs):
    disp = {"Ines": "Inès"}
    weeks = []
    for d in open_days():
        wk = d.isocalendar()[1]
        if not weeks or weeks[-1][0] != wk:
            weeks.append((wk, []))
        weeks[-1][1].append(d)
    rows = []
    for i, (wk, wdays) in enumerate(weeks, 1):
        rows.append(f'<tr class="wk"><td colspan="6">Semaine {i} · '
                    f'{wdays[0].day} → {wdays[-1].day} septembre</td></tr>')
        for d in wdays:
            sat = " sat" if d.weekday() == 5 else ""
            rows.append(f'<tr class="day{sat}">')
            rows.append(f'<th scope="row" class="date"><span class="dwrap">'
                        f'<span class="d">{d.day:02d}</span>'
                        f'<span class="j">{JOURS_FR[d.weekday()][:3].lower()}.</span>'
                        f'</span></th>')
            for a in ["Laura", "Soraya", "Lora", "Ines", "Aytana"]:
                rows.append(html_cell(a, plan[d][a]))
            rows.append("</tr>")
    cards = []
    for a in ["Laura", "Soraya", "Lora", "Ines", "Aytana"]:
        s = stats[a]
        cls, _ = DOMINANT[a]
        items = [("Jours", s["jours"]), ("Heures", hhmm(s["heures"])),
                 ("Accueil", s["acc"]), ("Rami", s["rami"]), ("Zied", s["zied"]),
                 ("Majdi", s["majdi"]), ("Renfort", s["ren"]), ("Samedis", s["sam"])]
        grid = "".join(f'<div class="st"><span class="v">{v}</span>'
                       f'<span class="k">{k}</span></div>' for k, v in items)
        cards.append(f'''<article class="card {cls}">
  <header><h3>{disp.get(a,a)}</h3>
  <p class="sub">Contrat {CONTRAT[a]}/sem · réalisé ~{hhmm(s["heures"]/4.3)}/sem</p></header>
  <div class="stats">{grid}</div>
</article>''')
    check = ("Toutes les contraintes sont respectées" if not errs
             else f"{len(errs)} anomalie(s) — voir le fichier source")
    legend = "".join(f'<span class="lg {c}"><span class="dot"></span>{n}</span>'
                     for c, n in [("rami", "Dr Rami"), ("zied", "Dr Zied"),
                                  ("majdi", "Dr Majdi"), ("accueil", "Accueil"),
                                  ("renfort", "Renfort"), ("samedi", "Samedi"),
                                  ("off", "Repos")])
    head = ('<th class="date">Date</th>' + "".join(
        f'<th class="{DOMINANT[a][0]}">{disp.get(a,a)}</th>'
        for a in ["Laura", "Soraya", "Lora", "Ines", "Aytana"]))
    return f'''<title>Planning cabinet dentaire — Septembre 2026</title>
<style>{CSS}</style>
<main>
  <header class="mast">
    <p class="eyebrow">Cabinet dentaire · Assistantes</p>
    <h1>Planning — Septembre 2026</h1>
    <p class="lede">Cinq assistantes à plein temps, du lundi au samedi. Chaque
      dentiste présent (Rami, Zied, Majdi) a son assistante&nbsp;; une personne
      tient l'accueil, une autre vient en <strong>renfort</strong> les jours bien
      pourvus. Le Dr Emine travaille sans assistante.</p>
    <div class="legend">{legend}</div>
  </header>
  <div class="scroll">
    <table class="grid">
      <thead><tr>{head}</tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
  <section class="recap">
    <h2>Récapitulatif du mois</h2>
    <div class="cards">{''.join(cards)}</div>
  </section>
  <section class="notes">
    <p class="ok"><span class="check">✓</span> {check}
      <span class="muted">— vérifié automatiquement (couverture, binômes
      habituels, jours OFF distincts Inès/Aytana, Soraya jamais vendredi ni
      samedi, rotation des samedis, exception Dr Rami du 25/09).</span></p>
    <p class="muted small">Toutes les assistantes travaillent leur plein temps :
      aucun repos n'est ajouté hors des jours OFF demandés. Les jours bien pourvus,
      une assistante est en <strong>Renfort</strong> (soutien polyvalent) — c'est
      assumé. Journée = 7h36 net ; Lora 6h48 (09h00-16h18) ; samedi 4h ;
      25/09 Dr Rami 10h00-13h00. Le contrat 38h de Soraya reste limité par le
      congé parental du vendredi et l'absence le samedi.</p>
  </section>
</main>'''

CSS = r"""
* { box-sizing: border-box; }
:root {
  --bg:#f3f5f8; --surface:#ffffff; --surface-2:#f7f9fc; --border:#e2e6ee;
  --text:#1f2733; --muted:#697386; --heading:#141b26;
  --c-rami:#4f46e5; --c-zied:#0f766e; --c-majdi:#b45309;
  --c-accueil:#be185d; --c-renfort:#7c3aed; --c-samedi:#15803d; --c-off:#94a0b3;
  --band:#eef1f6;
  --font:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg:#0e131b; --surface:#161d28; --surface-2:#131a24; --border:#26303f;
    --text:#dce3ec; --muted:#8b97a8; --heading:#f0f4f9;
    --c-rami:#a5b4fc; --c-zied:#5eead4; --c-majdi:#fcd34d;
    --c-accueil:#f9a8d4; --c-renfort:#c4b5fd; --c-samedi:#86efac; --c-off:#5c6779;
    --band:#1b2330;
  }
}
:root[data-theme="light"] {
  --bg:#f3f5f8; --surface:#ffffff; --surface-2:#f7f9fc; --border:#e2e6ee;
  --text:#1f2733; --muted:#697386; --heading:#141b26;
  --c-rami:#4f46e5; --c-zied:#0f766e; --c-majdi:#b45309;
  --c-accueil:#be185d; --c-renfort:#7c3aed; --c-samedi:#15803d; --c-off:#94a0b3; --band:#eef1f6;
}
:root[data-theme="dark"] {
  --bg:#0e131b; --surface:#161d28; --surface-2:#131a24; --border:#26303f;
  --text:#dce3ec; --muted:#8b97a8; --heading:#f0f4f9;
  --c-rami:#a5b4fc; --c-zied:#5eead4; --c-majdi:#fcd34d;
  --c-accueil:#f9a8d4; --c-renfort:#c4b5fd; --c-samedi:#86efac; --c-off:#5c6779; --band:#1b2330;
}
body { margin:0; background:var(--bg); color:var(--text);
  font-family:var(--font); line-height:1.5; -webkit-font-smoothing:antialiased; }
main { max-width:1160px; margin:0 auto; padding:clamp(20px,4vw,52px) clamp(16px,3vw,32px) 64px; }
.mast { margin-bottom:28px; }
.eyebrow { text-transform:uppercase; letter-spacing:.14em; font-size:.72rem;
  font-weight:600; color:var(--c-rami); margin:0 0 10px; }
h1 { font-family:var(--serif); font-weight:600; letter-spacing:-.01em;
  font-size:clamp(1.9rem,4.5vw,3rem); line-height:1.05; margin:0 0 12px;
  color:var(--heading); text-wrap:balance; }
.lede { max-width:64ch; color:var(--muted); font-size:1.02rem; margin:0 0 22px; }
.lede strong { color:var(--c-renfort); font-weight:600; }
.legend { display:flex; flex-wrap:wrap; gap:8px 16px; align-items:center; }
.lg { display:inline-flex; align-items:center; gap:7px; font-size:.82rem;
  color:var(--muted); font-weight:500; }
.lg .dot { width:11px; height:11px; border-radius:3px;
  background:color-mix(in srgb, var(--role) 22%, var(--surface));
  border-left:3px solid var(--role); }
.lg.rami{--role:var(--c-rami)} .lg.zied{--role:var(--c-zied)}
.lg.majdi{--role:var(--c-majdi)} .lg.accueil{--role:var(--c-accueil)}
.lg.renfort{--role:var(--c-renfort)} .lg.samedi{--role:var(--c-samedi)} .lg.off{--role:var(--c-off)}
.scroll { overflow-x:auto; border:1px solid var(--border); border-radius:14px;
  background:var(--surface); box-shadow:0 1px 2px rgba(20,27,38,.04); }
table.grid { border-collapse:collapse; width:100%; min-width:760px; }
.grid thead th { position:sticky; top:0; z-index:3; background:var(--surface);
  text-align:left; font-size:.82rem; font-weight:600; color:var(--heading);
  padding:14px 12px; border-bottom:1px solid var(--border);
  box-shadow:inset 0 -2px 0 color-mix(in srgb, var(--role,transparent) 55%, transparent); }
.grid thead th.rami{--role:var(--c-rami)} .grid thead th.zied{--role:var(--c-zied)}
.grid thead th.majdi{--role:var(--c-majdi)} .grid thead th.accueil{--role:var(--c-accueil)}
.grid thead th.date{ box-shadow:none; }
.grid th.date { width:64px; }
.grid tr.wk td { background:var(--band); color:var(--muted); z-index:1;
  font-size:.74rem; font-weight:600; letter-spacing:.06em; text-transform:uppercase;
  padding:8px 14px; border-bottom:1px solid var(--border); }
.grid td, .grid th.date { padding:7px 10px; border-bottom:1px solid var(--border);
  vertical-align:middle; }
.grid tr.day:hover td, .grid tr.day:hover th.date { background:var(--surface-2); }
.grid th.date { position:sticky; left:0; z-index:2; background:var(--surface); }
.dwrap { display:flex; align-items:baseline; gap:6px; }
.date .d { font-size:1.05rem; font-weight:700; color:var(--heading);
  font-variant-numeric:tabular-nums; }
.date .j { font-size:.72rem; color:var(--muted); }
tr.sat th.date .d { color:var(--c-samedi); }
.chip { display:flex; flex-direction:column; gap:1px; padding:6px 9px;
  border-radius:8px; border-left:3px solid var(--role);
  background:color-mix(in srgb, var(--role) 12%, var(--surface)); min-width:104px; }
.chip.rami{--role:var(--c-rami)} .chip.zied{--role:var(--c-zied)}
.chip.majdi{--role:var(--c-majdi)} .chip.accueil{--role:var(--c-accueil)}
.chip.renfort{--role:var(--c-renfort)} .chip.samedi{--role:var(--c-samedi)}
.chip .role { font-size:.83rem; font-weight:600; color:var(--role); }
.chip .time { font-size:.72rem; color:var(--muted); font-variant-numeric:tabular-nums; }
.chip .tag { font-size:.62rem; font-weight:600; text-transform:uppercase;
  letter-spacing:.05em; color:var(--muted); }
.off { font-size:.78rem; color:var(--c-off); font-style:italic; padding-left:3px; }
.recap { margin-top:40px; }
.recap h2, .notes h2 { font-family:var(--serif); font-weight:600;
  font-size:1.5rem; color:var(--heading); margin:0 0 18px; }
.cards { display:grid; gap:14px; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); }
.card { background:var(--surface); border:1px solid var(--border);
  border-radius:14px; padding:16px 16px 14px; border-top:3px solid var(--role); }
.card.rami{--role:var(--c-rami)} .card.zied{--role:var(--c-zied)}
.card.majdi{--role:var(--c-majdi)} .card.accueil{--role:var(--c-accueil)}
.card h3 { margin:0; font-size:1.15rem; color:var(--heading); }
.card .sub { margin:3px 0 12px; font-size:.76rem; color:var(--muted); }
.card .stats { display:grid; grid-template-columns:repeat(4,1fr); gap:9px 6px; }
.st { display:flex; flex-direction:column; }
.st .v { font-size:1.05rem; font-weight:700; color:var(--text);
  font-variant-numeric:tabular-nums; line-height:1.1; }
.st .k { font-size:.64rem; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); }
.notes { margin-top:36px; display:flex; flex-direction:column; gap:10px; }
.ok { font-size:.95rem; margin:0; }
.check { display:inline-grid; place-items:center; width:20px; height:20px;
  border-radius:50%; background:color-mix(in srgb,var(--c-samedi) 20%,transparent);
  color:var(--c-samedi); font-weight:700; font-size:.8rem; margin-right:6px; vertical-align:-2px; }
.muted { color:var(--muted); } .small { font-size:.82rem; line-height:1.55; }
.small strong { color:var(--c-renfort); }
@media (prefers-reduced-motion:reduce){ *{scroll-behavior:auto} }
"""

if __name__ == "__main__":
    plan = build()
    errs = verify(plan)
    stats = recap(plan)
    with open("planning-septembre-2026.md", "w") as f:
        f.write(render(plan, stats, errs) + "\n")
    with open("planning-septembre-2026.html", "w") as f:
        f.write(render_html(plan, stats, errs) + "\n")
    print("ERREURS:", errs if errs else "aucune")
    for a in ASSISTANTS:
        s = stats[a]
        print(f"{a:8} {s['jours']:2}j {hhmm(s['heures']):>7}  acc{s['acc']} "
              f"R{s['rami']} Z{s['zied']} M{s['majdi']} ren{s['ren']} sam{s['sam']}")
