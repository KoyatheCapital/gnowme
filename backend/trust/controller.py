class TrustProfile:
    def __init__(self):
        self.compliance_rate = 0.50
        self.interrupt_rate = 0.40
        self.engagement_score = 0.60
        self.daily_interventions = 0
        self.max_daily = 10

    def can_intervene(self) -> bool:
        return self.daily_interventions < self.max_daily

    def record_intervention(self):
        self.daily_interventions += 1

    def update_from_event(self, event_type: str):
        if event_type in ["followed", "engaged"]:
            self.compliance_rate = min(1.0, self.compliance_rate + 0.08)
            self.engagement_score = min(1.0, self.engagement_score + 0.06)
        elif event_type in ["interrupted", "ignored"]:
            self.interrupt_rate = min(1.0, self.interrupt_rate + 0.07)

    def adapt_config(self) -> dict:
        return {
            "frequency": "low" if self.interrupt_rate > 0.55 else "normal",
            "tone": "direct" if self.compliance_rate > 0.75 else "soft",
            "length": "short" if self.engagement_score < 0.5 else "medium"
        }
