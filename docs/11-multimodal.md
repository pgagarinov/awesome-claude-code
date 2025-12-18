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

In terminal emulators that support it, drag an image directly into the session.

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

## Best Practices

```
# BAD: No context
> What's wrong here? [image]

# GOOD: Context + specific focus
> This screenshot shows our checkout page. Users report the 'Submit'
  button is unresponsive. What might cause this? [image]
```
