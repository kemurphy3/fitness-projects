# 30-Day Action Plan (August 2025)

## Women's Soccer App (12 hrs/week)

### Week 1 (Aug 5-11): Database Foundation
- [ ] Create PostgreSQL schema with all tables (4 hrs)
- [ ] Build synthetic data generator for 20 players × 10 weeks (4 hrs)
- [ ] Document data model and assumptions (4 hrs)

**Key Files to Create:**
```
soccer_app/
├── database/
│   ├── schema.sql
│   ├── migrations/
│   └── seed_data.py
├── docs/
│   └── data_dictionary.md
└── requirements.txt
```

### Week 2 (Aug 12-18): Ingestion Pipeline
- [ ] Build Polar CSV parser with error handling (4 hrs)
- [ ] Create data validation layer (4 hrs)
- [ ] Test with sample Polar exports (4 hrs)

### Week 3 (Aug 19-25): Analytics Engine v1
- [ ] Implement basic readiness scoring algorithm (6 hrs)
- [ ] Create coach-friendly thresholds (3 hrs)
- [ ] Build unit tests for edge cases (3 hrs)

### Week 4 (Aug 26-Sept 1): MVP Dashboard
- [ ] Build coach dashboard in Streamlit (6 hrs)
- [ ] Add CSV upload interface (3 hrs)
- [ ] Create demo video for university coaches (3 hrs)

## Decision-Free Planner (8 hrs/week)

### Week 1 (Aug 5-11): Core Algorithm Design
- [ ] Design database schema for habits/tasks (3 hrs)
- [ ] Create basic task generation algorithm (3 hrs)
- [ ] Define adaptation rules (2 hrs)

### Week 2-3 (Aug 12-25): Prototype Development
- [ ] Build user preference capture flow (4 hrs)
- [ ] Implement streak tracking system (4 hrs)
- [ ] Create basic mobile-friendly web UI (4 hrs)
- [ ] Deploy prototype to friends/family (4 hrs)

### Week 4 (Aug 26-Sept 1): Feedback Integration
- [ ] Analyze user feedback from prototype (3 hrs)
- [ ] Refine adaptation algorithm (3 hrs)
- [ ] Plan v2 features based on usage data (2 hrs)

## Shared Infrastructure (Both Apps Benefit)

### Week 1: Foundation
- [ ] Set up shared PostgreSQL instance
- [ ] Create base user authentication system
- [ ] Initialize Git repositories with clear structure

## Daily Schedule Template

**Monday** (3 hrs): Soccer development
**Tuesday** (2 hrs): Soccer development  
**Wednesday** (2 hrs): Planner development
**Thursday** (3 hrs): Soccer development
**Saturday** (4 hrs): Flex time for urgent items
**Sunday** (4 hrs): Deep work on harder problems

## Success Criteria for Month 1

- Soccer app has working MVP with real data flow
- Planner has 10+ beta users providing feedback
- Both apps share authentication infrastructure
- Clear path to university pilot conversations