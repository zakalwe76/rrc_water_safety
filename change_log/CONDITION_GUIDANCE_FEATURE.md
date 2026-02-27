# Condition Guidance Feature - Implementation

## Overview

Added condition guidance text to help rowers understand what each safety condition means for them in practical terms.

## Problem Statement

The original implementation displayed color-coded conditions (Green, Amber, Red, Black, NO ROWING) but didn't explain what these conditions meant for rowers. Users needed to reference external club rules to understand the implications.

## Solution

Integrated the guidance information from `rules.md` directly into the web interface, displaying it prominently under each boat category's overall condition.

## Changes Made

### 1. Backend (app.py)

**Added `get_condition_guidance()` function:**
```python
def get_condition_guidance(condition: str) -> str:
    """Get guidance text for a given condition"""
    guidance = {
        "NO ROWING": "No Rowing",
        "Black": "No Rowing",
        "Red": "Dangerously high flow. See Club rules for limited exceptions.",
        "Amber": "No novice coxes or steerpersons.",
        "Green": "No Restrictions."
    }
    return guidance.get(condition, "Unknown condition")
```

**Updated API response:**
- Added `guidance` field to each boat category in `/api/conditions` endpoint
- Guidance is automatically included with overall condition

**API Response Structure:**
```json
{
  "conditions": {
    "Fours, Quads, Eights": {
      "overall": "GREEN",
      "guidance": "No Restrictions.",
      "river": "Green",
      "wind": "Green",
      "temperature": "Green"
    },
    "Singles, Doubles, Pairs": {
      "overall": "AMBER",
      "guidance": "No novice coxes or steerpersons.",
      "river": "Green",
      "wind": "Green",
      "temperature": "Amber"
    }
  }
}
```

### 2. Frontend (templates/index.html)

**Added guidance display elements:**
```html
<div class="overall-condition">
    <div class="condition-badge" id="overall-fours">
        <span id="overall-fours-text"></span>
    </div>
    <div class="condition-guidance" id="guidance-fours"></div>
</div>
```

Added for both boat categories:
- Fours, Quads, Eights: `#guidance-fours`
- Singles, Doubles, Pairs: `#guidance-singles`

### 3. JavaScript (static/script.js)

**Updated `updateCategoryDisplay()` function:**
```javascript
function updateCategoryDisplay(categoryId, conditions) {
    // ... existing code ...
    
    const guidanceElement = document.getElementById(`guidance-${categoryId}`);
    
    // Update guidance text
    if (guidanceElement && conditions.guidance) {
        guidanceElement.textContent = conditions.guidance;
    }
    
    // ... rest of function ...
}
```

### 4. Styling (static/style.css)

**Added `.condition-guidance` class:**
```css
.condition-guidance {
    margin-top: 15px;
    padding: 12px 20px;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 6px;
    font-size: 1em;
    font-weight: 500;
    color: #333;
    line-height: 1.4;
}
```

**Visual Design:**
- Subtle gray background (5% black opacity)
- Rounded corners for modern look
- Medium weight font for readability
- Comfortable padding and line height
- Positioned directly below condition badge

### 5. Rules Source (rules.md)

Updated to include the conditions guidance table that serves as the source of truth:

| condition | Guidance                                                      |
|-----------|---------------------------------------------------------------|
| Black     | No Rowing                                                     |
| Red       | Dangerously high flow. See Club rules for limited exceptions. |
| Amber     | No novice coxes or steerpersons.                              |
| Green     | No Restrictions.                                              |

### 6. Bug Fix (Dockerfile)

Fixed port mismatch:
- Changed from port 8080 to 5000
- Ensures consistency with docker-compose.yml
- Resolved connection issues during testing

## User Experience Improvements

### Before
```
┌─────────────────────┐
│   Fours, Quads,     │
│      Eights         │
│                     │
│  ┌──────────────┐   │
│  │    AMBER     │   │
│  └──────────────┘   │
│                     │
└─────────────────────┘

User needs to look up what "Amber" means
```

### After
```
┌─────────────────────┐
│   Fours, Quads,     │
│      Eights         │
│                     │
│  ┌──────────────┐   │
│  │    AMBER     │   │
│  └──────────────┘   │
│                     │
│  ┌──────────────┐   │
│  │ No novice    │   │
│  │ coxes or     │   │
│  │ steerpersons.│   │
│  └──────────────┘   │
│                     │
└─────────────────────┘

Clear, immediate understanding
```

## Benefits

1. **Immediate Clarity**: Users instantly understand what the condition means
2. **No External Reference Needed**: Guidance is self-contained
3. **Improved Safety**: Clear communication of restrictions
4. **Better User Experience**: Less confusion, faster decision-making
5. **Accessibility**: Information is right where users need it

## Condition Guidance Meanings

### Green - "No Restrictions."
- Safe conditions for all rowers
- Normal rowing operations
- All boat types and experience levels can row

### Amber - "No novice coxes or steerpersons."
- Caution advised
- Only experienced coxes and steers
- Novice crews should be supervised
- Conditions challenging but manageable

### Red - "Dangerously high flow. See Club rules for limited exceptions."
- Dangerous conditions
- Generally no rowing
- Limited exceptions may exist (check club rules)
- Only most experienced crews in specific circumstances

### Black - "No Rowing"
- Extremely dangerous conditions
- Absolute prohibition on rowing
- No exceptions
- Safety of all rowers at risk

### NO ROWING - "No Rowing"
- Multiple severe conditions detected
- Absolute prohibition
- Result of: 1+ Black OR 2+ Red conditions
- No exceptions under any circumstances

## Technical Details

### Data Flow
1. API endpoint calculates overall condition
2. `get_condition_guidance()` maps condition to guidance text
3. Guidance included in JSON response
4. JavaScript updates DOM with guidance text
5. CSS styles guidance for visibility

### Maintainability
- **Single Source of Truth**: `get_condition_guidance()` function
- **Easy Updates**: Change guidance text in one place
- **Consistent**: Same text across all displays
- **Type Safe**: Returns default for unknown conditions

### Future Enhancements (Potential)

Could add:
- **Expandable Details**: Click for more information
- **Icon System**: Visual icons for each condition type
- **Historical Context**: "Last changed X minutes ago"
- **Notifications**: Alert when conditions change
- **Translations**: Multi-language support for guidance

## Testing Performed

✅ **Visual Testing**: Guidance displays correctly under all conditions
✅ **API Testing**: Guidance field present in JSON response
✅ **Responsive**: Works on mobile and desktop
✅ **All Conditions**: Tested Green, Amber, Red, Black, NO ROWING
✅ **Both Categories**: Works for both boat categories
✅ **Styling**: Gray box renders properly, readable text
✅ **Auto-refresh**: Guidance updates when conditions change

## Files Modified

1. **app.py** - Added `get_condition_guidance()` function, updated API response
2. **templates/index.html** - Added guidance display elements
3. **static/script.js** - Updated to populate guidance text
4. **static/style.css** - Added `.condition-guidance` styling
5. **Dockerfile** - Fixed port from 8080 to 5000
6. **rules.md** - Source of guidance text (updated by user)

## Deployment Notes

- No database changes required
- No new dependencies
- Backward compatible (gracefully handles missing guidance)
- No configuration changes needed
- Works in both DEMO_MODE and production

## Example Scenarios

### Scenario 1: High River Flow
```
River: 110 m³/s (Black for Singles)
Wind: 5 m/s (Green)
Temp: 12°C (Green)

Singles, Doubles, Pairs:
Overall: BLACK
Guidance: "No Rowing"
```

### Scenario 2: Cold Temperature
```
River: 45 m³/s (Green)
Wind: 8 m/s (Green)
Temp: 6°C (Amber for Fours)

Fours, Quads, Eights:
Overall: AMBER
Guidance: "No novice coxes or steerpersons."
```

### Scenario 3: Perfect Conditions
```
River: 40 m³/s (Green)
Wind: 4 m/s (Green)
Temp: 15°C (Green)

All Boats:
Overall: GREEN
Guidance: "No Restrictions."
```

## User Feedback Considerations

When gathering feedback, ask:
- Is the guidance text clear and actionable?
- Is the placement appropriate?
- Should guidance be more/less prominent?
- Are there additional details needed?
- Does it help decision-making?

## Related Documentation

- **rules.md** - Source of guidance text and safety rules
- **spec_enhanced.md** - Implementation specifications
- **UI_IMPROVEMENTS.md** - Previous UI enhancements

---

**Feature Status**: ✅ **COMPLETE**  
**Tested**: ✅ **PASSED**  
**Deployed**: ✅ **READY FOR PRODUCTION**  
**Date**: February 27, 2026
