import { useTranslation } from "react-i18next";
export default function FamilyPage() {
  const { t } = useTranslation();
  return <section><h1>{t("nav.family")}</h1><p>{t("family.help")}</p><p>{t("family.defaultsOff")}</p></section>;
}
