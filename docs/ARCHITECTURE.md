# StormSight architecture

```mermaid
flowchart LR
    NOAA[NOAA historical tracks] --> FEATURES[Python geographic features]
    CENSUS[Census county internal points] --> FEATURES
    FEMA[FEMA NFIP claims v3] --> MATCH[County and date matching]
    FEATURES --> MATCH
    MATCH --> TABLE[Eligible storm and county targets]
    TABLE --> TRAIN[Training storms]
    TRAIN --> MODEL[Mean baseline and gradient boosting]
    MODEL --> CAL[Calibration storms select model and intervals]
    CAL --> TEST[Unseen storm evaluation]
    MODEL --> APP[Streamlit evidence dashboard]
    TEST --> APP
    NRI[FEMA NRI context only] --> APP
    CSV[Portfolio CSV] --> EXP[Python corridor value calculation]
    EXP --> APP
    APP --> TOOLS[Bounded Python evidence tools]
    TOOLS --> NEBIUS[Optional Nemotron on Nebius]
    NEBIUS --> CHECK[Schema and numerical prose checks]
    CHECK --> APP
    TAVILY[Optional official source lookup] --> TOOLS
```

The original NOAA file stays unchanged. FEMA claim downloads use only selected columns and event date windows. Raw claim caches stay local. The shared app uses county aggregates and a locally trained model artifact.

All model targets are NFIP payment proxies selected by the stated matching rule. They are not all hurricane losses. Current NRI risk scores do not enter the model. Portfolio insured values are not multiplied by arbitrary damage ratios.

The agent can only call named tools bound to the selected storm. It cannot run shell commands, select arbitrary URLs, or access files. API keys stay on the server. Numerical evidence is generated and rendered by Python. Qualitative AI text can still be wrong and requires review.
