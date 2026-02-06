# CSV Format Specification

Google Ads Editor compatible CSV format for Performance Max asset groups.

## Required Columns

| Column | Description | Required |
|--------|-------------|----------|
| Campaign | Campaign name | Yes |
| Asset Group | Asset group name | Yes |
| Asset Type | Type of asset | Yes |
| Asset Value | The actual content | Yes |

## Asset Types

The following Asset Type values are used:

| Asset Type | Character Limit | Quantity per Group |
|------------|----------------|-------------------|
| Headline 1-15 | 30 | Up to 15 |
| Long Headline 1-5 | 90 | Up to 5 |
| Description 1-5 | 90 | Up to 5 |
| Business Name | 25 | 1 per campaign |
| Call to Action | N/A | 1 per group |
| Final URL | N/A | 1 per group |
| Image Prompt | N/A | 1+ per group |

## CSV Structure Example

```csv
Campaign,Asset Group,Asset Type,Asset Value
[Campaign Name] - PMax,[Asset Group Name],Headline 1,[30 char max headline]
[Campaign Name] - PMax,[Asset Group Name],Headline 2,[30 char max headline]
[Campaign Name] - PMax,[Asset Group Name],Headline 3,[30 char max headline]
...
[Campaign Name] - PMax,[Asset Group Name],Headline 15,[30 char max headline]
[Campaign Name] - PMax,[Asset Group Name],Long Headline 1,[90 char max long headline]
[Campaign Name] - PMax,[Asset Group Name],Long Headline 2,[90 char max long headline]
...
[Campaign Name] - PMax,[Asset Group Name],Long Headline 5,[90 char max long headline]
[Campaign Name] - PMax,[Asset Group Name],Description 1,[90 char max description]
[Campaign Name] - PMax,[Asset Group Name],Description 2,[90 char max description]
...
[Campaign Name] - PMax,[Asset Group Name],Description 5,[90 char max description]
[Campaign Name] - PMax,[Asset Group Name],Business Name,[25 char max business name]
[Campaign Name] - PMax,[Asset Group Name],Call to Action,[CTA text]
[Campaign Name] - PMax,[Asset Group Name],Final URL,[Full URL]
[Campaign Name] - PMax,[Asset Group Name],Image Prompt,[Image generation prompt]
```

## Asset Group Naming Convention

Format: `[FUNNEL STAGE] - [THEME] - [OFFER or ACTION]`

Examples:
- `TOF - Sports Recovery - Learn More`
- `TOF - Back Pain Education - Find Out More`
- `MOF - Our Approach - Check Availability`
- `MOF - Treatment Process - See How It Works`
- `BOF - Free Consult - Book Now`
- `BOF - New Patient Offer - Call Today`

## Call to Action Options

PMax supports these CTAs:

**TOF (Awareness):**
- Learn more
- Find out more
- Get info

**MOF (Consideration):**
- Check availability
- See how it works
- Get details

**BOF (Action):**
- Book online
- Book now
- Call now
- Get quote
- Sign up
- Contact us

## Character Validation Rules

Before output, validate:

1. **Headlines**: <= 30 characters each
2. **Long Headlines**: <= 90 characters each
3. **Descriptions**: <= 90 characters each
4. **Business Name**: <= 25 characters

Count excludes leading/trailing whitespace.

## Full CSV Example

```csv
Campaign,Asset Group,Asset Type,Asset Value
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 1,Sports Physio Bondi
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 2,Recovery Support
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 3,Move Better Today
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 4,Athlete Care Bondi
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 5,Professional Physio
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 6,AHPRA Registered Team
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 7,Sports Injury Support
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 8,Your Recovery Journey
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 9,Bondi Physio Team
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 10,Movement Assessment
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 11,Evidence-Based Care
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 12,Personalised Approach
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 13,Qualified Physios
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 14,Local Sports Physio
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 15,Physio Near Bondi
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Long Headline 1,Professional sports physiotherapy helping Bondi athletes move with confidence
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Long Headline 2,AHPRA registered physiotherapists supporting your recovery journey
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Long Headline 3,Discover evidence-based physiotherapy for sports injuries and movement
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Long Headline 4,Personalised assessment and treatment plans for every body
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Long Headline 5,Your local Bondi physio team helping you move better every day
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Description 1,AHPRA registered physiotherapists offering personalised sports injury assessments.
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Description 2,Learn how evidence-based physiotherapy may help support your recovery goals.
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Description 3,Professional movement assessment from experienced Bondi physiotherapists.
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Description 4,Helping Bondi locals move with confidence through tailored physio care.
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Description 5,Discover our approach to sports physiotherapy and injury rehabilitation.
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Business Name,Bondi Physio
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Call to Action,Learn more
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Final URL,https://bondiphysio.com.au/sports-physio
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Image Prompt,"Scene: Modern clinical treatment room with natural light. Subject: Female physiotherapist in professional attire consulting with athletic patient. Mood: Professional, supportive, calm. Lighting: Soft natural daylight from large window. Composition: Medium shot showing both practitioner and patient in conversation. Style: Realistic professional photography. Negative prompt: no before/after, no text, no logos, no pain expressions, no medical procedures, no extreme poses."
```

## Output File Naming

Format: `pmax-assets-[client-slug]-[YYYY-MM-DD].csv`

Examples:
- `pmax-assets-bondi-physio-2025-01-30.csv`
- `pmax-assets-sydney-chiro-2025-02-15.csv`

## Import Notes

When importing to Google Ads Editor:
1. Use "Import" > "From CSV"
2. Select the generated file
3. Review asset groups before publishing
4. Upload generated images separately
5. Match images to corresponding asset groups
