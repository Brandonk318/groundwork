import { describe, expect, it } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../App";
import MusicPlayer from "../components/MusicPlayer";
import { scoreInterview, merchIsDiscreet, tokenBalance, negotiate, coarseCity, MERCH } from "../data/phase3";
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

describe("phase3 helpers", () => {
  it("scores interviews deterministically, strong beats weak", () => {
    const weak = scoreInterview("q1", "I dunno.");
    const strong = scoreInterview("q1", "For example, I helped finish a job safely and learned the result was good.");
    expect(strong.score).toBeGreaterThan(weak.score);
    expect(scoreInterview("q1", "For example, I helped finish a job safely and learned the result was good.").score).toBe(strong.score);
  });
  it("merch catalog is discreet", () => { expect(MERCH.every(merchIsDiscreet)).toBe(true); });
  it("tokens add up, negotiation explains own side", () => {
    expect(tokenBalance([{ points: 10 }, { points: -4 }])).toBe(6);
    expect(negotiate({ interests: ["music"], dealbreakers: ["smoking"] }, { interests: ["music"], attributes: { habit: "smoking" } }).reasons[0]).toMatch(/You listed smoking/);
    expect(coarseCity("Fort Worth")).toEqual({ city: "Fort Worth", precision: "city" });
  });
});

describe("i18n", () => {
  it("all 8 locales carry phase3 keys including new features", () => {
    const need = ["carpoolTitle", "rideFallbackTitle", "groupsTitle2", "housingTitle", "musicTitle", "contactLabel", "pingStart", "calcRun", "call211"];
    for (const [lang, dict] of Object.entries(LOCALES)) {
      for (const k of need) expect(dict.phase3[k], `${lang}.${k}`).toBeTruthy();
    }
  });
});

describe("phase3 pages", () => {
  it("learn + match routes render", () => {
    at("/learn");
    expect(screen.getByTestId("course-parole_navigation")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Need help now" })).toBeInTheDocument();
  });
  it("match page runs local preview offline", async () => {
    at("/match");
    fireEvent.click(screen.getByRole("button", { name: /Find matches/ }));
    expect(await screen.findByText(/demo/)).toBeInTheDocument();
  });
  it("work page has resume, interview, gigs with read-aloud", async () => {
    at("/work");
    expect(screen.getByTestId("resume-section")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText(/Full name/), { target: { value: "Alex" } });
    fireEvent.click(screen.getByRole("button", { name: /Build resume/ }));
    expect(await screen.findByText("Alex")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText(/Your answer/), { target: { value: "For example I helped and learned." } });
    fireEvent.click(screen.getByRole("button", { name: /Score my answer/ }));
    await waitFor(() => expect(screen.getAllByRole("button", { name: "Read aloud" }).length).toBeGreaterThanOrEqual(3));
  });
  it("support leads with carpool board and shows ride fallback as backup", () => {
    at("/support");
    expect(screen.getByTestId("carpool-section")).toHaveTextContent(/first place to look/);
    expect(screen.getByTestId("ride-fallback")).toHaveTextContent(/backup/);
    expect(screen.getByTestId("groups-section")).toHaveTextContent(/Sample data only/);
    expect(screen.getByTestId("family-ride-section")).toHaveTextContent(/Approved drivers only/);
    expect(screen.getByTestId("partners-section")).toBeInTheDocument();
  });
  it("community has events, groups, meetings, media, anonymous Q&A", () => {
    at("/feed");
    expect(screen.getByTestId("events-section")).toBeInTheDocument();
    expect(screen.getByTestId("groups-section")).toBeInTheDocument();
    expect(screen.getByTestId("meetings-section")).toBeInTheDocument();
    expect(screen.getByTestId("media-section")).toBeInTheDocument();
    expect(screen.getByTestId("qa-section")).toHaveTextContent(/anonymously/);
  });
  it("journey has tokens, merch, share card, archive, housing calculator", async () => {
    at("/journey");
    expect(screen.getByTestId("tokens-section")).toHaveTextContent(/no cash value/);
    expect(screen.getByTestId("merch-section")).toBeInTheDocument();
    expect(screen.getByTestId("housing-section")).toHaveTextContent(/call 211/);
    fireEvent.change(screen.getByLabelText(/Target \(\$/), { target: { value: "100" } });
    fireEvent.change(screen.getByLabelText(/Monthly savings/), { target: { value: "25" } });
    fireEvent.click(screen.getByRole("button", { name: /Calculate/ }));
    expect(await screen.findByText(/4 months to reach your goal/)).toBeInTheDocument();
  });
  it("music plays in settings but is off inside academy modules", () => {
    at("/settings");
    expect(screen.getByTestId("music-player")).toBeInTheDocument();
    render(<MemoryRouter initialEntries={["/learn"]}><MusicPlayer /></MemoryRouter>);
    expect(screen.getByTestId("music-off")).toHaveTextContent(/off while you are in a course module/);
  });
});
