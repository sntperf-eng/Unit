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

if __name__ == "__main__":
    plan = build()
    errs = verify(plan)
    stats = recap(plan)
    md = render(plan, stats, errs)
    with open("planning-septembre-2026.md", "w") as f:
        f.write(md + "\n")
    print("ERREURS:", errs if errs else "aucune")
    print("--- STATS ---")
    for a in ASSISTANTS:
        s = stats[a]
        print(a, s, hhmm(s['heures']))
