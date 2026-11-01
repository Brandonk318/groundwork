import { afterEach, describe, expect, it } from "vitest";
import { act, fireEvent, render, screen } from "@testing-library/react";
import i18n, { LANGS } from "../i18n";
import CrisisButton from "../components/CrisisButton";
import TranslationCheck from "../components/TranslationCheck";
import en from "../locales/en/common.json";
import ru from "../locales/ru/common.json";

describe("translation safeguard", () => {
  afterEach(async () => {
    await act(() => i18n.changeLanguage("en"));
  });

  it("every locale has the notice; ru keeps the English string for Brann", () => {
    for (const lng of LANGS) expect(i18n.getResource(lng, "common", "translationCheck.notice"), lng).toBeTruthy();
    expect(ru.translationCheck.notice).toBe(en.translationCheck.notice);
  });

  it("is hidden in English", () => {
    render(<TranslationCheck keys="support.resourcesNote" />);
    expect(screen.queryByTestId("translation-check")).toBeNull();
  });

  it("is hidden while a protected line is still English (current policy)", async () => {
    await act(() => i18n.changeLanguage("es"));
    render(<TranslationCheck keys="crisis.title" />);
    expect(screen.queryByTestId("translation-check")).toBeNull();
  });

  it("crisis dialog opens in one tap with 988/911 links and shows English under translated crisis text", async () => {
    await act(() => i18n.changeLanguage("es"));
    const before = i18n.getResource("es", "common", "crisis.title");
    i18n.addResource("es", "common", "crisis.title", "No estás solo");
    try {
      render(<CrisisButton />);
      fireEvent.click(screen.getByRole("button"));
      const dialog = screen.getByRole("dialog");
      expect(dialog.querySelector('a[href="tel:988"]')).toBeTruthy();
      expect(dialog.querySelector('a[href="tel:911"]')).toBeTruthy();
      const box = screen.getByTestId("translation-check");
      expect(box).toHaveTextContent(en.crisis.title);
      expect(box).toHaveTextContent(i18n.t("translationCheck.notice"));
      expect(box.querySelectorAll("a, button, input").length).toBe(0);
    } finally {
      i18n.addResource("es", "common", "crisis.title", before);
    }
  });
});
