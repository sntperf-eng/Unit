# NAYRA — Site vitrine

> **La beauté sans compromis.**
> Site vitrine premium pour NAYRA, marque de cosmétiques dont le premier
> produit est un kit de coloration des ongles au henné.

Site minimaliste, luxueux et émotionnel, pensé **mobile-first**, optimisé pour
la performance, le SEO et les Core Web Vitals.

## Stack technique

- **[Astro](https://astro.build/)** — génération statique, zéro JavaScript
  superflu envoyé au client, excellents Core Web Vitals.
- **CSS natif** avec un design system par variables (`src/styles/global.css`) —
  palette, typographie fluide (`clamp`), transitions et animations.
- **Logo officiel NAYRA** — le fichier `public/nayra-logo.png` (or embossé sur
  beige) est l'identité validée, **conservée telle quelle**. Des versions
  optimisées (`.webp`) sont générées pour la performance sans jamais altérer le
  visuel : le logo apparaît dans le hero, l'en-tête, la section finale et le
  pied de page, et sert de base à l'image de partage (`og-image.jpg`).
- **Polices auto-hébergées** ([Fontsource](https://fontsource.org/)) —
  _Cormorant Garamond_ (titres) & _Jost_ (texte) — aucune requête externe.
- **Aucune dépendance runtime côté client** — les interactions (révélation au
  scroll, menu, parallaxe, accordéon FAQ) sont en JavaScript vanille léger.

## Démarrage

```bash
npm install      # installe les dépendances
npm run dev      # serveur de développement (http://localhost:4321)
npm run build    # build de production dans dist/
npm run preview  # prévisualise le build de production
```

## Architecture

```text
src/
├── data/site.ts          # Contenu éditorial centralisé (marque, kit, FAQ, avis…)
├── layouts/Layout.astro  # Enveloppe HTML : SEO, Open Graph, JSON-LD, scripts globaux
├── components/           # Composants réutilisables et autonomes
│   ├── Header.astro          # Navigation fixe + menu mobile
│   ├── Hero.astro            # Section d'accroche (logo, slogan, CTA, illustration)
│   ├── Manifesto.astro       # « Pourquoi NAYRA »
│   ├── KitContents.astro     # Composition du kit (12 éléments)
│   ├── Benefits.astro        # « Pourquoi choisir NAYRA »
│   ├── HowItWorks.astro      # Le rituel en 4 étapes
│   ├── Testimonials.astro    # Avis clientes (prêt au lancement)
│   ├── FAQ.astro             # Questions fréquentes (accordéon accessible)
│   ├── Cta.astro             # Appel à l'action final
│   ├── Footer.astro          # Pied de page (liens, réseaux, mentions)
│   ├── Logo.astro            # Signature typographique NAYRA
│   └── Icon.astro            # Jeu d'icônes linéaires cohérent
├── pages/index.astro     # Page d'accueil (assemblage des sections)
└── styles/global.css     # Design system (tokens, base, utilitaires)
public/                   # favicon, og-image, robots.txt, sitemap, manifest
```

Tout le **contenu** vit dans `src/data/site.ts` : les composants sont pilotés
par ces données, ce qui rend le site facile à faire évoluer (ajout de produits,
d'avis, de questions…).

## Points forts

- **SEO** — structure sémantique (H1/H2), métadonnées, Open Graph & Twitter
  Cards, données structurées JSON-LD (`Brand` + `Product`), `sitemap.xml`,
  `robots.txt`.
- **Performance** — HTML compressé, CSS minifié (Lightning CSS) et intégré,
  images/illustrations vectorielles, polices auto-hébergées.
- **Accessibilité** — navigation clavier, `focus-visible`, libellés ARIA,
  respect de `prefers-reduced-motion`, lien d'évitement.
- **Expérience** — animations douces à l'apparition, parallaxe léger,
  micro-interactions, transitions élégantes.

## Palette

| Rôle | Couleur |
| --- | --- |
| Ivoire / fond | `#faf6ef` |
| Crème | `#f4ece1` |
| Beige chaud | `#e9dcc9` |
| Beige du logo | `#e8d8cb` |
| Or / bronze (accent) | `#b98f5c` |
| Doré profond | `#a9814d` |
| Vert sauge | `#a7b3a0` |
| Encre (texte) | `#2c2723` |

Palette accordée au logo officiel : dominante or / bronze chaud sur beige.
