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

export type KitItem = { name: string; icon: string };

export const kitItems: KitItem[] = [
  { name: 'Henné', icon: 'leaf' },
  { name: 'Lime', icon: 'file' },
  { name: 'Buffer', icon: 'buffer' },
  { name: 'Repousse-cuticules', icon: 'pusher' },
  { name: 'Brosse', icon: 'brush' },
  { name: 'Huile pour cuticules', icon: 'drop' },
  { name: 'Stick de nettoyage', icon: 'stick' },
  { name: "Séparateur d'orteils", icon: 'separator' },
  { name: 'Stickers de protection', icon: 'sticker' },
  { name: 'Petit bol en silicone', icon: 'bowl' },
  { name: 'Pochette', icon: 'pouch' },
  { name: "Guide d'utilisation", icon: 'book' },
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

export type Step = { n: string; title: string; text: string; icon: string };

export const steps: Step[] = [
  {
    n: '01',
    title: 'Préparer les ongles',
    text: "Limez, polissez et nettoyez délicatement pour une surface parfaitement nette.",
    icon: 'file',
  },
  {
    n: '02',
    title: 'Appliquer le henné',
    text: 'Déposez la préparation avec la brosse, en un geste précis et enveloppant.',
    icon: 'brush',
  },
  {
    n: '03',
    title: 'Laisser poser',
    text: "Accordez-vous un instant. Le henné révèle sa couleur en toute douceur.",
    icon: 'clock',
  },
  {
    n: '04',
    title: 'Découvrir la couleur',
    text: 'Retirez délicatement et laissez apparaître une teinte chaude et lumineuse.',
    icon: 'sparkle',
  },
];

export type Testimonial = { quote: string; author: string; detail: string };

/** Section prête au lancement — témoignages à venir. */
export const testimonials: Testimonial[] = [
  {
    quote:
      "Une couleur d'une élégance folle, et surtout ce sentiment d'utiliser enfin un produit qui me ressemble.",
    author: 'Première cliente',
    detail: 'Votre avis ici',
  },
  {
    quote:
      "Le kit est complet et magnifiquement pensé. Le geste est devenu mon petit rituel du dimanche.",
    author: 'Première cliente',
    detail: 'Votre avis ici',
  },
  {
    quote:
      'Une teinte naturelle qui tient et un packaging à la hauteur des plus grandes maisons.',
    author: 'Première cliente',
    detail: 'Votre avis ici',
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
