# Part 11: Multi-Modal: Screenshots & Images

## Claude's Vision Capabilities

Claude Code can analyse:
- Screenshots of UI/applications
- Error message screenshots
- Design mockups and wireframes
- Architecture diagrams
- Charts and graphs
- Photos of whiteboards

## Providing Images

### Method 1: File Path

```
> Analyse the screenshot at ./screenshots/error.png

> Review the UI mockup at ./designs/homepage-v2.png
```

### Method 2: Drag and Drop

In terminal emulators that support it, drag an image directly into the session. You can also paste images from your clipboard.

See [Common Workflows: Images](https://code.claude.com/docs/en/common-workflows#work-with-images) for more details.

## Use Cases

### Debugging Visual Issues

```
> Here's a screenshot of the bug: ./screenshots/layout-broken.png
  The sidebar should be on the left but it's overlapping the content.
  Find and fix the CSS issue.
```

### Error Analysis

```
> This screenshot shows the error in my browser console:
  ./screenshots/console-error.png
  Help me debug this issue.
```

### Design Implementation

```
> Implement this UI component based on the mockup at
  ./designs/card-component.png using our existing design system.
```

### Architecture Understanding

```
> Here's a diagram of our system architecture: ./docs/architecture.png
  Explain how data flows from the user request to the database.
```

## Automated Visual Debugging with Playwright

A powerful technique for UI debugging: use Playwright to take screenshots, analyse them, fix the code, and repeat.

### The Loop

```
1. Take screenshot → 2. Claude analyses → 3. Fix code → 4. Take new screenshot → Repeat
```

### Example Workflow

```
> Write a Playwright script that:
  1. Opens http://localhost:3000/checkout
  2. Takes a screenshot and saves it to ./screenshots/step1.png

[Claude writes and runs the script]

> Analyse ./screenshots/step1.png - the form layout looks broken

[Claude identifies CSS issues and fixes them]

> Now click the "Continue" button and take another screenshot

[Claude updates the script to click and capture]

> Analyse ./screenshots/step2.png - is the validation error showing correctly?

[Continue iterating...]
```

### Full Automation Example

```
> Create a Playwright test that:
  1. Goes to the login page
  2. Takes a screenshot
  3. Enters invalid credentials
  4. Clicks submit
  5. Takes a screenshot of the error state
  6. Enters valid credentials
  7. Clicks submit
  8. Takes a screenshot of the dashboard

  Save all screenshots to ./test-screenshots/ and run it.
  Then analyse each screenshot and tell me if anything looks wrong.
```

### Why This Works Well

- **No manual screenshots** - Playwright automates capture
- **Reproducible states** - Script can replay exact interactions
- **Iterate quickly** - Fix code, re-run script, analyse new screenshot
- **Test user flows** - Click buttons, fill forms, navigate pages
- **CI integration** - Run visual tests in pipelines

### Useful Playwright Commands

```python
# Screenshot full page
await page.screenshot(path="full.png", full_page=True)

# Screenshot specific element
await page.locator(".modal").screenshot(path="modal.png")

# Wait for animations before capture
await page.wait_for_timeout(500)
await page.screenshot(path="after-animation.png")
```

## Best Practices

```
# BAD: No context
> What's wrong here? [image]

# GOOD: Context + specific focus
> This screenshot shows our checkout page. Users report the 'Submit'
  button is unresponsive. What might cause this? [image]
```
