# Valido Professional Themes

## Overview

Valido provides two professional themes designed specifically for business applications:

- **Valido White** - Clean, professional light theme
- **Valido Dark** - Modern dark theme with excellent readability

Both themes are built using Tailwind CSS classes and custom CSS properties for maximum flexibility and performance.

## Features

### 🎨 Design Philosophy
- **Professional Appearance** - Business-ready design
- **High Contrast** - Excellent readability
- **Accessibility** - WCAG 2.1 compliant
- **Responsive** - Works on all device sizes
- **Performance Optimized** - Minimal CSS footprint

### 🛠️ Technical Features
- **Tailwind Integration** - Uses Tailwind classes extensively
- **CSS Custom Properties** - Dynamic theming support
- **Component System** - Pre-built UI components
- **Dark Mode Support** - Automatic dark mode detection
- **Print Styles** - Optimized for printing

## Quick Start

### 1. Include Theme CSS

```html
<!-- In your base template -->
<link rel="stylesheet" href="{{ url_for('static', filename='themes/valido-white.css') }}">
```

### 2. Apply Theme Class

```html
<!-- On your root element -->
<html class="theme-valido-white">
```

### 3. Use Theme Components

```html
<!-- Buttons -->
<button class="btn-primary">Primary Button</button>
<button class="btn-secondary">Secondary Button</button>

<!-- Cards -->
<div class="card">
    <h3 class="card-title">Card Title</h3>
    <p class="card-content">Card content</p>
</div>

<!-- Forms -->
<input type="text" class="form-input" placeholder="Enter text">
<select class="form-select">
    <option>Select option</option>
</select>
```

## Valido White Theme

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Primary | `#2563eb` | Main brand color, buttons, links |
| Success | `#059669` | Success states, confirmations |
| Warning | `#d97706` | Warnings, alerts |
| Danger | `#dc2626` | Errors, deletions |
| Info | `#0891b2` | Information, help text |

### CSS Custom Properties

```css
:root {
  --valido-primary: #2563eb;
  --valido-success: #059669;
  --valido-warning: #d97706;
  --valido-danger: #dc2626;
  --valido-info: #0891b2;
  --valido-bg-primary: #ffffff;
  --valido-text-primary: #1e293b;
  --valido-border: #e2e8f0;
}
```

### Components

#### Buttons
```html
<button class="btn-primary">Primary Action</button>
<button class="btn-success">Success Action</button>
<button class="btn-warning">Warning Action</button>
<button class="btn-danger">Danger Action</button>
```

#### Forms
```html
<div class="form-group">
    <label class="form-label">Label</label>
    <input type="text" class="form-input" placeholder="Enter text">
    <textarea class="form-textarea" rows="4"></textarea>
    <select class="form-select">
        <option>Option 1</option>
        <option>Option 2</option>
    </select>
</div>
```

#### Tables
```html
<table class="table">
    <thead>
        <tr>
            <th>Column 1</th>
            <th>Column 2</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Data 1</td>
            <td>Data 2</td>
        </tr>
    </tbody>
</table>
```

#### Cards
```html
<div class="card">
    <div class="card-header">
        <h3 class="card-title">Card Title</h3>
    </div>
    <div class="card-body">
        <p>Card content goes here</p>
    </div>
</div>
```

#### Navigation
```html
<nav class="navbar">
    <div class="navbar-brand">ValidoAI</div>
    <ul class="navbar-nav">
        <li><a href="#" class="nav-link">Home</a></li>
        <li><a href="#" class="nav-link active">Dashboard</a></li>
    </ul>
</nav>
```

#### Alerts
```html
<div class="alert alert-success">
    <strong>Success!</strong> Operation completed successfully.
</div>
<div class="alert alert-danger">
    <strong>Error!</strong> Something went wrong.
</div>
```

## Valido Dark Theme

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Primary | `#3b82f6` | Main brand color, buttons, links |
| Success | `#10b981` | Success states, confirmations |
| Warning | `#f59e0b` | Warnings, alerts |
| Danger | `#ef4444` | Errors, deletions |
| Info | `#06b6d4` | Information, help text |

### CSS Custom Properties

```css
:root {
  --valido-primary: #3b82f6;
  --valido-success: #10b981;
  --valido-warning: #f59e0b;
  --valido-danger: #ef4444;
  --valido-info: #06b6d4;
  --valido-bg-primary: #0f172a;
  --valido-text-primary: #f8fafc;
  --valido-border: #475569;
}
```

## Theme Integration

### Flask Integration

```python
# In your Flask app
from src.assets.asset_manager import theme_manager

# Set theme in template context
@app.context_processor
def inject_theme():
    return {
        'current_theme': 'valido-white',  # or 'valido-dark'
        'available_themes': theme_manager.get_available_themes()
    }
```

### Template Integration

```html
<!-- In your base template -->
<!DOCTYPE html>
<html lang="en" class="theme-{{ current_theme }}">
<head>
    <!-- Theme CSS will be loaded automatically -->
    {{ theme_manager.render_theme_css() | safe }}
</head>
<body>
    <!-- Your content -->
</body>
</html>
```

### JavaScript Theme Switching

```javascript
// Function to switch themes
function switchTheme(themeName) {
    // Remove current theme class
    document.documentElement.classList.remove('theme-valido-white', 'theme-valido-dark');

    // Add new theme class
    document.documentElement.classList.add(`theme-${themeName}`);

    // Save preference
    localStorage.setItem('valido-theme', themeName);
}

// Load saved theme on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('valido-theme') || 'valido-white';
    switchTheme(savedTheme);
});
```

## Advanced Features

### Custom Properties Override

You can override theme colors by setting CSS custom properties:

```css
.theme-valido-white {
  --valido-primary: #your-custom-color;
  --valido-bg-primary: #your-bg-color;
}
```

### Theme Variants

Create theme variants by extending the base themes:

```css
/* High contrast variant */
.theme-valido-white-high-contrast {
  --valido-text-primary: #000000;
  --valido-bg-primary: #ffffff;
  --valido-border: #000000;
}
```

### Component Customization

Override component styles for specific use cases:

```css
.theme-valido-white .custom-button {
  @apply bg-gradient-to-r from-blue-600 to-purple-600;
  @apply text-white font-bold py-3 px-6 rounded-lg;
  @apply transform hover:scale-105 transition-transform;
}
```

## Browser Support

### Desktop
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Mobile
- iOS Safari 14+
- Chrome Mobile 90+
- Firefox Mobile 88+

## Performance

### CSS Bundle Size
- Valido White: ~15KB
- Valido Dark: ~15KB
- Both themes combined: ~25KB (gzipped)

### Loading Strategy
- CSS loaded asynchronously
- Critical CSS inlined for above-the-fold content
- Theme switching without page reload

## Accessibility

### WCAG 2.1 Compliance
- ✅ Color contrast ratios meet AA standards
- ✅ Focus indicators clearly visible
- ✅ Keyboard navigation support
- ✅ Screen reader compatible
- ✅ Reduced motion support

### High Contrast Support
- Automatic detection of high contrast mode
- Enhanced focus indicators
- Improved color contrast

## Best Practices

### 1. Consistent Usage
```html
<!-- Good: Use semantic class names -->
<button class="btn-primary">Save Changes</button>

<!-- Avoid: Inline styles that break theme -->
<button style="background: red;">Save Changes</button>
```

### 2. Theme-Aware Components
```html
<!-- Good: Theme-aware alerts -->
<div class="alert alert-success">Success message</div>

<!-- Avoid: Hard-coded colors -->
<div style="background: green; color: white;">Success message</div>
```

### 3. Responsive Design
```html
<!-- Good: Responsive classes -->
<div class="card p-4 md:p-6 lg:p-8">
    <h3 class="text-lg md:text-xl lg:text-2xl">Title</h3>
</div>
```

### 4. Performance Optimization
```html
<!-- Good: Use theme utilities -->
<div class="bg-gradient-primary text-white p-4 rounded-lg">
    Content with gradient background
</div>
```

## Troubleshooting

### Common Issues

#### 1. Theme Not Loading
**Problem:** Theme styles not applied
**Solution:**
- Check if theme CSS is loaded
- Verify theme class is applied to html element
- Check browser console for errors

#### 2. Inconsistent Colors
**Problem:** Colors don't match theme
**Solution:**
- Use theme-aware classes instead of hard-coded colors
- Check CSS custom property values
- Verify theme class is applied correctly

#### 3. Mobile Issues
**Problem:** Layout breaks on mobile
**Solution:**
- Use responsive Tailwind classes
- Test with browser dev tools
- Check viewport meta tag

### Debug Mode

Enable debug mode to see theme information:

```javascript
// In browser console
console.log('Current theme:', document.documentElement.className);
console.log('Available themes:', window.availableThemes);
```

## Contributing

### Adding New Components
1. Create component styles in theme files
2. Use Tailwind classes for consistency
3. Test in both light and dark themes
4. Document usage examples

### Theme Customization
1. Fork the theme files
2. Modify CSS custom properties
3. Test across all components
4. Update documentation

## Changelog

### Version 1.0.0
- Initial release
- Valido White and Dark themes
- Complete component library
- Accessibility features
- Performance optimizations

---

**Valido Themes** - Professional themes for modern business applications.
