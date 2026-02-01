"""
Issues Agent State Manager
Singleton state manager for issues agent tools.
"""


class IssuesAgentState:
    """
    Singleton state manager for issues agent tools.
    Persists state across tool calls within a conversation.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._reset()
        return cls._instance

    def _reset(self):
        self.queries = []
        self.query_results = []
        self.issues = []
        self.proposed_fixes = []
        self.selected_issue_index = -1
        self.focus_areas = []

    def reset(self):
        self._reset()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
