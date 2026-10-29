import { useState } from "react";
import { useTranslation } from "react-i18next";

// Always rendered by Shell, on every screen, for every plan. Never gated by plan, locks or filters.
export default function CrisisButton() {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  return (
    <div className="crisis">
      <button type="button" className="crisis-button" aria-haspopup="dialog" onClick={() => setOpen(true)}>
        {t("crisis.button")}
      </button>
      {open && (
        <div role="dialog" aria-modal="true" aria-label={t("crisis.title")} className="crisis-dialog">
          <h2>{t("crisis.title")}</h2>
          <a href="tel:988">{t("crisis.call988")}</a>
          <a href="sms:988">{t("crisis.text988")}</a>
          <a href="tel:911">{t("crisis.call911")}</a>
          <button type="button" onClick={() => setOpen(false)}>{t("crisis.close")}</button>
        </div>
      )}
    </div>
  );
}
