"""UI tests for the Panel Sine Wave App using Playwright."""

import re

import pytest
from playwright.sync_api import Page, expect

APP_URL = "http://localhost:5006/app"


@pytest.fixture(scope="session")
def browser_context_args():
    return {"base_url": APP_URL}


def test_page_title(page: Page):
    """Verify the page title contains the app name."""
    page.goto(APP_URL)
    expect(page).to_have_title(re.compile("Panel Sine Wave App"))


def test_sliders_present(page: Page):
    """Verify the Frequency, Amplitude, and Phase sliders are present."""
    page.goto(APP_URL)
    for name in ["Frequency", "Amplitude", "Phase"]:
        slider_label = page.get_by_text(name, exact=False)
        expect(slider_label).to_be_visible()


def test_slider_interaction_updates_plot(page: Page):
    """Move the Amplitude slider and verify the plot image updates."""
    page.goto(APP_URL)

    # Wait for the initial plot to render
    plot_img = page.locator("img").last
    expect(plot_img).to_be_visible(timeout=10_000)

    # Capture the initial plot image src
    initial_src = plot_img.get_attribute("src")

    # The Amplitude slider: label and input are siblings inside a container div.
    # Locate the container that has "Amplitude" text, then find the slider within it.
    amp_container = page.locator("div").filter(has_text=re.compile(r"^Amplitude: \d"))
    amp_slider = amp_container.get_by_role("slider")
    expect(amp_slider).to_be_visible()
    amp_slider.focus()

    # Press ArrowRight multiple times to increase the amplitude
    for _ in range(10):
        amp_slider.press("ArrowRight")

    # Verify the slider label updated (value changed from 1)
    expect(page.get_by_text(re.compile(r"Amplitude: [2-5]"))).to_be_visible(timeout=10_000)

    # Verify the plot image was re-rendered (src should change)
    expect(plot_img).not_to_have_attribute("src", initial_src, timeout=10_000)
