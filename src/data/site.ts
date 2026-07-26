/**
 * NAYRA — Contenu du site centralisé.
 * Toutes les données éditoriales vivent ici pour garder les composants
 * réutilisables et l'architecture évolutive (ajout de produits futurs).
 */

export const brand = {
  name: 'NAYRA',
  slogan: 'La beauté sans compromis.',
  baseline:
    'Le premier kit de coloration des ongles au henné, pensé comme un rituel de beauté.',
  url: 'https://nayra.com',
  email: 'contact@nayra.com',
  social: {
    instagram: 'https://instagram.com/nayra',
    tiktok: 'https://tiktok.com/@nayra',
  },
} as const;

export const nav = [
  { label: 'La marque', href: '#marque' },
  { label: 'Le kit', href: '#kit' },
  { label: 'Rituel', href: '#rituel' },
  { label: 'Avis', href: '#avis' },
  { label: 'FAQ', href: '#faq' },
] as const;

export const manifesto = {
  eyebrow: 'Pourquoi NAYRA',
  title: 'Prendre soin de soi, sans jamais renoncer à ses valeurs.',
  paragraphs: [
    "Beaucoup de femmes rêvent d'ongles élégants et colorés, tout en cherchant une alternative plus naturelle au vernis classique.",
    "NAYRA est née de cette conviction : il ne devrait plus être nécessaire de choisir entre prendre soin de soi et rester fidèle à ce que l'on est.",
    "Nous avons imaginé une solution douce, naturelle et raffinée — un geste simple qui devient un véritable rituel de beauté.",
  ],
  signature: 'Enfin une marque pensée pour vous.',
} as const;

export type KitItem = { name: string; label: string; desc: string; icon: string };

export const kitItems: KitItem[] = [
  {
    name: 'Henné pour ongles',
    label: 'Flacon style vernis · 10 ml',
    desc: 'Coloration naturelle pour des ongles éclatants.',
    icon: 'leaf',
  },
  {
    name: 'Lime à ongles',
    label: 'Blanche',
    desc: 'Pour façonner et mettre en forme.',
    icon: 'file',
  },
  {
    name: 'Buffer',
    label: 'Bloc blanc',
    desc: "Pour lisser et préparer l'ongle.",
    icon: 'buffer',
  },
  {
    name: 'Repousse-cuticules',
    label: 'Inox double embout',
    desc: 'Pour des cuticules nettes et soignées.',
    icon: 'pusher',
  },
  {
    name: 'Brossette ongles',
    label: 'Sans manche',
    desc: 'Pour nettoyer les ongles en douceur.',
    icon: 'brush',
  },
  {
    name: 'Huile cuticules',
    label: 'Flacon pipette ambré · 10 ml',
    desc: 'Nourrit, hydrate et sublime.',
    icon: 'drop',
  },
  {
    name: 'Stick de nettoyage',
    label: 'Bois',
    desc: 'Pour nettoyer les contours avec précision.',
    icon: 'stick',
  },
  {
    name: "Séparateur d'orteils",
    label: 'Mousse',
    desc: 'Pour une application facile sur les pieds.',
    icon: 'separator',
  },
  {
    name: 'Stickers de protection',
    label: 'Autocollants',
    desc: "Protègent la peau lors de l'application.",
    icon: 'sticker',
  },
  {
    name: 'Petit bol en silicone',
    label: 'Rose poudré',
    desc: 'Pour mélanger le henné facilement.',
    icon: 'bowl',
  },
  {
    name: 'Pochette en coton',
    label: 'Écru',
    desc: 'Élégante et pratique pour ranger votre kit.',
    icon: 'pouch',
  },
  {
    name: "Guide d'utilisation",
    label: 'Livret imprimé',
    desc: 'Toutes les étapes expliquées pour un résultat parfait.',
    icon: 'book',
  },
];

export type Benefit = { icon: string; title: string; text: string };

export const benefits: Benefit[] = [
  {
    icon: 'leaf',
    title: 'Naturel',
    text: "Une coloration au henné, alternative douce au vernis classique.",
  },
  {
    icon: 'sparkle',
    title: 'Élégant',
    text: 'Une teinte subtile et raffinée qui sublime la main avec justesse.',
  },
  {
    icon: 'hand',
    title: 'Facile à utiliser',
    text: 'Un geste simple, guidé pas à pas, à réaliser chez soi en toute sérénité.',
  },
  {
    icon: 'heart',
    title: 'Pensé pour votre routine',
    text: "Un rituel qui s'intègre naturellement à votre moment de soin.",
  },
  {
    icon: 'gift',
    title: 'Kit complet',
    text: "Tout le nécessaire réuni dans un écrin, du henné jusqu'à la pochette.",
  },
];

export type Step = {
  n: string;
  phase: string;
  title: string;
  text: string;
  icon: string;
  art: number;
};

export const steps: Step[] = [
  {
    n: '01',
    phase: 'Préparez',
    title: 'Préparez vos ongles',
    text: 'Limez, polissez, repoussez les cuticules et nettoyez soigneusement vos ongles avant toute application.',
    icon: 'file',
    art: 1,
  },
  {
    n: '02',
    phase: 'Mélangez',
    title: 'Préparez votre henné',
    text: "Versez la poudre dans le bol puis ajoutez progressivement quelques gouttes d'eau jusqu'à obtenir une pâte lisse et homogène.",
    icon: 'bowl',
    art: 2,
  },
  {
    n: '03',
    phase: 'Protégez',
    title: 'Protégez les contours',
    text: 'Appliquez les stickers autour des ongles pour un résultat net et précis.',
    icon: 'sticker',
    art: 3,
  },
  {
    n: '04',
    phase: 'Appliquez',
    title: 'Appliquez le henné',
    text: 'Recouvrez uniformément chaque ongle avec une fine couche de henné.',
    icon: 'brush',
    art: 4,
  },
  {
    n: '05',
    phase: 'Patientez',
    title: 'Laissez agir',
    text: 'Plus le temps de pose est long, plus la couleur sera intense.',
    icon: 'clock',
    art: 5,
  },
  {
    n: '06',
    phase: 'Révélez',
    title: 'Découvrez votre couleur',
    text: 'Retirez délicatement le henné sec. La couleur continuera de se développer naturellement pendant les 24 à 48 heures suivantes.',
    icon: 'sparkle',
    art: 6,
  },
];

export type PoseLevel = { icon: string; time: string; label: string; level: number };

export const poseLevels: PoseLevel[] = [
  { icon: 'clock', time: '30 min', label: 'Léger', level: 1 },
  { icon: 'clock', time: '1–2 h', label: 'Soutenu', level: 2 },
  { icon: 'moon', time: 'Toute une nuit', label: 'Intensité maximale', level: 3 },
];

export const secret = {
  title: "Le secret d'un résultat optimal",
  text: "Pour une couleur plus intense, laissez poser le henné le plus longtemps possible et évitez de mouiller vos ongles juste après le retrait. La couleur continue d'évoluer naturellement pendant les heures qui suivent.",
};

export type Testimonial = { quote: string; author: string; detail: string };

export const testimonials: Testimonial[] = [
  {
    quote:
      "Une couleur d'une élégance folle, et surtout ce sentiment d'utiliser enfin un produit qui me ressemble.",
    author: 'Camille Laurent',
    detail: 'Cliente vérifiée',
  },
  {
    quote:
      "Le kit est complet et magnifiquement pensé. Le geste est devenu mon petit rituel du dimanche.",
    author: 'Inès Benali',
    detail: 'Cliente vérifiée',
  },
  {
    quote:
      'Une teinte naturelle qui tient et un packaging à la hauteur des plus grandes maisons.',
    author: 'Sarah Moreau',
    detail: 'Cliente vérifiée',
  },
];

export type Faq = { q: string; a: string };

export const faqs: Faq[] = [
  {
    q: 'Combien de temps dure la couleur ?',
    a: "La teinte au henné évolue naturellement avec la pousse de l'ongle. Selon votre routine, elle sublime vos mains pendant plusieurs semaines, sans écaillage brutal comme un vernis.",
  },
  {
    q: 'Comment appliquer le henné ?',
    a: "Rien de plus simple : préparez vos ongles, appliquez la préparation à la brosse, laissez poser puis révélez la couleur. Le guide d'utilisation vous accompagne à chaque étape.",
  },
  {
    q: "À quelle fréquence puis-je l'utiliser ?",
    a: "Aussi souvent que vous le souhaitez. Le henné est doux ; vous pouvez renouveler le rituel dès que vous avez envie de raviver la teinte.",
  },
  {
    q: 'Le kit est-il adapté aux débutantes ?',
    a: "Absolument. Chaque accessoire et le guide pas à pas ont été pensés pour rendre le geste accessible, même pour une toute première fois.",
  },
  {
    q: 'Puis-je utiliser le kit sur les pieds ?',
    a: "Oui. Le séparateur d'orteils est justement prévu pour cela : le rituel se prolonge naturellement des mains jusqu'aux pieds.",
  },
];

export const footerLinks = {
  navigation: [
    { label: 'La marque', href: '#marque' },
    { label: 'Le kit', href: '#kit' },
    { label: 'Le rituel', href: '#rituel' },
    { label: 'FAQ', href: '#faq' },
  ],
  legal: [
    { label: 'Mentions légales', href: '#' },
    { label: 'CGV', href: '#' },
    { label: 'Politique de confidentialité', href: '#' },
  ],
} as const;
