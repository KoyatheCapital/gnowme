from typing import Dict, Any
from intelligence.rag import UserRAG
from core.stoic_knowledge import get_stoic_reframe
from state_engine.engine import StateEngine, Biometrics

class ConsciousnessTranslator:
    def __init__(self, user_id: str):
        self.rag = UserRAG(user_id)
        self.active_books: list[str] = []
        self.state_engine = StateEngine()

    def activate_book(self, book_id: str, source_path: str = None):
        self.rag.add_book(source_path or f"data/books/{book_id}")
        if book_id not in self.active_books:
            self.active_books.append(book_id)

    def translate(self, bio_state: Dict, context: Dict, user_input: str = "") -> str:
        bio = Biometrics(
            hrv=bio_state.get("hrv"),
            heart_rate=bio_state.get("heart_rate"),
            resting_hr=bio_state.get("resting_hr"),
            sleep_score=bio_state.get("sleep_score")
        )
        state_data = self.state_engine.build_state(bio, context)
        use_soft = state_data["use_soft_language"]
        human_state = state_data["state"]

        query = f"Human state: {human_state}. Current situation: {context.get('work_summary', 'daily life')}. Help the human stay calm, focused and driven."
        relevant = self.rag.query(query, top_k=3)

        lines = []
        if use_soft:
            lines.append("Something feels like it's building slightly right now...")
        else:
            lines.append(f"Alright… {human_state} right now.")

        if isinstance(relevant, list):
            for item in relevant[:2]:
                reasoning = item.get("reasoning", "This is a moment that benefits from steadiness.")
                if isinstance(reasoning, list):
                    reasoning = reasoning[0]
                action = item.get("actions", "Take one steady breath and continue.")
                if isinstance(action, list):
                    action = action[0]
                lines.append(reasoning)
                lines.append(action)
        elif isinstance(relevant, str):
            lines.append(relevant)

        lines.append(get_stoic_reframe("dichotomy_of_control", human_state))
        lines.append("The choice is yours from here. One steady step at a time.")

        return " ".join(lines)
