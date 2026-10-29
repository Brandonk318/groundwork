import { useTranslation } from "react-i18next";

// Placeholder for one feature area. Each feature id becomes a real page as its module is built.
export default function AreaPage({ area }) {
  const { t } = useTranslation();
  return (
    <section data-area={area.key}>
      <h1>{t(`nav.${area.key}`)}</h1>
      <p>{t("area.comingSoon")}</p>
      <ul>{area.features.map((f) => <li key={f} data-feature={f}>{f}</li>)}</ul>
    </section>
  );
}
