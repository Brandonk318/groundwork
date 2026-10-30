import { describe, expect, it } from "vitest";
import { render, screen, fireEvent, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../App";
import en from "../locales/en/common.json";
import es from "../locales/es/common.json";
import fr from "../locales/fr/common.json";
import hi from "../locales/hi/common.json";
import vi from "../locales/vi/common.json";
import ar from "../locales/ar/common.json";
import tl from "../locales/tl/common.json";
import ht from "../locales/ht/common.json";

const at = (p) => render(<MemoryRouter initialEntries={[p]}><App /></MemoryRouter>);
const LOCALES = { en, es, fr, hi, vi, ar, tl, ht };

describe("phase4 portfolio UI", () => {
  it("all 8 locales carry portfolio share/reorder keys", () => {
    const need = ["portfolioAdd", "shareDialog", "shareWho", "mintLink", "revokeLink", "moveUp", "moveDown", "suggestTitle", "suggestHelp", "visPrivate", "visLink"];
    for (const [lang, dict] of Object.entries(LOCALES)) {
      for (const k of need) expect(dict.phase3[k], `${lang}.${k}`).toBeTruthy();
    }
  });
  it("portfolio section is private by default with read-aloud and crisis button", () => {
    at("/journey");
    const sec = screen.getByTestId("portfolio-section");
    expect(sec).toHaveTextContent(/Private by default/);
    expect(within(sec).getAllByRole("button", { name: "Read aloud" }).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByRole("button", { name: "Need help now" })).toBeInTheDocument();
  });
  it("can add an item locally, open share dialog, and edit it", async () => {
    at("/journey");
    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Day 30" } });
    fireEvent.click(screen.getByRole("button", { name: /Add item/ }));
    const item = await screen.findByText("Day 30");
    expect(item).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Share this item/ }));
    const dlg = await screen.findByTestId("share-dialog");
    expect(dlg).toHaveTextContent(/only you/);
    expect(dlg).toHaveTextContent(/Mint link/);
    fireEvent.click(within(dlg).getByRole("button", { name: /Cancel/ }));
    fireEvent.click(screen.getByRole("button", { name: /Edit/ }));
    fireEvent.change(screen.getByLabelText("edit title"), { target: { value: "Day 30 edited" } });
    fireEvent.click(within(screen.getByTestId("portfolio-section")).getByRole("button", { name: /^Save$/ }));
    expect(await screen.findByText("Day 30 edited")).toBeInTheDocument();
  });
  it("reorder buttons move items", async () => {
    at("/journey");
    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "First" } });
    fireEvent.click(screen.getByRole("button", { name: /Add item/ }));
    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Second" } });
    fireEvent.click(screen.getByRole("button", { name: /Add item/ }));
    await screen.findByText("Second");
    const lis = screen.getByTestId("portfolio-section").querySelectorAll("li");
    const before = [...lis].map((li) => li.textContent);
    const ups = screen.getAllByRole("button", { name: /Move up/ });
    fireEvent.click(ups[ups.length - 1]);
    const after = [...screen.getByTestId("portfolio-section").querySelectorAll("li")].map((li) => li.textContent);
    expect(after).not.toEqual(before);
  });
});
