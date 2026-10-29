import { useTranslation } from "react-i18next";
import { APP_NAME } from "../brand";

export default function Home() {
  const { t } = useTranslation();
  return (
    <section>
      <h1>{t("home.title", { app: APP_NAME })}</h1>
      <p>{t("home.tagline")}</p>
    </section>
  );
}
