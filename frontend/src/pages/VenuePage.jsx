import { useTranslation } from "react-i18next";
export const VENUE_STOPS = ["entrance", "zero-proof bar", "lounge", "stage", "dining"];
export default function VenuePage() {
  const { t } = useTranslation();
  return (
    <section>
      <h1>{t("nav.venue")}</h1>
      <p data-testid="venue-placeholder">{t("venue.placeholder")}</p>
      <ul>{VENUE_STOPS.map((s) => <li key={s}>{s}</li>)}</ul>
    </section>
  );
}
