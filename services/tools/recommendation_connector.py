class RecommendationConnector:
    def __init__(self, db):
        self.db = db

    def recommend_for_item(self, item: str):
        query = """
        SELECT consequent, confidence, lift
        FROM association_rules
        WHERE antecedent @> ARRAY[%s]
        ORDER BY lift DESC, confidence DESC
        """
        return self.db.fetch_all(query, (item,))

    def recommend_for_basket(self, basket: list[str]):
        query = """
        SELECT consequent, confidence, lift
        FROM association_rules
        WHERE antecedent <@ %s
        ORDER BY lift DESC, confidence DESC
        """
        return self.db.fetch_all(query, (basket,))
