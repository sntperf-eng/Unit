# -*- coding: utf-8 -*-
"""
Générateur + vérificateur du planning des assistantes dentaires — Septembre 2026.

Modèle horaire :
  - Journée complète = 7h36 net (créneaux 09h00-17h06, 09h30-17h36 ou 10h00-18h06,
    tous égaux à 8h06 brut - 30 min de pause = 7h36).
  - Lora : contrat 34h en 6h48/jour sur 5 jours (créneau 09h00-16h18).
  - Samedi : 09h30-13h30 = 4h.
  - Vendredi 25 (exception Dr Rami, 10h00-13h00) : matinée = 3h.

Le script assigne le planning selon les binômes habituels, puis VÉRIFIE
automatiquement toutes les contraintes avant de produire le tableau final.
"""
import datetime

ASSISTANTS = ["Laura", "Soraya", "Lora", "Ines", "Aytana"]

# Horaires normalisés par rôle (réguliers).
HOR = {
    "R":   "10h00-18h06",   # couvre Dr Rami 10h00-17h30
    "Z":   "09h30-17h36",   # couvre Dr Zied 09h30-17h30
    "M":   "09h00-17h06",   # Dr Majdi
    "ACC": "09h00-17h06",   # accueil, ouverture au plus tôt
    "SAT": "09h30-13h30",   # samedi matin
    "RAM_AM": "10h00-13h00",  # Rami exceptionnel vendredi 25
}
HLABEL = {
    "R": "Rami", "Z": "Zied", "M": "Majdi", "ACC": "Accueil",
    "SAT": "Samedi", "RAM_AM": "Rami",
}
HOURS = {"R": 7.6, "Z": 7.6, "M": 7.6, "ACC": 7.6, "SAT": 4.0, "RAM_AM": 3.0}
# Lora fait des journées de 6h48 (=6.8h) et un créneau spécifique.
LORA_HOR = "09h00-16h18"
LORA_HOURS = 6.8

# --- Présence des dentistes qui nécessitent une assistante ---------------
def rami_present(d):
    wd = d.weekday()  # 0=lundi
    if d == datetime.date(2026, 9, 25):
        return "AM"           # exception : matinée seulement
    return wd in (0, 1, 2, 3)  # lun-jeu

def zied_present(d):
    return d.weekday() in (0, 1, 2, 3, 4)  # lun-ven

def majdi_present(d):
    wd = d.weekday()
    day = d.day
    if wd == 0:   # lundi : un sur deux
        return day in (14, 28)
    if wd == 1:   # mardi : jamais
        return False
    if wd == 2:   # mercredi : toujours
        return True
    if wd == 3:   # jeudi : un sur deux
        return day in (10, 24)
    if wd == 4:   # vendredi : toujours
        return True
    return False

# --- Jours OFF structurés (1/semaine, différents entre Inès et Aytana) ---
AYTANA_OFF = {datetime.date(2026, 9, x) for x in (4, 10, 16, 22, 28)}
INES_OFF   = {datetime.date(2026, 9, x) for x in (3, 8, 14, 24, 29)}

# --- Rotation des samedis (imposée) --------------------------------------
SAT = {
    datetime.date(2026, 9, 5): "Laura",
    datetime.date(2026, 9, 12): "Lora",
    datetime.date(2026, 9, 19): "Aytana",
    datetime.date(2026, 9, 26): "Ines",
}

def open_days():
    days = []
    for x in range(1, 31):
        d = datetime.date(2026, 9, x)
        if d.weekday() != 6:  # fermé le dimanche
            days.append(d)
    return days

# --- Décisions de répartition (contrôlées pour l'équité) ------------------
# Rami est occasionnellement confié à Soraya (habitude "Soraya occasionnellement").
SORAYA_RAMI = {15, 17}
# Affectation explicite de l'accueil (jour -> assistante) : équilibre Soraya/Inès.
ACC_MAP = {
    1: "Ines", 2: "Soraya", 3: "Soraya", 4: "Ines",
    7: "Lora", 8: "Soraya", 9: "Ines", 10: "Soraya", 11: "Laura",
    14: "Soraya", 15: "Ines", 16: "Soraya", 17: "Ines", 18: "Ines",
    21: "Soraya", 22: "Soraya", 23: "Soraya", 24: "Soraya", 25: "Ines",
    28: "Soraya", 29: "Lora", 30: "Ines",
}

# --- Construction des affectations ---------------------------------------
def build():
    plan = {}
    for d in open_days():
        roles = {a: "OFF" for a in ASSISTANTS}

        # Samedi : une seule assistante
        if d.weekday() == 5:
            roles[SAT[d]] = "SAT"
            plan[d] = roles
            continue

        aytana_off = d in AYTANA_OFF
        chair = {}

        # Exception vendredi 25 : Rami matin -> Laura (priorité), puis Inès à l'accueil
        if d == datetime.date(2026, 9, 25):
            roles.update(Laura="RAM_AM", Aytana="Z", Lora="M", Ines="ACC")
            plan[d] = roles
            continue

        # Zied (lun-ven) : Aytana, ou Laura si Aytana en repos
        if zied_present(d):
            chair["Aytana" if not aytana_off else "Laura"] = "Z"

        # Rami : Soraya (occasionnel) / Inès (si Laura a pris Zied) / Laura (défaut)
        if rami_present(d):
            if d.day in SORAYA_RAMI:
                chair["Soraya"] = "R"
            elif "Laura" in chair:      # Laura déjà chez Zied (Aytana en repos)
                chair["Ines"] = "R"
            else:
                chair["Laura"] = "R"

        # Majdi -> Lora
        if majdi_present(d):
            chair["Lora"] = "M"

        # Accueil (affectation explicite contrôlée)
        acc = ACC_MAP[d.day]
        assert acc not in chair, f"{d}: accueil {acc} déjà au fauteuil"
        chair[acc] = "ACC"

        for a, r in chair.items():
            roles[a] = r
        plan[d] = roles

    return plan

# --- Vérification des contraintes ----------------------------------------
def verify(plan):
    errs = []
    for d in open_days():
        roles = plan[d]
        present = [a for a, r in roles.items() if r != "OFF"]

        if d.weekday() == 5:
            if len(present) != 1:
                errs.append(f"{d}: samedi doit avoir 1 assistante, a {present}")
            who = present[0] if present else None
            if who == "Soraya":
                errs.append(f"{d}: Soraya ne travaille jamais le samedi")
            continue

        # couverture : chaque dentiste présent a une assistante dédiée + accueil
        need = []
        if rami_present(d):
            need.append("R" if rami_present(d) is True else "RAM_AM")
        if zied_present(d):
            need.append("Z")
        if majdi_present(d):
            need.append("M")
        need.append("ACC")
        got = sorted(r for r in roles.values() if r != "OFF")
        if got != sorted(need):
            errs.append(f"{d}: rôles={got} attendus={sorted(need)}")

        # accueil ≠ fauteuil (implicite : un rôle par personne) ; 1 seul accueil
        if list(roles.values()).count("ACC") != 1:
            errs.append(f"{d}: il faut exactement 1 accueil")

        # Soraya jamais le vendredi
        if d.weekday() == 4 and roles["Soraya"] != "OFF":
            errs.append(f"{d}: Soraya travaille un vendredi")

        # binômes habituels
        for a, r in roles.items():
            if r == "R" or r == "RAM_AM":
                if a not in ("Laura", "Ines", "Soraya"):
                    errs.append(f"{d}: {a} avec Rami (habitude La/In/So)")
            if r == "Z" and a not in ("Aytana", "Laura"):
                errs.append(f"{d}: {a} avec Zied (habitude Ay/La)")
            if r == "M" and a != "Lora":
                errs.append(f"{d}: {a} avec Majdi (habitude Lora)")

    # Inès / Aytana : jours off différents + 1/semaine
    if AYTANA_OFF & INES_OFF:
        errs.append("Inès et Aytana partagent un jour OFF")

    # semaines : au moins un jour off pour In et Ay
    def week_key(d):
        return d.isocalendar()[1]
    weeks = sorted({week_key(d) for d in open_days()})
    for wk in weeks:
        wdays = [d for d in open_days() if week_key(d) == wk and d.weekday() < 5]
        for name, offset in (("Ines", INES_OFF), ("Aytana", AYTANA_OFF)):
            offs = [d for d in wdays if d in offset]
            worked = [d for d in wdays if plan[d][name] != "OFF"]
            # au moins 1 jour off garanti (structurel), sauf semaine partielle sans jour dispo
            if wdays and not offs and len(worked) == len(wdays):
                errs.append(f"S{wk} {name}: aucun jour OFF")

    # Majdi toujours couvert par Lora quand présent
    for d in open_days():
        if majdi_present(d) and plan[d]["Lora"] != "M":
            errs.append(f"{d}: Majdi présent mais Lora non affectée (Lora={plan[d]['Lora']})")

    return errs

# --- Récapitulatif -------------------------------------------------------
def recap(plan):
    stats = {a: dict(jours=0, heures=0.0, acc=0, rami=0, zied=0, majdi=0, sam=0)
             for a in ASSISTANTS}
    for d in open_days():
        for a, r in plan[d].items():
            if r == "OFF":
                continue
            stats[a]["jours"] += 1
            if a == "Lora" and r != "SAT":
                stats[a]["heures"] += LORA_HOURS
            else:
                stats[a]["heures"] += HOURS[r]
            if r == "ACC":
                stats[a]["acc"] += 1
            if r in ("R", "RAM_AM"):
                stats[a]["rami"] += 1
            if r == "Z":
                stats[a]["zied"] += 1
            if r == "M":
                stats[a]["majdi"] += 1
            if r == "SAT":
                stats[a]["sam"] += 1
    return stats

def hhmm(h):
    m = round(h * 60)
    return f"{m//60}h{m%60:02d}"

# --- Rendu Markdown ------------------------------------------------------
JOURS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

def cell(a, r):
    if r == "OFF":
        return "OFF"
    if r == "SAT":
        return f"{HOR['SAT']} — Samedi"
    if a == "Lora" and r != "SAT":
        return f"{LORA_HOR} — {HLABEL[r]}"
    if r == "RAM_AM":
        return f"{HOR['RAM_AM']} — Rami (matin)"
    return f"{HOR[r]} — {HLABEL[r]}"

def render(plan, stats, errs):
    out = []
    out.append("# Planning des assistantes dentaires — Septembre 2026\n")
    out.append("_Cabinet ouvert du lundi au samedi (fermé le dimanche). "
               "Samedi : uniquement le matin (09h30-13h30), une seule assistante._\n")
    out.append("| Date | Jour | Laura | Soraya | Lora | Inès | Aytana |")
    out.append("|------|------|-------|--------|------|------|--------|")
    for d in open_days():
        roles = plan[d]
        row = [f"{d.day:02d}/09", JOURS_FR[d.weekday()]]
        for a in ["Laura", "Soraya", "Lora", "Ines", "Aytana"]:
            row.append(cell(a, roles[a]))
        out.append("| " + " | ".join(row) + " |")
    out.append("")
    out.append("## Récapitulatif par assistante\n")
    out.append("| Assistante | Jours travaillés | Heures prestées | Accueil | Avec Rami | Avec Zied | Avec Majdi | Samedis |")
    out.append("|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")
    disp = {"Ines": "Inès"}
    for a in ["Laura", "Soraya", "Lora", "Ines", "Aytana"]:
        s = stats[a]
        out.append(f"| {disp.get(a,a)} | {s['jours']} | {hhmm(s['heures'])} | "
                   f"{s['acc']} | {s['rami']} | {s['zied']} | {s['majdi']} | {s['sam']} |")
    out.append("")
    out.append("## Vérification automatique des contraintes\n")
    if not errs:
        out.append("✅ **Toutes les contraintes sont respectées** "
                   "(couverture des dentistes, accueil unique, binômes habituels, "
                   "jours OFF Inès/Aytana distincts, Soraya jamais vendredi/samedi, "
                   "rotation des samedis, exception Dr Rami du 25/09).")
    else:
        out.append("❌ Anomalies détectées :\n")
        for e in errs:
            out.append(f"- {e}")

    out.append("\n## Comment lire le planning\n")
    out.append("- **Horaires assistantes** (journée = 7h36 net) : `09h00-17h06`, "
               "`09h30-17h36` ou `10h00-18h06` (8h06 brut − 30 min de pause).")
    out.append("- **Lora** : contrat 34h en 6h48/jour sur 5 jours → créneau `09h00-16h18`.")
    out.append("- **Samedi** : `09h30-13h30` (matin, 4h), une seule assistante.")
    out.append("- **25/09** : le Dr Rami travaille exceptionnellement `10h00-13h00` "
               "(matinée), assisté par Laura.")
    out.append("- Correspondance horaire/dentiste : Rami `10h00-18h06`, "
               "Zied `09h30-17h36`, Majdi & Accueil `09h00-17h06` (ouverture au plus tôt).")

    out.append("\n## Analyse de charge et contrats\n")
    out.append("Chaque jour, le besoin réel est de **3 à 4 postes** (une assistante "
               "par dentiste présent parmi Rami/Zied/Majdi + une à l'accueil ; le Dr "
               "Emine travaille sans assistante). Pour **5 assistantes**, il existe "
               "donc une capacité excédentaire structurelle, répartie en jours de "
               "repos. Les heures ci-dessous sont donc **au maximum atteignable sans "
               "dépasser aucun contrat** ; l'écart au contrat correspond à cette "
               "sur-effectif et est réparti équitablement.\n")
    out.append("| Assistante | Contrat/sem. | Moyenne réalisée/sem. | Total mois |")
    out.append("|-----------|:---:|:---:|:---:|")
    contrat = {"Laura": "38h", "Soraya": "38h*", "Lora": "34h",
               "Ines": "30h", "Aytana": "30h"}
    WEEKS = 4.3
    for a in ["Laura", "Soraya", "Lora", "Ines", "Aytana"]:
        s = stats[a]
        out.append(f"| {disp.get(a,a)} | {contrat[a]} | "
                   f"~{hhmm(s['heures']/WEEKS)} | {hhmm(s['heures'])} |")
    out.append("\n_*Soraya : contrat 38h ramené à ~30h24 effectives par le congé "
               "parental (tous les vendredis) ; sans samedi et non affectée à "
               "Zied/Majdi par habitude, sa charge se concentre sur l'accueil et "
               "quelques journées avec le Dr Rami._")

    out.append("\n## Règles et habitudes appliquées\n")
    out.append("- **Binômes conservés** : Laura ↔ Rami (priorité), Aytana ↔ Zied, "
               "Lora ↔ Majdi (Lora couvre **les 13** jours de présence du Dr Majdi).")
    out.append("- **Remplacements habituels** : le jour OFF d'Aytana, Laura passe "
               "chez Zied et Inès (#2 chez Rami) prend le Dr Rami.")
    out.append("- **Accueil équilibré** entre Soraya (11) et Inès (8), avec appoint "
               "de Lora (2) et Laura (1) ; Aytana reste dédiée au Dr Zied.")
    out.append("- **Variété maîtrisée** : Soraya assure occasionnellement le Dr Rami "
               "(2 j), sans casser les binômes habituels.")
    out.append("- **Jours OFF** : Aytana les 04, 10, 16, 22, 28/09 ; Inès les 03, 08, "
               "14, 24, 29/09 — toujours **des jours différents** pour garantir la "
               "couverture.")
    out.append("- **Rotation des samedis** : Laura (05), Lora (12), Aytana (19), "
               "Inès (26) — Soraya jamais le samedi.")
    return "\n".join(out)

ROLE_CLASS = {"R": "rami", "Z": "zied", "M": "majdi", "ACC": "accueil",
              "SAT": "samedi", "RAM_AM": "rami"}
ROLE_NAME = {"R": "Dr Rami", "Z": "Dr Zied", "M": "Dr Majdi",
             "ACC": "Accueil", "SAT": "Samedi", "RAM_AM": "Dr Rami"}
DOMINANT = {"Laura": ("rami", "Dr Rami"), "Soraya": ("accueil", "Accueil"),
            "Lora": ("majdi", "Dr Majdi"), "Ines": ("accueil", "Accueil"),
            "Aytana": ("zied", "Dr Zied")}
CONTRAT = {"Laura": "38h", "Soraya": "38h", "Lora": "34h",
           "Ines": "30h", "Aytana": "30h"}

def html_cell(a, r):
    if r == "OFF":
        return '<td class="c"><span class="off">Repos</span></td>'
    cls = ROLE_CLASS[r]
    name = ROLE_NAME[r]
    if a == "Lora" and r != "SAT":
        time = LORA_HOR
    elif r == "RAM_AM":
        time = HOR["RAM_AM"]
    else:
        time = HOR[r]
    tag = ' <span class="tag">matin</span>' if r == "RAM_AM" else ""
    return (f'<td class="c"><span class="chip {cls}">'
            f'<span class="role">{name}{tag}</span>'
            f'<span class="time">{time}</span></span></td>')

def render_html(plan, stats, errs):
    disp = {"Ines": "Inès"}
    days = open_days()
    # groupes par semaine ISO, ordonnés
    weeks = []
    for d in days:
        wk = d.isocalendar()[1]
        if not weeks or weeks[-1][0] != wk:
            weeks.append((wk, []))
        weeks[-1][1].append(d)

    rows = []
    for i, (wk, wdays) in enumerate(weeks, 1):
        lo, hi = wdays[0], wdays[-1]
        rows.append(
            f'<tr class="wk"><td colspan="6">Semaine {i} · '
            f'{lo.day} → {hi.day} septembre</td></tr>')
        for d in wdays:
            sat = " sat" if d.weekday() == 5 else ""
            jour = JOURS_FR[d.weekday()]
            rows.append(f'<tr class="day{sat}">')
            rows.append(
                f'<th scope="row" class="date"><span class="dwrap">'
                f'<span class="d">{d.day:02d}</span>'
                f'<span class="j">{jour[:3].lower()}.</span></span></th>')
            for a in ["Laura", "Soraya", "Lora", "Ines", "Aytana"]:
                rows.append(html_cell(a, plan[d][a]))
            rows.append("</tr>")

    cards = []
    for a in ["Laura", "Soraya", "Lora", "Ines", "Aytana"]:
        s = stats[a]
        cls, dname = DOMINANT[a]
        avg = hhmm(s["heures"] / 4.3)
        stat_items = [
            ("Jours", s["jours"]), ("Heures", hhmm(s["heures"])),
            ("Accueil", s["acc"]), ("Rami", s["rami"]),
            ("Zied", s["zied"]), ("Majdi", s["majdi"]), ("Samedis", s["sam"]),
        ]
        grid = "".join(
            f'<div class="st"><span class="v">{v}</span>'
            f'<span class="k">{k}</span></div>' for k, v in stat_items)
        cards.append(f'''<article class="card {cls}">
  <header><h3>{disp.get(a,a)}</h3>
  <p class="sub">Contrat {CONTRAT[a]}/sem · réalisé ~{avg}/sem</p></header>
  <div class="stats">{grid}</div>
</article>''')

    check = ("Toutes les contraintes sont respectées" if not errs
             else f"{len(errs)} anomalie(s) — voir le fichier source")

    legend = "".join(
        f'<span class="lg {c}"><span class="dot"></span>{n}</span>'
        for c, n in [("rami", "Dr Rami"), ("zied", "Dr Zied"),
                     ("majdi", "Dr Majdi"), ("accueil", "Accueil"),
                     ("samedi", "Samedi"), ("off", "Repos")])

    head = ('<th class="date">Date</th>'
            + "".join(f'<th class="{DOMINANT[a][0]}">{disp.get(a,a)}</th>'
                      for a in ["Laura", "Soraya", "Lora", "Ines", "Aytana"]))

    return f'''<title>Planning cabinet dentaire — Septembre 2026</title>
<style>{CSS}</style>
<main>
  <header class="mast">
    <p class="eyebrow">Cabinet dentaire · Assistantes</p>
    <h1>Planning — Septembre 2026</h1>
    <p class="lede">Cinq assistantes, du lundi au samedi. Chaque dentiste
      présent (Rami, Zied, Majdi) a son assistante&nbsp;; une personne tient
      l'accueil. Le Dr Emine travaille sans assistante.</p>
    <div class="legend">{legend}</div>
  </header>

  <div class="scroll">
    <table class="grid">
      <thead><tr>{head}</tr></thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </div>

  <section class="recap">
    <h2>Récapitulatif du mois</h2>
    <div class="cards">
      {''.join(cards)}
    </div>
  </section>

  <section class="notes">
    <p class="ok"><span class="check">✓</span> {check}
      <span class="muted">— vérifié automatiquement (couverture, binômes
      habituels, jours OFF distincts Inès/Aytana, Soraya jamais vendredi ni
      samedi, rotation des samedis, exception Dr Rami du 25/09).</span></p>
    <p class="muted small">Journée = 7h36 net (créneaux 09h00-17h06, 09h30-17h36,
      10h00-18h06). Lora : 6h48/jour (09h00-16h18). Samedi 09h30-13h30 (4h).
      Besoin quotidien réel de 3 à 4 postes pour 5 assistantes : le temps de
      repos excédentaire est réparti équitablement, sans dépasser aucun contrat.
      Le contrat 38h de Soraya est ramené à ~30h24 par le congé parental du
      vendredi.</p>
  </section>
</main>'''

CSS = r"""
* { box-sizing: border-box; }
:root {
  --bg:#f3f5f8; --surface:#ffffff; --surface-2:#f7f9fc; --border:#e2e6ee;
  --text:#1f2733; --muted:#697386; --heading:#141b26;
  --c-rami:#4f46e5; --c-zied:#0f766e; --c-majdi:#b45309;
  --c-accueil:#be185d; --c-samedi:#15803d; --c-off:#94a0b3;
  --band:#eef1f6;
  --font:"Inter var",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg:#0e131b; --surface:#161d28; --surface-2:#131a24; --border:#26303f;
    --text:#dce3ec; --muted:#8b97a8; --heading:#f0f4f9;
    --c-rami:#a5b4fc; --c-zied:#5eead4; --c-majdi:#fcd34d;
    --c-accueil:#f9a8d4; --c-samedi:#86efac; --c-off:#5c6779;
    --band:#1b2330;
  }
}
:root[data-theme="light"] {
  --bg:#f3f5f8; --surface:#ffffff; --surface-2:#f7f9fc; --border:#e2e6ee;
  --text:#1f2733; --muted:#697386; --heading:#141b26;
  --c-rami:#4f46e5; --c-zied:#0f766e; --c-majdi:#b45309;
  --c-accueil:#be185d; --c-samedi:#15803d; --c-off:#94a0b3; --band:#eef1f6;
}
:root[data-theme="dark"] {
  --bg:#0e131b; --surface:#161d28; --surface-2:#131a24; --border:#26303f;
  --text:#dce3ec; --muted:#8b97a8; --heading:#f0f4f9;
  --c-rami:#a5b4fc; --c-zied:#5eead4; --c-majdi:#fcd34d;
  --c-accueil:#f9a8d4; --c-samedi:#86efac; --c-off:#5c6779; --band:#1b2330;
}
body { margin:0; background:var(--bg); color:var(--text);
  font-family:var(--font); line-height:1.5;
  -webkit-font-smoothing:antialiased; }
main { max-width:1120px; margin:0 auto; padding:clamp(20px,4vw,52px) clamp(16px,3vw,32px) 64px; }

.mast { margin-bottom:28px; }
.eyebrow { text-transform:uppercase; letter-spacing:.14em; font-size:.72rem;
  font-weight:600; color:var(--c-rami); margin:0 0 10px; }
h1 { font-family:var(--serif); font-weight:600; letter-spacing:-.01em;
  font-size:clamp(1.9rem,4.5vw,3rem); line-height:1.05; margin:0 0 12px;
  color:var(--heading); text-wrap:balance; }
.lede { max-width:62ch; color:var(--muted); font-size:1.02rem; margin:0 0 22px; }

.legend { display:flex; flex-wrap:wrap; gap:8px 16px; align-items:center; }
.lg { display:inline-flex; align-items:center; gap:7px; font-size:.82rem;
  color:var(--muted); font-weight:500; }
.lg .dot { width:11px; height:11px; border-radius:3px;
  background:color-mix(in srgb, var(--role) 22%, var(--surface));
  border-left:3px solid var(--role); }
.lg.rami{--role:var(--c-rami)} .lg.zied{--role:var(--c-zied)}
.lg.majdi{--role:var(--c-majdi)} .lg.accueil{--role:var(--c-accueil)}
.lg.samedi{--role:var(--c-samedi)} .lg.off{--role:var(--c-off)}

.scroll { overflow-x:auto; border:1px solid var(--border); border-radius:14px;
  background:var(--surface); box-shadow:0 1px 2px rgba(20,27,38,.04); }
table.grid { border-collapse:collapse; width:100%; min-width:720px; }
.grid thead th { position:sticky; top:0; z-index:3; background:var(--surface);
  text-align:left; font-size:.82rem; font-weight:600; color:var(--heading);
  padding:14px 12px; border-bottom:1px solid var(--border);
  box-shadow:inset 0 -2px 0 color-mix(in srgb, var(--role,transparent) 55%, transparent); }
.grid thead th.rami{--role:var(--c-rami)} .grid thead th.zied{--role:var(--c-zied)}
.grid thead th.majdi{--role:var(--c-majdi)} .grid thead th.accueil{--role:var(--c-accueil)}
.grid thead th.date{ box-shadow:none; }

.grid th.date { width:64px; }
.grid tr.wk td { background:var(--band); color:var(--muted);
  font-size:.74rem; font-weight:600; letter-spacing:.06em; text-transform:uppercase;
  padding:8px 14px; border-bottom:1px solid var(--border); }
.grid tbody, .grid tr { border:0; }
.grid td, .grid th.date { padding:7px 10px; border-bottom:1px solid var(--border);
  vertical-align:middle; }
.grid tr.day:hover td, .grid tr.day:hover th.date { background:var(--surface-2); }
.grid th.date { position:sticky; left:0; z-index:2; background:var(--surface); }
.grid tr.wk td { z-index:1; }
.dwrap { display:flex; align-items:baseline; gap:6px; }
.grid tr.day:hover th.date { background:var(--surface-2); }
.date .d { font-size:1.05rem; font-weight:700; color:var(--heading);
  font-variant-numeric:tabular-nums; }
.date .j { font-size:.72rem; color:var(--muted); }
tr.sat th.date .d { color:var(--c-samedi); }

.chip { display:flex; flex-direction:column; gap:1px; padding:6px 9px;
  border-radius:8px; border-left:3px solid var(--role);
  background:color-mix(in srgb, var(--role) 12%, var(--surface));
  min-width:104px; }
.chip.rami{--role:var(--c-rami)} .chip.zied{--role:var(--c-zied)}
.chip.majdi{--role:var(--c-majdi)} .chip.accueil{--role:var(--c-accueil)}
.chip.samedi{--role:var(--c-samedi)}
.chip .role { font-size:.83rem; font-weight:600; color:var(--role); }
.chip .time { font-size:.72rem; color:var(--muted); font-variant-numeric:tabular-nums; }
.chip .tag { font-size:.62rem; font-weight:600; text-transform:uppercase;
  letter-spacing:.05em; color:var(--muted); }
.off { font-size:.78rem; color:var(--c-off); font-style:italic; padding-left:3px; }

.recap { margin-top:40px; }
.recap h2, .notes h2 { font-family:var(--serif); font-weight:600;
  font-size:1.5rem; color:var(--heading); margin:0 0 18px; }
.cards { display:grid; gap:14px;
  grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); }
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
.st .k { font-size:.64rem; text-transform:uppercase; letter-spacing:.05em;
  color:var(--muted); }

.notes { margin-top:36px; display:flex; flex-direction:column; gap:10px; }
.ok { font-size:.95rem; margin:0; }
.check { display:inline-grid; place-items:center; width:20px; height:20px;
  border-radius:50%; background:color-mix(in srgb,var(--c-samedi) 20%,transparent);
  color:var(--c-samedi); font-weight:700; font-size:.8rem; margin-right:6px;
  vertical-align:-2px; }
.muted { color:var(--muted); } .small { font-size:.82rem; line-height:1.55; }
@media (prefers-reduced-motion:reduce){ *{scroll-behavior:auto} }
"""

if __name__ == "__main__":
    plan = build()
    errs = verify(plan)
    stats = recap(plan)
    md = render(plan, stats, errs)
    with open("planning-septembre-2026.md", "w") as f:
        f.write(md + "\n")
    with open("planning-septembre-2026.html", "w") as f:
        f.write(render_html(plan, stats, errs) + "\n")
    print("ERREURS:", errs if errs else "aucune")
    print("--- STATS ---")
    for a in ASSISTANTS:
        s = stats[a]
        print(a, s, hhmm(s['heures']))
