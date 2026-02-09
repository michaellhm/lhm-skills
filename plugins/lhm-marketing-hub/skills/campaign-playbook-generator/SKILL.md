---
name: campaign-playbook-generator
description: "Transform client conversation transcripts into comprehensive Campaign & Sales Playbooks. Use this when the user uploads client transcripts, ChatGPT conversations, or interview notes and wants to create a strategic playbook. Also use when the user mentions 'build a playbook', 'campaign playbook', 'sales playbook', 'brand guidelines from transcript', or 'convert conversation to playbook'. This skill creates the McDonald's-style reference guide for marketing and client-facing teams, ensuring that every single interaction reflects the founder's values, vision, and mission consistently."
---

# Campaign Playbook Generator

Transform client conversation transcripts into comprehensive, strategic Campaign & Sales Playbooks that serve as the definitive reference for creative, marketing, and client-facing teams.

## Purpose

Campaign Playbooks are "McDonald's-style" strategic reference guides. Just as McDonald's ensures every location delivers the same experience through detailed playbooks, these documents ensure consistency, authenticity, and excellence across all touchpoints. Every piece of content, every client interaction, and every marketing campaign should reflect the founder's values, vision, and unwavering commitment to transforming lives.

## Workflow

### Step 1: Gather Context

**Check for existing client_profile.md:**
- Read `client_profile.md` if it exists in the current folder
- This provides baseline business information
- Note any gaps to fill from transcripts

**Identify transcript files:**
- Ask user which files contain the conversation transcripts
- Accept multiple files (conversations often span several documents)
- Common formats: `.txt`, `.md`, `.pdf`, `.docx`
- User might say: "These three files" or "All the uploaded documents"

**Read all transcript files thoroughly:**
- Read each file completely (don't skim)
- Take detailed notes as you read
- Pay attention to emotional language, repeated phrases, and stories
- Notice what the founder is passionate about
- Identify gaps where information is missing

### Step 2: Extract Core Information

As you read transcripts, extract and organize information into these categories. If something isn't mentioned, note it as a gap.

#### Business Foundation
- Business name and industry
- Founder's name and background
- Founder's personal story (why they started this business)
- Business origin story
- Mission statement (explicit or implied from conversation)
- North Star / tagline / big audacious promise
- Core values (stated directly or demonstrated through how they talk)

#### Brand Identity
- Brand personality traits (how they describe themselves)
- Voice and tone preferences
- Words and phrases the founder uses frequently
- Words and phrases they avoid or express dislike for
- Alternatives to overused industry terms
- How they want people to communicate with customers

#### Target Audience
- Primary audience (demographics, psychographics, pain points)
- Secondary audiences
- Who they DON'T target (exclusions matter)
- Where ideal customers are in their journey when they find the business

#### Customer Psychology
- Primary concerns and fears
- Emotional state when customers find them
- Detailed pain points
- What keeps customers up at night
- Common objections
- Hesitations that prevent purchase

#### Solutions & Differentiators
- How they address each customer concern
- Unique selling propositions
- What makes them different from competitors
- Proof points (certifications, partnerships, methodology, authority figures)
- Treatment/product/service philosophy

#### Social Proof
- Testimonial themes mentioned
- Success story categories
- Transformation examples
- Customer feedback patterns
- Story categories to collect more of

#### Product/Service Details
- Core offerings
- Service or product tiers
- Pricing philosophy (if mentioned)
- Delivery model
- Guarantees or promises made

#### Sales Approach
- Sales philosophy and ethos
- How salespeople should behave
- Discovery questions they use
- Objection handling approaches
- Sample scripts or responses
- What should NEVER be said to customers

#### Marketing Strategy
- Positioning strategy
- Content pillars
- SEO targets (if mentioned)
- Ad platform preferences
- Website principles
- Design/branding direction
- Calls to action

#### Compliance & Regulations
- Industry regulatory body (AHPRA, TGA, ASIC, etc.)
- Specific compliance requirements
- Words to avoid for regulatory reasons
- Claims that cannot be made
- How to phrase benefits compliantly

### Step 3: Detect Industry & Apply Compliance Framework

Based on business type, automatically determine applicable regulations and build guardrails into the playbook.

**Australian Healthcare (AHPRA):**
- Triggers: Physiotherapy, chiropractic, osteopathy, podiatry, psychology, counseling, optometry, ophthalmology, dentistry, orthodontics, Chinese medicine, naturopathy
- Avoid: "cure", "guaranteed", outcome promises, before/after photos for therapeutic claims
- Use: "may help", "could assist", evidence-based language, focus on process not outcomes
- Include: "AHPRA-compliant messaging" section in guardrails

**Medical Devices/Treatments (TGA):**
- Triggers: Medical equipment, adjustable beds (if marketed for health), therapeutic products, diagnostic tools
- Avoid: Miracle cure claims, absolute promises of outcomes
- Use: "Australian Registered Medical Device", "may help", "could assist" compliance language
- Include: TGA compliance notes in guardrails

**Financial Services (ASIC):**
- Triggers: Financial advice, investment services, wealth management
- Avoid: Guaranteed returns, "get rich" claims
- Include: Appropriate disclaimers about risk, past performance
- Include: ASIC compliance section

**General Business (Consumer Law):**
- All other businesses
- Standard Australian Consumer Law compliance
- Honest representation, no misleading claims
- Include: Basic consumer law guardrails

### Step 4: Generate Campaign Playbook Structure

Create the playbook using this exact template. Fill in sections from transcript analysis. If information is missing, explicitly note gaps with **[To be determined]** or **[Question for Founder]**.

```markdown
# [Business Name] — Master Campaign & Sales Playbook

## PURPOSE OF THIS DOCUMENT

This strategic reference guide serves as the definitive resource for creative, marketing, and client-facing teams at [Business Name]. Every piece of content, every [customer] interaction, every marketing campaign, and every business decision should reflect [Founder]'s values, vision, and unwavering commitment to [mission statement]. This is our "McDonald's-style" playbook, the blueprint that ensures consistency, authenticity, and excellence across all touchpoints.

## WHO IS [BUSINESS NAME]?

[Business overview - what they do, core services/products, unique positioning]

[If multiple locations or service areas, include geographic details]

[Business model details - e.g., "Operating across eight clinics (seven in NSW, one in Melbourne)" or "Online-only, delivering across QLD, NSW, VIC"]

## ABOUT THE FOUNDER / OWNER

[Founder Name] is [role - e.g., "the heart, soul, and driving force behind [Business Name]"]

### Their Story, In Their Words

[Include direct quotes from transcripts that capture their personal journey]

**Quote:** *"[Powerful quote about why they started this]"*

[Narrative of their journey - challenges faced, pivotal moments, what led them to this work]

[If they had personal experience with the problem they solve, highlight it]

### Their Philosophy

**Quote:** *"[Core belief about how to serve customers]"*

[What matters most to them in how they run the business]

[Their non-negotiables]

### Their Values in Action

[Specific examples from the transcript of how they live their values]

[Stories that demonstrate their commitment - e.g., "She and Dr. Toyos provided $10,000 worth of free treatment to a struggling nine-year-old patient"]

### Their Disruptive Spirit

**Quote:** *"[Quote about challenging status quo]"*

[What they do differently than everyone else in their industry]

[What frustrates them about competitors]

[How they're leading change]

### Their Promise to [Customers]

**Quote:** *"[The commitment they make to every customer - direct quote if possible]"*

[Explanation of this promise and why it matters]

## WHY [BUSINESS] EXISTS: MISSION, NORTH STAR, & VALUES

### Vision (Blue Sky Goal)

*[The long-term world they want to create]*

**Example:** "To create a world where no one suffers alone with [condition], where, with the right care, there will come a day you won't remember what it was like to live this way."

### Corporate Mission Statement (How We Deliver — Professional Tone)

*[Formal mission statement - craft from conversation or use provided version]*

**Example:** "[Business Name] delivers holistic, proven care for [condition] through globally recognized protocols, advanced diagnostics, and compassionate support. We go beyond symptom management to address root causes, restore quality of life, and expand a centre of excellence that empowers every [customer]'s journey."

### Mission from the Heart (How We Deliver — Values Tone)

*[More emotional, personal version of the mission]*

**Example:** "At [Business Name], we welcome and support every person with genuine care and compassion. We disrupt tired old healthcare systems by treating the whole person (body, mind, and spirit) through world-class protocols and heartfelt connection. Our mission is to restore hope, renew quality of life, and ensure no one feels dismissed or unseen again."

### North Star (Anchor Promise)

**"[The one-line promise or tagline that anchors everything]"**

**Example:** "There will come a day when you won't remember what it was like to live like this."

[Explain significance: This isn't just a tagline, it's [Founder]'s personal promise to every [customer], grounded in [their experience/expertise]]

### Core Values

1. **[Value 1 - e.g., Integrity & Transparency]** - [Description: Always choosing honesty over convenience, even when it's difficult]
2. **[Value 2 - e.g., Holistic, Whole-Person Care]** - [Description: Treating root causes, not just symptoms, and addressing inflammation throughout the body]
3. **[Value 3 - e.g., Accessibility]** - [Description: Making world-class care available to as many people as possible]
4. **[Value 4 - e.g., Excellence in Care & Technology]** - [Description: Global leadership; growing centre of excellence; locally delivered with best-in-class, Toyos-approved technology]
5. **[Value 5 - e.g., Compassionate [Customer] Experience]** - [Description: Every [customer] feels genuinely cared for and never dismissed]

### Regulatory Considerations

[Business Name] operates under [REGULATORY BODY - e.g., AHPRA / TGA / ASIC] compliance requirements.

**Messaging guardrails:**
- Avoid claims of "cure" - emphasise "symptom-free living" and "management"
- Use "evidence-based" rather than unsubstantiated claims
- Focus on "holistic treatment" and "root cause approach"
- Emphasise "protocols" and "global validation"
- Frame outcomes as patient experiences, not guarantees

## BRAND PERSONALITY & VOICE

### Brand Personality

If [Business Name] were a person, it would be:

- **[Trait 1 - e.g., Warm & Loving]** - Genuinely caring, never dismissive
- **[Trait 2 - e.g., Powerful & Strong]** - Confident in capabilities, unwavering in mission
- **[Trait 3 - e.g., Compassionate & Considerate]** - Understanding [customer] struggles deeply
- **[Trait 4 - e.g., Intelligent & Genius]** - Evidence-based, scientifically grounded
- **[Trait 5 - e.g., Disruptive & Trailblazing]** - Challenging the status quo, leading change
- **[Trait 6 - e.g., Unwavering]** - Consistent in values and approach
- **[Trait 7 - e.g., Big Presence]** - A movement, not just a [business type]

### Voice & Tone

**Written Communication:**
- Warm but authoritative
- Educational without being condescending
- Honest about challenges and realistic about timelines
- Hopeful and encouraging
- Evidence-based and scientific when appropriate
- Conversational and accessible

**Words to Use:**
- [List of preferred words from transcripts - e.g., "Holistic, evidence-based protocols, validated"]
- [e.g., "Soothe, support, empower, transform"]
- [e.g., "Journey, wellness, root cause"]
- [e.g., "Centre of excellence, global leadership"]
- [e.g., "Community, family, movement"]

**Words to Avoid:**
- [e.g., "Quick fix, instant results, miracle cure"]
- [e.g., "Cheap, affordable (we're not the cheapest, but worth it)"]
- [e.g., "Pushy sales language"]
- [e.g., "Generic medical jargon without explanation"]

**Alternatives to "Evidence-Based"** *(keeps credibility but allows softer/more approachable language)*:
- Proven
- Validated
- Trusted
- Science-backed
- Clinically informed
- Well-researched
- Globally recognized
- Protocol-driven
- Grounded in science
- Backed by expertise

**Tone in [Customer] Interactions:**
- Lead with empathy and understanding
- Acknowledge their frustration and journey
- Provide hope grounded in reality
- Educate without overwhelming
- Soothe before selling

## TARGET AUDIENCE

### Primary Audience

**[Detailed description of ideal customer]**

**Example:** "Everyone aged 7+ living with or at risk of [condition], specifically:
- People with autoimmune or inflammatory conditions ([specific conditions])
- Women experiencing hormonal or menopausal changes
- Post-surgical patients ([specific surgeries])
- Patients on medications linked to [condition] ([specific medications])
- Office workers exposed to air conditioning and screens
- Higher-risk individuals seeking preventative care before symptoms develop"

### Secondary Audience

**[Other audiences worth targeting]**

**Example:**
- Patients with [related condition] (90%+ develop [primary condition])
- Those with [other related conditions]
- Patients with [complications linked to primary issue]"

### We Do Not Target

[Important exclusions - who is not a good fit and why]

**Example:** "We welcome all [customers]. However, those unwilling to participate in their own wellness journey (diet, lifestyle, habit changes) may not be ready for our holistic approach. Our treatment is not a quick fix; it's a 6-12 month journey to wellness with long-term maintenance."

## CUSTOMER CONCERNS

### The [Customer]'s Emotional Journey

When [customers] find us, they are typically:

- **[Emotional State 1]** - [Description]
- **[Emotional State 2]** - [Description]
- **[Emotional State 3]** - [Description]
- **[Emotional State 4]** - [Description]
- **[Emotional State 5]** - [Description]

**Quote from Founder:** *"[Powerful quote about customer psychology/emotional state]"*

### Primary Concerns

1. **[Concern 1 - e.g., Cost]** - "I can't afford this treatment"
2. **[Concern 2 - e.g., Hope & Recovery]** - "Will I ever get better?"
3. **[Concern 3 - e.g., Safety]** - "Is [treatment] dangerous?"
4. **[Concern 4 - e.g., Effectiveness]** - "I've had [treatment] before, it didn't work"
5. **[Concern 5 - e.g., Being Taken Seriously]** - "Will they actually listen to me?"
6. **[Concern 6 - e.g., Quality of Life Impact]** - "Will I be able to work/travel/live normally?"

## HOW THE BUSINESS ADDRESSES THOSE CONCERNS

### Our Comprehensive Approach

**[Concern 1 - e.g., Cost]:**
- **Truth-first approach:** Even the assessment alone provides valuable tools to slow disease progression
- **No pressure tactics:** "If they can't afford treatment, no pressure, but many return later"
- **Community giving program** for those truly in need
- **Reframe:** The long-term cost of untreated disease is far greater

**[Concern 2 - e.g., Hope & Recovery]:**
- **Our signature promise:** *"[North Star quote]"*
- **Real [customer] outcomes and testimonials**
- **Clear explanation of the journey:** 6-12 months to wellness, then maintenance
- **Evidence:** Show the science, share success stories

**[Concern 3 - e.g., Safety]:**
- **Reframe:** [Treatment] as benefits: photo-facial rejuvenation (clearer skin, fewer wrinkles, more even tone)
- **Explain the difference:** "It may not have been done correctly. We follow [Authority Figure]'s proven global protocols, not generic manufacturer settings"
- **[Authority Figure]-approved technology and techniques**

**[Concern 4 - e.g., Effectiveness]:**
- **Protocol differences matter:** Not all [treatment] is created equal - [specific methodology] is the only protocol with FDA approval for [condition]
- **Explain methodology:** Show why our approach works when others don't

**[Concern 5 - e.g., Being Heard & Supported]:**
- **"You're not alone"** - Immediate community and support network
- **The comprehensive first call** focused on soothing and understanding
- **Psychological referrals when needed**
- **"Once a [customer], always a [customer]"** - lifelong support

### Our Unique Differentiators

1. **[Differentiator 1]** - [Description]
2. **[Differentiator 2]** - [Description]
3. **[Differentiator 3]** - [Description]
4. **[Differentiator 4]** - [Description]
5. **[Differentiator 5]** - [Description]

## KEY TESTIMONIALS AND STORY THEMES

### Consistent [Customer] Feedback Themes

**[Theme 1 - e.g., Professional & Expert]:**
- "More progress in one appointment than 2 years elsewhere"
- "Trained directly by the inventor of [treatment], it shows in the results"

**[Theme 2 - e.g., Compassionate & Patient-Centred]:**
- "They listened when no one else would"
- "Finally felt heard and understood"

**[Theme 3 - e.g., Life-Changing]:**
- "I thought I'd live this way forever. Now I'm symptom-free"
- "Changed my entire quality of life"

### Story Categories We Should Collect More Of:

- Independence restored (e.g., mobility regained, returning to activities)
- Professional life saved (e.g., able to continue working, career preserved)
- Social/family reconnection (e.g., seeing friends/family again, participating in life)
- Hope after desperation (e.g., tried everything else, found us, finally got relief)
- "Above & beyond" service stories (e.g., [Founder/team] going the extra mile)
- Complex case successes (e.g., difficult diagnosis, multiple conditions, finally solved)

**[RECOMMENDATION: Record more [customer] success stories and use AI to analyse themes for content creation]**

**Remember:** These stories can be shared verbally, in person, and with the team, but they cannot be showcased publicly and in our communications. [Include if AHPRA-regulated]

## PRODUCT OVERVIEW & COMPARISON

### Core Services

**[Primary Service/Product]:**
- [Description]
- [Duration/format]
- [What's included]
- [Key benefits]

**[Secondary Services]:**
- [List]

**[Additional Services]:**
- [List]

### Service Model / Delivery

- [How services are delivered - e.g., "Comprehensive 45-minute assessment"]
- [Service area - e.g., "Eight clinics (seven in NSW, one in Melbourne)"]
- [Unique elements - e.g., "Free delivery, installation, old bed removal"]

### Competitive Comparison

[If competitor details were discussed, create comparison table]

| Feature | [Business Name] | [Competitor Type A] | [Competitor Type B] |
|---------|-----------------|---------------------|---------------------|
| [Feature 1] | [Details] | [Details] | [Details] |
| [Feature 2] | [Details] | [Details] | [Details] |
| [Feature 3] | [Details] | [Details] | [Details] |

**Questions for [Founder] / Gaps to Fill:**
- [List product/service details not mentioned in transcripts]

## HOW TO SELL OUR OFFERING: THE [BUSINESS] PHILOSOPHY

### Our Core Sales Philosophy

**Quote:** *"[Direct quote capturing sales ethos]"*

**Example:** "We don't do sales, we help people. Like a lighthouse, we shine brightly, and [customers] come to us. It's attraction, not pursuit."

### The [Metaphor] Principle

[If founder used a metaphor for their sales approach, expand on it]

**Example:** "We don't chase [customers]. Instead, we:
- Shine our expertise brightly through education
- Attract those ready for real solutions
- Welcome everyone who seeks our help
- Never pressure or push"

### Sales Approach Principles

1. **[Principle 1 - e.g., Listen First]** - Always start with "What's going on with your [issue]?"
2. **[Principle 2 - e.g., Soothe Before Selling]** - Address their emotional and physical needs first
3. **[Principle 3 - e.g., Educate, Don't Pressure]** - Information empowers choice
4. **[Principle 4 - e.g., Truth & Transparency]** - Honest about timelines, costs, and expectations
5. **[Principle 5 - e.g., Support for Life]** - "Once a [customer], always a [customer]"

### Discovery Questions for Every [Customer/Lead]

**Opening Questions:**
- "What's going on with your [issue]?"
- "What are your symptoms?"
- "How is it affecting your quality of life?"

**Assessment Questions:**
- "Who have you seen already?"
- "What drops/treatments are you using?"
- "Are you using [common incorrect advice]?" (Often incorrect advice)
- "What's your lifestyle, diet, and general health like?"
- "Do you have any inflammatory conditions?"
- "What's your support network like?"
- "Do you get enough sunlight?"

**Understanding Impact:**
- "How is this affecting your work?"
- "What activities have you had to stop?"
- "How is your family handling this?"

### Sample Scripts and Responses

**First Call Opening:**

"Thank you for calling [Business Name]. Before I tell you about what we do, can you help me understand what's going on with your [issue]?"

**After They Share Their Story:**

"I can hear the frustration in your voice, and I want you to know that what you're experiencing is real, it's valid, and most importantly, there is hope. Let me start by giving you something that might help right now..."

**[Addressing Common Incorrect Advice]:**

"I know you've probably been told to use [common treatment], but with [Condition], we're dealing with [root cause], your [affected area] are already [problem state]. We recommend [correct approach] instead. Our goal is to soothe the [area], not add more heat."

**The Hope Message:**

"I want to tell you something that might be hard to believe right now, but I've said this to thousands of [customers] who have cried on the phone to me, 'There will come a time when you won't remember what it's like to live like this.' And they think I'm mad. But I can guarantee there will come a time when they'll ring me up or send me a message, or the next time I see them, they'll say, 'Oh, my God, you were right. I forgot to put [treatment] in yesterday, it's the first time in 10 years.'"

**Addressing Cost Concerns:**

"I understand cost is a concern. Here's what I want you to know: if left untreated, this disease will cost you more in the long term, not just financially, but in quality of life. Even our assessment alone gives you tools to slow the progression. And if you're not ready for treatment now, that's okay. We'll be here when you are."

**Explaining Our Difference:**

"You mentioned you've had [treatment] before, and it didn't work. That's not uncommon, and it may not have been done correctly. We follow [Authority Figure]'s proven global protocols; he's the inventor of [treatment] for [Condition] treatment. We don't use generic manufacturer settings; we use protocols refined over 26 years of treating [customers] worldwide."

### Objection Handling

**"It's too expensive"**
- Acknowledge the concern genuinely
- Explain the long-term cost of untreated disease
- Highlight the value of the assessment alone
- No pressure if they're not ready

**"I've tried everything"**
- Validate their frustration
- Explain why previous treatments may have failed
- Share success stories of similar [customers]
- Offer hope based on our different approach

**"[Treatment] didn't work for me before"**
- Explain protocol differences
- Discuss [Authority Figure] methodology
- Offer to assess what went wrong previously

**"Is it safe?"**
- Explain the safety profile
- Reframe side effects as benefits (e.g., skin improvement)
- Share our experience and training

### The [Assessment/Consultation] Invitation

"Based on what you've told me, I think our comprehensive assessment would be really valuable for you. It's a [duration]-minute session where we'll conduct detailed imaging of your [area], analyse your [specific elements], and create a personalised plan. Even if you decide not to proceed with treatment, you'll leave with tools and knowledge to help manage your condition. Would you like to book that in?"

**[RECOMMENDATION: Record actual [customer] calls with [Founder] and [Team] to expand the script library using AI analysis]**

## EXTERNAL MESSAGING GUARDRAILS

This playbook is primarily intended for **internal education and briefing purposes**.

Not all language in this document is suitable for use in external marketing or [customer]-facing communication. The following guardrails ensure compliance with [REGULATORY BODY] standards and protect the integrity of [Business Name]'s public messaging.

### Do Not Use Externally

- **[Customer] testimonials or quotes** [if AHPRA/TGA regulated]
  - Examples: "Changed my entire quality of life," "Now I'm symptom-free"
- **Before/after imagery** [if therapeutic claims]
- **Guarantees of outcomes**
  - Example: "I guarantee there will come a time when..."
- **Language suggesting a cure**
  - Use "symptom management" or "improvement in quality of life" instead
- **Metaphysical or spiritual explanations** [if applicable]
  - Example: "Aspects of themselves they don't want to see"

### Safe to Use Externally

- **Expertise** – [Authority Figure] protocols, global leadership, advanced diagnostics
- **Approach** – holistic, root cause, whole-person care
- **Values** – integrity, transparency, compassion, accessibility, excellence
- **Promise framed carefully** – "Many [customers] tell us that, over time, they reach a point where daily [treatment] is no longer needed." (Always as a [customer] experience, not a guarantee)
- **Educational content** – treatment explanations, lifestyle guidance, debunking myths, evidence and research

### Tone Reminders for External Use

- Be hopeful, not absolute: share possibilities without promising results
- Be compassionate, not emotive: acknowledge [customer] struggles without exaggerating
- Be informative, not promotional: provide facts, guidance, and support, not hype

## DIGITAL MARKETING & CONTENT STRATEGY

### Core Digital Strategy

**[Approach - e.g., Education-First Approach]:**
- Position as the authoritative source for [condition] information
- Create content that attracts [customers] ready for real solutions
- Build trust through transparency and expertise

### SEO Targets:

[If specific keywords were mentioned:]
- "[Keyword 1 - e.g., Dry eye treatment Australia]"
- "[Keyword 2 - e.g., IPL Dry Eye [city names]]"
- "[Keyword 3 - e.g., Holistic Dry Eye treatment]"
- "[Keyword 4 - e.g., Toyos protocols Australia]"
- "[Keyword 5 - e.g., Dry eye specialist [locations]]"
- "[Keyword 6 - e.g., Meibomian gland dysfunction treatment]"

### Content Pillars:

1. **[Pillar 1 - e.g., Educational Authority]**
   - Detailed treatment explanations
   - Root cause analysis
   - Lifestyle factors and management
   - Debunking common myths

2. **[Pillar 2 - e.g., Patient Stories]** *[We might need to make this up]*
   - Transformation journeys
   - Before/after experiences
   - Quality of life improvements
   - Community testimonials

3. **[Pillar 3 - e.g., Clinical Excellence]**
   - [Authority Figure] protocol explanations
   - Technology and innovation
   - Research and evidence
   - Team expertise

4. **[Pillar 4 - e.g., Holistic Wellness]**
   - Diet and lifestyle guidance
   - Environmental factors
   - Stress management
   - Whole-body health connection

### Website Principles

**Trust-Building Elements:**
- Prominent [Authority Figure] association
- Clear protocol explanations
- Honest about timelines and costs
- Extensive [customer] testimonials [if compliant]
- Team credentials and training

**User Experience:**
- Easy assessment booking
- Clear service explanations
- Educational resources
- Support community access

**Calls to Action:**
- "Book Your Assessment"
- "Free Discovery Call"
- "Learn About Our Protocols"
- "Join Our Community"
- "Download Our Guide"
- "Take the 1 minute [Condition] quiz"

### Content Hub Needs

**FAQ Section Must Address:**
- Cost and payment options
- Treatment timelines
- Safety concerns
- Protocol differences
- Aftercare requirements
- Travel and accessibility

**Blog Content Ideas:**

[If specific content was mentioned:]
- "[Blog idea 1]"
- "[Blog idea 2]"
- "[Blog idea 3]"

### Design & Branding

**Visual Identity:**
- [Design direction if mentioned - e.g., "Professional yet warm"]
- [Brand feeling - e.g., "Clean, modern medical aesthetic"]
- [Color/style notes - e.g., "Soothing colour palette"]

**Imagery Style:**
- Real [customers] (with permission) [if compliant]
- Professional clinic environments
- Advanced technology
- Caring interactions
- Before/after where appropriate [check compliance]

## FINAL CHECKLIST

### Always Remember - Our Core Values

1. **[Value 1]** - [Key reminder - e.g., "Truth over convenience, always"]
2. **[Value 2]** - [Key reminder - e.g., "Their well-being over our profit"]
3. **[Value 3]** - [Key reminder - e.g., "Treat the whole person, not just symptoms"]
4. **[Value 4]** - [Key reminder - e.g., "[Authority Figure] protocols, global leadership"]
5. **[Value 5]** - [Key reminder - e.g., "Love them back to wellness"]

### In Every Interaction, Ask:

- Are we being honest and transparent?
- Are we treating [root cause], not just symptoms?
- Are we showing genuine care and compassion?
- Are we maintaining our standards of excellence?
- Are we building community and support?

### Our Promise to Keep

**"[North Star / Anchor Promise]"**

This isn't marketing, it's our commitment. Every [customer] interaction, every treatment decision, every piece of content should move us closer to fulfilling this promise.

---

*This playbook is a living document that should evolve as we grow, learn, and refine our approach. Like our [business type], it should be continuously updated with new insights, [customer] feedback, and emerging best practices. The heart of who we are, [Founder]'s values, our commitment to [customers], and our mission to [mission] remain constant.*
```

### Step 5: Save Outputs

**Create campaign-playbook.md:**
- Save the complete playbook to `campaign-playbook.md` in the client folder root
- Use the full markdown structure above
- Fill every section with extracted information from transcripts
- Explicitly mark gaps with **[To be determined]** or **[Question for Founder]**

**Enrich client_profile.md:**
1. Read existing `client_profile.md` if it exists
2. Add a new section at the end: `## Campaign Playbook Summary`
3. Include condensed versions of:
   - **Mission Statement:** [One sentence]
   - **North Star:** [The anchor promise]
   - **Core Values:** [Bulleted list of 5 values]
   - **Brand Personality:** [3-5 key traits]
   - **Primary Audience:** [One paragraph]
   - **Key Differentiators:** [3-5 bullet points]
   - **Sales Philosophy:** [One paragraph]
   - **Regulatory Framework:** [Name of regulatory body and key restrictions]
4. DO NOT overwrite existing sections
5. Append the summary at the end

**Report completion:**
- "Campaign playbook created at `campaign-playbook.md`"
- "I've also added a playbook summary to `client_profile.md`"
- Highlight gaps: "I noticed [X] wasn't mentioned in the transcripts. You may want to follow up on..."
- List sections that have **[To be determined]** markers

## Best Practices

### Reading Transcripts Deeply

Read with intention. Look for:
- **Stories the founder tells about themselves** - These reveal motivations
- **Emotional language when discussing customers** - Shows what they truly care about
- **Repeated phrases or words** - These become brand language
- **What frustrates them about competitors** - Reveals differentiators
- **Moments of passion** - These are core values in action
- **Specific customer stories referenced** - Social proof themes
- **How they describe their approach** - Sales philosophy

### Extracting Authentic Voice

- Capture the founder's actual words and phrases
- Note their natural speaking style (formal vs casual, technical vs accessible)
- Identify linguistic patterns (do they use metaphors? scientific terms? emotional language?)
- Distinguish between how they speak personally and how they want the brand to speak

### Handling Missing Information

When sections can't be filled from transcripts:
- Mark with **[To be determined]**
- Add specific questions: **[Question for Founder: What are your core values?]**
- Include a "Questions for [Founder] / Gaps to Fill" section
- Never invent information - transparency about unknowns builds trust

### Applying Compliance Frameworks

Always err on the side of caution:
- Frame all therapeutic claims as "may help" not "will cure"
- Distinguish internal language (more direct) from external messaging (compliant)
- Include specific guardrails for the industry
- Provide compliant alternatives for powerful claims

### Preserving Authenticity

- Use direct quotes liberally - they bring the playbook to life
- Don't sanitize passion or strong opinions (internally)
- Capture contradictions or tensions - these reveal real priorities
- Let the founder's personality shine through

## Common Industry Patterns

### Healthcare (Physio, Chiro, Optometry, Dry Eye, etc.)
- Founder often has personal health journey that led them here
- Mission centres on treating root cause, not masking symptoms
- Values include patient-first, evidence-based, holistic, compassionate
- Sales approach emphasises listening, education, and building trust
- Compliance requires "may help" language, no outcome guarantees
- Differentiation through methodology, authority partnerships, or comprehensive approach

### Home/Lifestyle Products (Beds, Sleep, etc.)
- Founder story often about solving own problem or caring for loved ones
- Mission about quality of life, independence, dignity, family
- Values include integrity, transparency, genuine care, honesty
- Sales approach emphasises "right fit" over revenue, referral over pressure
- Differentiation through service model (personal delivery), product quality, warranty
- Compliance around therapeutic claims (TGA if marketed as medical device)

### SaaS / Tech
- Founder story often about frustration with broken existing solutions
- Mission about empowerment, efficiency, transformation, innovation
- Values include user-centric, simplicity, transparency, results
- Sales approach emphasises problem-solving and demonstrable value
- Less regulatory concern, more consumer law compliance
- Differentiation through features, UX, or unique methodology

## Quality Checks

Before marking complete, verify:

- [ ] All 13 major sections are present and filled (or marked as gaps)
- [ ] Direct quotes from transcripts are included throughout
- [ ] Founder's personal story is captured authentically
- [ ] Brand voice guidelines are specific and actionable
- [ ] Compliance framework is identified and applied correctly
- [ ] Customer concerns and solutions are detailed with examples
- [ ] Sales scripts, discovery questions, and objection handling are included
- [ ] External messaging guardrails are clear and specific
- [ ] Gaps and missing information are explicitly noted
- [ ] Both `campaign-playbook.md` and `client_profile.md` are created/updated
- [ ] Playbook reads like a living document, not a template

## Final Notes

This skill works best with rich, conversational transcripts where the founder shares:
- Personal stories and motivations
- Philosophy and values
- Customer psychology insights
- Specific examples and anecdotes
- Sales approaches and scripts
- Strong opinions about their industry

If transcripts are thin or transactional, the playbook will have more gaps - that's expected and acceptable. Mark the gaps clearly and the playbook becomes a roadmap for follow-up conversations.

This is a starting point, not the final version. Real playbooks evolve through client review, team feedback, and real-world testing.

---

**Remember:** Campaign playbooks are strategic anchors that transform how teams represent the business. They ensure every interaction reflects the founder's vision authentically and serves customers at the deepest level.
