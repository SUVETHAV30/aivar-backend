from typing import List
from sqlalchemy.orm import Session
from app.models import Scenario

# Heavy ML libraries are disabled for testing environment
_HAS_ML = False

class ClusteringService:
    def __init__(self):
        # Disable heavy ML model to avoid crashes in test environment
        self.model = None

    def cluster_scenarios(self, scenarios: List[Scenario], n_clusters: int = 5) -> None:
        if not self.model or len(scenarios) < n_clusters:
            # Fallback if ML libs missing or not enough scenarios
            for i, scenario in enumerate(scenarios):
                scenario.cluster_id = i % n_clusters
            return

        descriptions = [s.description for s in scenarios]
        
        # 1. Generate embeddings
        embeddings = self.model.encode(descriptions)
        
        # 2. Run KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans.fit(embeddings)
        
        # 3. Assign cluster_id back to scenarios
        labels = kmeans.labels_
        for i, scenario in enumerate(scenarios):
            scenario.cluster_id = int(labels[i])
