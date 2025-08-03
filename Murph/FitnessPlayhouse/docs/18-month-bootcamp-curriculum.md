# 18-Month Data Science & Engineering Bootcamp Curriculum

## Overview
This curriculum is designed to take you from current state to senior/lead data scientist level while building two production applications. It prioritizes TrainingPeaks-relevant skills early and uses spaced repetition for optimal retention.

## Learning Philosophy
- **Just-in-Time Learning**: Learn concepts 2-4 weeks before you need them
- **Spaced Repetition**: Revisit concepts at 1 day, 1 week, 1 month, 3 months
- **Project-Based**: Every concept is immediately applied
- **T-Shaped Skills**: Deep expertise in sports analytics, broad knowledge across data science

---

# Phase 1: Foundation & TrainingPeaks Skills (Months 1-3)
*Focus: Core skills immediately applicable at TrainingPeaks*

## Month 1: Data Engineering Fundamentals

### Week 1-2: Python for Data Engineering
**Topics:**
- Advanced Python: decorators, generators, context managers
- Async programming with asyncio
- Type hints and dataclasses
- Testing with pytest, mocking, fixtures

**Project:** Build a robust data pipeline for processing training files

**TrainingPeaks Relevance:** ⭐⭐⭐⭐⭐
- Process FIT files, TCX, GPX formats
- Handle large-scale athlete data

### Week 3-4: Time Series Analysis
**Topics:**
- Pandas time series functionality
- Rolling windows and resampling
- Seasonal decomposition
- Autocorrelation and stationarity

**Project:** Analyze your own training data patterns

**Resources:**
```python
# Example: Training Load Analysis
import pandas as pd
import numpy as np

def calculate_training_stress(power_data, ftp):
    """Calculate Training Stress Score (TSS)"""
    normalized_power = calculate_normalized_power(power_data)
    intensity_factor = normalized_power / ftp
    duration_hours = len(power_data) / 3600
    tss = (duration_hours * normalized_power * intensity_factor) / (ftp * 36)
    return tss
```

## Month 2: Sports Science Analytics

### Week 5-6: Physiological Modeling
**Topics:**
- Performance modeling (Banister, FITNESS-FATIGUE)
- Power duration curves
- Critical power concepts
- Lactate threshold estimation

**Project:** Implement TSB (Training Stress Balance) calculator

**TrainingPeaks Relevance:** ⭐⭐⭐⭐⭐
- Core functionality of TrainingPeaks
- Performance Management Chart (PMC)

### Week 7-8: Machine Learning for Athletes
**Topics:**
- Feature engineering for sports data
- Injury prediction models
- Performance prediction
- Anomaly detection for overtraining

**Project:** Build readiness predictor using HRV + training load

**Code Example:**
```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

class ReadinessPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)
        self.scaler = StandardScaler()
        
    def create_features(self, athlete_data):
        """Engineer features for readiness prediction"""
        features = {
            'acute_load': athlete_data['load'].rolling(7).mean(),
            'chronic_load': athlete_data['load'].rolling(28).mean(),
            'load_ratio': lambda x: x['acute_load'] / x['chronic_load'],
            'hrv_trend': athlete_data['hrv'].rolling(7).mean(),
            'sleep_debt': athlete_data['sleep_hours'].rolling(7).sum() - 56
        }
        return pd.DataFrame(features)
```

## Month 3: Advanced Analytics & APIs

### Week 9-10: API Development & Integration
**Topics:**
- RESTful API design
- FastAPI advanced features
- OAuth2 implementation
- Webhook handling
- Rate limiting and caching

**Project:** Build Strava/Garmin integration service

### Week 11-12: Statistical Methods
**Topics:**
- Bayesian methods for small samples
- Hierarchical models for team data
- A/B testing for training interventions
- Causal inference in sports

**Project:** Analyze training intervention effectiveness

---

# Phase 2: Application Development (Months 4-6)
*Focus: Building MVP of Women's Soccer Readiness App*

## Month 4: Database & Architecture

### Week 13-14: Database Design
**Topics:**
- PostgreSQL optimization
- Time-series databases (TimescaleDB)
- Database partitioning strategies
- Query optimization

**Project:** Design soccer readiness database schema

### Week 15-16: Cloud Architecture
**Topics:**
- AWS services (RDS, S3, Lambda, SQS)
- Docker and Kubernetes basics
- CI/CD pipelines
- Monitoring and logging

**Project:** Deploy first microservice

## Month 5: Frontend & Visualization

### Week 17-18: Modern Frontend
**Topics:**
- React with TypeScript
- State management (Redux/Zustand)
- Real-time updates with WebSockets
- Mobile-responsive design

**Project:** Build athlete dashboard

### Week 19-20: Data Visualization
**Topics:**
- D3.js for custom charts
- Plotly for interactive dashboards
- Best practices for sports data viz
- Performance optimization

**Project:** Create training load visualization

## Month 6: Integration & Testing

### Week 21-22: System Integration
**Topics:**
- Microservices communication
- Event-driven architecture
- Message queues (Redis, RabbitMQ)
- Service mesh concepts

### Week 23-24: Testing & Quality
**Topics:**
- Integration testing
- Load testing with Locust
- Security testing
- Performance profiling

---

# Phase 3: Advanced Features (Months 7-9)
*Focus: Wellness tracking, team features, advanced analytics*

## Month 7: Machine Learning Pipeline

### Week 25-26: MLOps Fundamentals
**Topics:**
- Model versioning with MLflow
- Feature stores
- Model monitoring
- A/B testing models

**Project:** Deploy readiness prediction model

### Week 27-28: Deep Learning for Sports
**Topics:**
- LSTM for sequence prediction
- Attention mechanisms
- Time series forecasting
- Injury risk modeling

**Code Example:**
```python
import torch
import torch.nn as nn

class InjuryRiskLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super(InjuryRiskLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        output = self.fc(lstm_out[:, -1, :])
        return self.sigmoid(output)
```

## Month 8: Team Analytics

### Week 29-30: Multi-athlete Analysis
**Topics:**
- Network analysis for team dynamics
- Clustering for player roles
- Optimization for lineup selection
- Workload distribution algorithms

### Week 31-32: Real-time Processing
**Topics:**
- Apache Kafka basics
- Stream processing with Flink/Spark
- Real-time analytics dashboards
- Edge computing concepts

## Month 9: Computer Vision Integration

### Week 33-34: Video Analysis
**Topics:**
- OpenCV for sports
- Player tracking
- Pose estimation
- Movement pattern analysis

**Project:** Integrate Veo footage analysis

### Week 35-36: Advanced Metrics
**Topics:**
- GPS data processing
- Accelerometer analysis
- Heart rate variability deep dive
- Multimodal data fusion

---

# Phase 4: Decision-Free Daily App (Months 10-12)
*Focus: NLP, personalization, behavioral science*

## Month 10: NLP & Content Generation

### Week 37-38: Natural Language Processing
**Topics:**
- Transformers and BERT
- Fine-tuning language models
- Prompt engineering
- Text summarization

**Project:** Build workout description generator

### Week 39-40: Recommendation Systems
**Topics:**
- Collaborative filtering
- Content-based filtering
- Hybrid approaches
- Reinforcement learning for recommendations

## Month 11: Personalization Engine

### Week 41-42: User Modeling
**Topics:**
- Behavioral analytics
- Preference learning
- Contextual bandits
- Adaptive algorithms

### Week 43-44: Optimization Algorithms
**Topics:**
- Genetic algorithms for workout planning
- Constraint satisfaction
- Multi-objective optimization
- Scheduling algorithms

## Month 12: Advanced Integration

### Week 45-46: Voice & Wearables
**Topics:**
- Voice interface design
- Wearable API integration
- Real-time data sync
- Offline-first architecture

### Week 47-48: Privacy & Security
**Topics:**
- HIPAA compliance
- Data encryption
- Differential privacy
- Secure multi-party computation

---

# Phase 5: Scale & Leadership (Months 13-15)
*Focus: Senior/Lead level skills*

## Month 13: System Design & Scale

### Week 49-50: Distributed Systems
**Topics:**
- CAP theorem
- Consensus algorithms
- Distributed databases
- Microservices patterns

### Week 51-52: High-Performance Computing
**Topics:**
- GPU programming basics
- Parallel processing
- Performance optimization
- Caching strategies

## Month 14: Data Science Leadership

### Week 53-54: Team Leadership
**Topics:**
- Technical mentoring
- Code review best practices
- Documentation standards
- Agile for data science

### Week 55-56: Business Strategy
**Topics:**
- Product metrics definition
- ROI calculation
- Stakeholder communication
- Technical decision making

## Month 15: Research & Innovation

### Week 57-58: Research Methods
**Topics:**
- Literature review process
- Experimental design
- Statistical power analysis
- Publishing findings

### Week 59-60: Cutting Edge Tech
**Topics:**
- Federated learning
- Edge AI
- Quantum computing basics
- Future of sports analytics

---

# Phase 6: Polish & Launch (Months 16-18)
*Focus: Production readiness, business development*

## Month 16: Production Hardening

### Week 61-62: Reliability Engineering
**Topics:**
- SRE principles
- Chaos engineering
- Disaster recovery
- SLA definition

### Week 63-64: Performance Optimization
**Topics:**
- Database tuning
- Query optimization
- Caching strategies
- CDN usage

## Month 17: Business Development

### Week 65-66: Go-to-Market
**Topics:**
- Market analysis
- Pricing strategies
- Customer acquisition
- Partnership development

### Week 67-68: Legal & Compliance
**Topics:**
- Data privacy laws
- Terms of service
- Intellectual property
- Insurance needs

## Month 18: Launch & Iterate

### Week 69-70: Launch Preparation
**Topics:**
- Beta testing
- User feedback loops
- Performance monitoring
- Support systems

### Week 71-72: Continuous Improvement
**Topics:**
- Analytics implementation
- A/B testing framework
- Feature flagging
- User research

---

# Learning Resources by Category

## Books (Read in Order)
1. **Month 1**: "Designing Data-Intensive Applications" - Kleppmann
2. **Month 2**: "The Science of Running" - Magness
3. **Month 3**: "Clean Architecture" - Martin
4. **Month 4**: "Machine Learning Engineering" - Burkov
5. **Month 6**: "The Sports Gene" - Epstein
6. **Month 8**: "Thinking in Systems" - Meadows
7. **Month 10**: "Algorithms to Live By" - Christian & Griffiths
8. **Month 12**: "Peak Performance" - Stulberg & Magness
9. **Month 14**: "The Manager's Path" - Fournier
10. **Month 16**: "Site Reliability Engineering" - Google

## Online Courses
1. **TrainingPeaks University**: All courses (Month 1)
2. **Fast.ai**: Practical Deep Learning (Month 7)
3. **Coursera**: Sports Performance Analytics (Month 2)
4. **AWS Training**: Solutions Architect (Month 4)
5. **Udacity**: Data Engineering Nanodegree (Month 3)

## Certifications (Optional but Valuable)
1. **AWS Certified Solutions Architect** (Month 6)
2. **Google Cloud Professional Data Engineer** (Month 9)
3. **Certified Kubernetes Administrator** (Month 12)

## Daily Practices
1. **Code Review**: 30 minutes daily
2. **Technical Writing**: 1 blog post weekly
3. **Open Source**: Contribute 2 hours weekly
4. **Networking**: 1 sports tech meetup monthly

---

# Spaced Repetition Schedule

## Core Concepts to Revisit
1. **ACWR Calculations**: Day 1, 7, 30, 90
2. **API Security**: Day 1, 7, 30, 90
3. **Time Series Analysis**: Day 1, 7, 30, 90
4. **Database Optimization**: Day 1, 7, 30, 90
5. **Machine Learning Pipeline**: Day 1, 7, 30, 90

## Practice Projects
- **Week 4**: Rebuild Week 1 project with new knowledge
- **Week 8**: Refactor Week 4 code
- **Week 12**: Integrate Weeks 1-8 into unified system
- **Continue pattern throughout program**

---

# Success Metrics

## Technical Proficiency
- [ ] Can design and implement distributed systems
- [ ] Can optimize queries processing millions of records
- [ ] Can build and deploy ML models to production
- [ ] Can lead technical architecture discussions

## Domain Expertise  
- [ ] Published 3+ articles on sports analytics
- [ ] Presented at 1+ conferences
- [ ] Contributed to open source sports projects
- [ ] Recognized expert in training load management

## Business Impact
- [ ] Launched 2 production applications
- [ ] Generated revenue from products
- [ ] Built partnerships with teams/organizations
- [ ] Mentored junior developers

## Career Progression
- [ ] Performing at senior/lead level at TrainingPeaks
- [ ] Receiving inbound recruiter interest
- [ ] Consulting opportunities in sports tech
- [ ] Building personal brand in field