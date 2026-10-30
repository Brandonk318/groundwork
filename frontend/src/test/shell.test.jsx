import { describe, expect, it } from "vitest";
import { act, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import i18n, { LANGS } from "../i18n";
import App from "../App";
import { AREAS } from "../areas";
import { APP_NAME } from "../brand";

const at = (path) => render(<MemoryRouter initialEntries={[path]}><App /></MemoryRouter>);

describe("shell", () => {
  it("renders the brand from one config value", () => {
    at("/");
    expect(screen.getAllByText(APP_NAME).length).toBeGreaterThan(0);
    expect(APP_NAME).toBe("Groundwork");
  });

  it.each(["/", ...AREAS.map((a) => `/${a.path}`)])("shows the crisis button on %s", (path) => {
    at(path);
    expect(screen.getByRole("button", { name: "Need help now" })).toBeInTheDocument();
  });

  it("crisis dialog surfaces 988 and 911", () => {
    at("/wellbeing");
    fireEvent.click(screen.getByRole("button", { name: "Need help now" }));
    expect(screen.getByText("Call 988").closest("a")).toHaveAttribute("href", "tel:988");
    expect(screen.getByText("Text 988").closest("a")).toHaveAttribute("href", "sms:988");
    expect(screen.getByText("Emergency: call 911").closest("a")).toHaveAttribute("href", "tel:911");
  });

  it("covers every feature id except the crisis button in an area page", () => {
    const ids = AREAS.flatMap((a) => a.features);
    expect(new Set(ids).size).toBe(ids.length);
    expect(ids.length).toBe(48); // 49 registry entries minus crisis_button (on every screen)
  });
});

describe("i18n", () => {
  it("has the 21 locales", () => {
    expect(LANGS).toEqual(["en", "es", "fr", "hi", "vi", "ar", "tl", "ht", "zh", "ko", "pt", "ru", "so", "ur", "bn", "pa", "fa", "am", "my", "ne", "sw"]);
  });

  it("Arabic is RTL and stubbed locales fall back to English", async () => {
    await act(() => i18n.changeLanguage("ar"));
    expect(document.documentElement.dir).toBe("rtl");
    expect(i18n.t("crisis.button")).toBe("Need help now");
    await act(() => i18n.changeLanguage("es"));
    expect(document.documentElement.dir).toBe("ltr");
    await act(() => i18n.changeLanguage("en"));
  });
});
