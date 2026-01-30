from typing import List, Dict, Any
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

class AssociationRuleRecommender:
    
    """ Association Rule-based Recommender System. It uses the Apriori algorithm
     for frequent itemset mining and generates association rules ranked by confidence and lift.
        
    Attributes:
        min_support (float): Minimum support threshold.
        min_confidence (float): Minimum confidence threshold.
        encoder (TransactionEncoder | None): One-hot encoder fitted to baskets.
        itemsets (pd.DataFrame | None): Frequent itemsets mined.
        rules_df (pd.DataFrame | None): DataFrame of association rules (sorted by lift & confidence).
        rules (List[Dict[str, Any]]): JSON-friendly list of rules.
    """

    def __init__(self, min_support: float = 0.02, min_confidence: float = 0.3):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.encoder = None
        self.itemsets = None
        self.rules_df = None
        self.rules = []

    # ----- Pipeline -----
    
    def fit(self, baskets: List[List[str]]):
        """
        Fit the recommender to the given baskets.
        """
        df = self._baskets_to_dataframe(baskets)
        self.itemsets = self._mine_frequent_itemsets(df)
        self.rules_df = self._generate_association_rules(self.itemsets)
        self.rules = self._rules_to_records(self.rules_df)

    def get_rules(self) -> List[Dict[str, Any]]:
        """
        Return mined rules in JSON-friendly format.
        """
        return self.rules

    # ----- Recommendation methods -----
    
    def recommend_for_item(self, item: str, top_n: int = 5) -> List[str]:
        """
        Recommend items based on a single antecedent item.
        Returns top_n consequents sorted by lift.
        """
        if self.rules_df is None or self.rules_df.empty:
            return []

        # Filter rules where item is in antecedent (vectorized)
        filtered = self.rules_df[self.rules_df['antecedents'].apply(lambda x: item in x)]
        
        # Flatten all consequents except the item
        recommendations = pd.Series([c for conseq in filtered['consequents'] for c in conseq if c != item])
        
        # Keep unique top_n while preserving order
        recommendations = recommendations.drop_duplicates().head(top_n)
        return recommendations.tolist()

    def recommend_for_basket(self, basket: List[str], top_n: int = 5) -> List[str]:
        """
        Recommend items based on a basket of items.
        Finds rules whose antecedent is a subset of the basket.
        Returns top_n consequents sorted by lift.
        """
        if self.rules_df is None or self.rules_df.empty:
            return []

        basket_set = set(basket)
        # Filter rules where antecedent is subset of basket
        filtered = self.rules_df[self.rules_df['antecedents'].apply(lambda x: set(x).issubset(basket_set))]

        # Flatten consequents excluding items already in basket
        recommendations = pd.Series([
            c for conseq in filtered['consequents'] for c in conseq
            if c not in basket_set
        ])
        # Keep unique top_n
        recommendations = recommendations.drop_duplicates().head(top_n)
        return recommendations.tolist()

    # ----- Internal helpers -----
    
    def _baskets_to_dataframe(self, baskets: List[List[str]]) -> pd.DataFrame:
        """
        Convert baskets to one-hot encoded DataFrame.
        Reuse encoder if already fitted to avoid recomputation.
        """
        if self.encoder is None:
            self.encoder = TransactionEncoder()
            encoded_array = self.encoder.fit(baskets).transform(baskets)
        else:
            # Transform using existing encoder
            encoded_array = self.encoder.transform(baskets)
        return pd.DataFrame(encoded_array, columns=self.encoder.columns_)

    def _mine_frequent_itemsets(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Mine frequent itemsets using Apriori.
        """
        return apriori(df, min_support=self.min_support, use_colnames=True)

    def _generate_association_rules(self, itemsets: pd.DataFrame) -> pd.DataFrame:
        """
        Generate association rules and sort once by lift & confidence.
        """
        rules = association_rules(itemsets, metric="confidence", min_threshold=self.min_confidence)
        if not rules.empty:
            rules = rules.sort_values(by=["lift", "confidence"], ascending=False).reset_index(drop=True)
        return rules

    def _rules_to_records(self, rules_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Convert rules DataFrame to a JSON-friendly list of dictionaries.
        """
        records = []
        for _, row in rules_df.iterrows():
            records.append({
                "antecedent": list(row["antecedents"]),
                "consequent": list(row["consequents"]),
                "support": float(row["support"]),
                "confidence": float(row["confidence"]),
                "lift": float(row["lift"]),
                "leverage": float(row["leverage"]),
                "conviction": float(row["conviction"]),
            })
        return records


baskets = [
    ["milk", "bread", "butter"],
    ["bread", "butter"],
    ["milk", "bread"],
    ["milk", "bread", "butter", "eggs"],
    ["bread", "eggs"],
    ["milk", "eggs"],
]

# Create recommender with low support/confidence to see some rules
recommender = AssociationRuleRecommender(min_support=0.3, min_confidence=0.5)
recommender.fit(baskets)

rules = recommender.get_rules()
for r in rules:
    print(r)

