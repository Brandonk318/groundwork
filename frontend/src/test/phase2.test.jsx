import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../App";
import i18n from "../i18n";
import en from "../locales/en/common.json";
import es from "../locales/es/common.json";
import fr from "../locales/fr/common.json";
import hi from "../locales/hi/common.json";
import vi from "../locales/vi/common.json";
import ar from "../locales/ar/common.json";
import tl from "../locales/tl/common.json";
import ht from "../locales/ht/common.json";
import { REENTRY_STEPS, REENTRY_SECTIONS, celebrationsFor, sectionProgress } from "../data/reentrySteps";

const at = (p) => render(<MemoryRouter initialEntries={[p]}><App /></MemoryRouter>);
const LOCALES = { en, es, fr, hi, vi, ar, tl, ht };

describe("33 steps data", () => {
  it("has exactly 33 in order grouped by 7 sections", () => {
    expect(REENTRY_STEPS).toHaveLength(33);
    expect(REENTRY_STEPS.map((s) => s.id)).toEqual(Array.from({ length: 33 }, (_, i) => i + 1));
    expect(REENTRY_STEPS[0].title).toBe("Order your birth certificate");
    expect(REENTRY_STEPS[10].title).toBe("Save 988 and 911 in your phone");
    expect(REENTRY_STEPS[32].title).toBe("Set one long-term goal and celebrate your 90-day milestone");
    expect(REENTRY_SECTIONS.map((s) => s.step_ids)).toEqual([[1,2,3,4,5,6],[7,8,9,10,11],[12,13,14,15],[16,17,18],[19,20,21,22,23,24,25],[26,27,28],[29,30,31,32,33]]);
  });
  it("celebrations: first, section, all", () => {
    expect(celebrationsFor([])).toEqual([]);
    expect(celebrationsFor([1])[0].type).toBe("first_step");
    expect(celebrationsFor([1,2,3,4,5,6]).some((c) => c.type === "section_complete" && c.section === "before_release")).toBe(true);
    expect(celebrationsFor(REENTRY_STEPS.map((s) => s.id)).at(-1).type).toBe("all_complete");
    expect(sectionProgress([1,2,3])[0]).toMatchObject({ done: 3, total: 6, percent: 50 });
  });
});

describe("i18n step keys", () => {
  it("all 8 locales have step1..33 and all section keys", () => {
    for (const [lang, dict] of Object.entries(LOCALES)) {
      for (let i = 1; i <= 33; i++) expect(dict.reentry.steps[`step${i}`], `${lang} step${i}`).toBeTruthy();
      for (const s of REENTRY_SECTIONS) expect(dict.reentry.sections[s.id], `${lang} ${s.id}`).toBeTruthy();
    }
    expect(en.reentry.steps.step11).toBe("Save 988 and 911 in your phone");
    expect(i18n.t("reentry.steps.step1")).toBe("Order your birth certificate");
  });
});

describe("checklist page", () => {
  it("renders all 33 steps grouped, read-aloud on every step, crisis links", () => {
    at("/reentry");
    for (let i = 1; i <= 33; i++) expect(screen.getByTestId(`step-${i}`)).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Read aloud" })).toHaveLength(33);
    expect(screen.getByTestId("checklist-crisis")).toHaveTextContent("Call 988");
    expect(screen.getByTestId("step11-crisis").querySelector('a[href="tel:988"]')).toBeTruthy();
    expect(screen.getByTestId("step11-crisis").querySelector('a[href="tel:911"]')).toBeTruthy();
    expect(screen.getByRole("button", { name: "Need help now" })).toBeInTheDocument();
    expect(screen.getByTestId("section-before_release")).toHaveTextContent("0/6");
  });
  it("marking first step fires celebration and updates section progress", () => {
    at("/reentry");
    const step1 = screen.getByTestId("step-1");
    fireEvent.click(step1.querySelectorAll("button")[1]); // Mark done (first button is Read aloud)
    expect(screen.getByTestId("celebrations")).toHaveTextContent("First step done");
    expect(screen.getByTestId("overall-progress")).toHaveTextContent("1/33");
    expect(screen.getByTestId("section-before_release")).toHaveTextContent("1/6");
  });
  it("housing/food steps show 211 pointer only", () => {
    at("/reentry");
    expect(screen.getByTestId("step-7")).toHaveTextContent("call 211");
    expect(screen.getByTestId("step-7")).toHaveTextContent("does not provide");
    expect(screen.getByTestId("step-8")).toHaveTextContent("call 211");
  });
  it("each step has due date, priority, notes and anonymous tips UI", () => {
    at("/reentry");
    expect(screen.getByLabelText("Due date 1")).toBeInTheDocument();
    expect(screen.getByLabelText("Priority 1")).toBeInTheDocument();
    expect(screen.getByLabelText("Notes 1")).toBeInTheDocument();
    fireEvent.click([...screen.getByTestId("step-1").querySelectorAll("button")].find((b) => b.textContent.includes("Tips from people")));
    expect(screen.getByTestId("tips-1")).toHaveTextContent("Tips are anonymous");
  });
  it("can add own step locally", () => {
    at("/reentry");
    fireEvent.change(screen.getByPlaceholderText("Add your own step"), { target: { value: "Call my sister" } });
    fireEvent.click(screen.getAllByRole("button", { name: "Add your own step" })[0]);
    expect(screen.getByText("Call my sister")).toBeInTheDocument();
  });
});
