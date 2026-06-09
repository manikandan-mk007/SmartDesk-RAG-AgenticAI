import re


FOLLOW_UP_KEYWORDS = [
    "not working",
    "still same",
    "still not",
    "not fixed",
    "doesn't work",
    "did not work",
    "already tried",
    "i tried",
    "tried but",
    "same issue",
    "what next",
    "next step",
    "again",
    "still",
    "no change",
    "not solved",
    "not resolved",
]


class RAGMemoryService:
    def clean_text(self, value):
        if not value:
            return ""

        value = str(value).strip()
        value = re.sub(r"\s+", " ", value)
        return value

    def normalize_history(self, chat_history):
        if not isinstance(chat_history, list):
            return []

        normalized = []

        for item in chat_history[-10:]:
            role = self.clean_text(item.get("role", "")).lower()
            content = self.clean_text(item.get("content", ""))

            if role not in ["user", "assistant"]:
                continue

            if not content:
                continue

            normalized.append({
                "role": role,
                "content": content,
            })

        return normalized

    def is_follow_up_question(self, question):
        question_lower = self.clean_text(question).lower()

        if len(question_lower.split()) <= 5:
            return True

        return any(keyword in question_lower for keyword in FOLLOW_UP_KEYWORDS)

    def get_last_user_issue(self, chat_history):
        for item in reversed(chat_history):
            if item["role"] == "user":
                return item["content"]
        return ""

    def get_last_assistant_answer(self, chat_history):
        for item in reversed(chat_history):
            if item["role"] == "assistant":
                return item["content"]
        return ""

    def build_history_text(self, chat_history):
        lines = []

        for item in chat_history[-8:]:
            role = "User" if item["role"] == "user" else "SmartDesk AI"
            lines.append(f"{role}: {item['content']}")

        return "\n".join(lines)

    def build_contextual_question(self, question, chat_history):
        question = self.clean_text(question)
        normalized_history = self.normalize_history(chat_history)

        if not normalized_history:
            return question

        if not self.is_follow_up_question(question):
            return question

        last_user_issue = self.get_last_user_issue(normalized_history)
        last_assistant_answer = self.get_last_assistant_answer(normalized_history)
        history_text = self.build_history_text(normalized_history)

        return f"""
The user is continuing the same support conversation.

Previous conversation:
{history_text}

Original / previous issue:
{last_user_issue}

Previous SmartDesk suggestion already given:
{last_assistant_answer}

Current user follow-up:
{question}

The user says the previous fix did not solve the issue. Give the next-level troubleshooting steps. 
Avoid repeating the same basic steps unless needed. Mention what to check next and when to create a support ticket.
""".strip()

    def build_ticket_description_from_conversation(self, question, rag_answer, conversation):
        lines = []

        lines.append("Issue raised from SmartDesk RAG chat.")
        lines.append("")
        lines.append("Latest user question:")
        lines.append(question or "No question provided.")
        lines.append("")
        lines.append("Latest AI answer:")
        lines.append(rag_answer or "No AI answer available.")

        if conversation:
            lines.append("")
            lines.append("Full RAG conversation:")
            lines.append("----------------------")

            for item in conversation:
                role = item.get("role", "").upper()
                content = self.clean_text(item.get("content", ""))

                if role and content:
                    lines.append(f"{role}: {content}")

        return "\n".join(lines)