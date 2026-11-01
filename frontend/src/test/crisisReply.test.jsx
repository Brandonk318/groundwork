import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import CommunityPage from "../pages/CommunityPage";
import SafetyPage from "../pages/SafetyPage";
import CrisisNotice from "../components/CrisisNotice";
import "../i18n";

const NOTICE = { locale: "en", title: "You are not alone", body: "Call or text 988. Text HOME to 741741.", private: true,
  resources: [{ id: "988", label: "Call or text 988", tel: "tel:988" }, { id: "911", label: "Emergency: 911", tel: "tel:911" }, { id: "741741", label: "Text HOME to 741741", sms: "sms:741741?body=HOME" }],
  links: { crisis_button: "/safety" } };
const json = (d) => Promise.resolve({ ok: true, json: () => Promise.resolve(d) });
afterEach(() => vi.restoreAllMocks());

describe("private crisis auto-reply", () => {
  it("renders 988, 911, 741741 and crisis-button link", () => {
    render(<MemoryRouter><CrisisNotice notice={NOTICE} /></MemoryRouter>);
    expect(screen.getByText("Call or text 988").getAttribute("href")).toBe("tel:988");
    expect(screen.getByText("Emergency: 911").getAttribute("href")).toBe("tel:911");
    expect(screen.getByText("Text HOME to 741741").getAttribute("href")).toContain("741741");
    expect(screen.getByText(/Only you can see/)).toBeTruthy();
  });
  it("renders nothing without a notice", () => {
    const { container } = render(<MemoryRouter><CrisisNotice notice={null} /></MemoryRouter>);
    expect(container.innerHTML).toBe("");
  });
  it("shows the notice to the author after posting, post goes through", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation((url, opts) =>
      opts?.method === "POST" ? json({ body: "x", status: "published", private_notice: NOTICE }) : json({ posts: [], questions: [] }));
    render(<MemoryRouter><CommunityPage /></MemoryRouter>);
    fireEvent.change(screen.getByLabelText(/Share/), { target: { value: "I want to die" } });
    fireEvent.click(screen.getByText("Post"));
    await waitFor(() => expect(screen.getByTestId("crisis-notice")).toBeTruthy());
  });
  it("no notice when the response has none", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation((url, opts) =>
      opts?.method === "POST" ? json({ body: "hi", status: "published" }) : json({ posts: [], questions: [] }));
    render(<MemoryRouter><CommunityPage /></MemoryRouter>);
    fireEvent.change(screen.getByLabelText(/Share/), { target: { value: "hi" } });
    fireEvent.click(screen.getByText("Post"));
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(4));
    expect(screen.queryByTestId("crisis-notice")).toBeNull();
  });
  it("safety page shows the caller's own private inbox", async () => {
    const f = vi.spyOn(globalThis, "fetch").mockImplementation(() => json({ messages: [{ id: "m1", message: NOTICE, read: false }] }));
    render(<MemoryRouter><SafetyPage /></MemoryRouter>);
    await waitFor(() => expect(screen.getByTestId("private-inbox")).toBeTruthy());
    expect(f.mock.calls[0][0]).toBe("/api/safety/private_inbox");
  });
});
