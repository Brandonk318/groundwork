import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../App";
import { suggestFilters, isRough, reachedMilestones } from "../lib/mood";
import { speak } from "../components/ReadAloud";

const at = (p) => render(<MemoryRouter initialEntries={[p]}><App /></MemoryRouter>);

describe("phase1 logic", () => {
  it("rough mood suggests filters, good does not", () => {
    expect(suggestFilters("rough")).toEqual(["hide_triggering_content", "quiet_dms"]);
    expect(suggestFilters("good")).toEqual([]);
    expect(isRough("craving")).toBe(true);
  });
  it("milestones reached", () => { expect(reachedMilestones(95)).toEqual([30, 60, 90]); expect(reachedMilestones(10)).toEqual([]); });
  it("speak returns false without speechSynthesis", () => { expect(typeof speak("hi")).toBe("boolean"); });
});

describe("phase1 pages", () => {
  it("wellbeing shows filter suggestion on rough", () => {
    at("/wellbeing");
    fireEvent.click(screen.getAllByRole("radio")[2]);
    expect(screen.getByTestId("filter-suggestion")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Need help now" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Read aloud" })).toBeInTheDocument();
  });
  it("venue is labelled placeholder", () => { at("/venue"); expect(screen.getByTestId("venue-placeholder").textContent).toMatch(/Placeholder/); expect(screen.getByRole("button", { name: "Need help now" })).toBeInTheDocument(); });
  it("safety shows 988/911 and wipe confirm disabled", () => { at("/safety"); expect(screen.getByText("Call 988")).toBeInTheDocument(); expect(screen.getByRole("button", { name: "Delete my data" })).toBeDisabled(); });
  it("support says directory excludes food/housing in copy", () => { at("/support"); expect(screen.getByText(/does not cover food or housing/)).toBeInTheDocument(); });
  it("reentry shows Brann's first steps", () => { at("/reentry"); expect(screen.getByTestId("step-1")).toHaveTextContent("Order your birth certificate"); expect(screen.getByTestId("step-33")).toHaveTextContent("Set one long-term goal"); });
  it("settings has read-aloud", () => { at("/settings"); expect(screen.getByRole("button", { name: "Read aloud" })).toBeInTheDocument(); });
});
