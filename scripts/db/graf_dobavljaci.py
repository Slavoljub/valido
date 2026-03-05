import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine

# konekcija na bazu
engine = create_engine("postgresql://postgres:postgres@localhost:5432/valido")

# SQL upit
query = """
SELECT
    d.naziv as dobavljac,
    SUM(k.ukupan_iznos) as promet
FROM kpr_transakcije k
JOIN racuni r ON k.racun_id = r.id
JOIN dobavljaci d ON r.dobavljac_id = d.id
GROUP BY d.naziv
"""

df = pd.read_sql(query, engine)

# napravi graf
G = nx.Graph()

for _, row in df.iterrows():
    dobavljac = row["dobavljac"]
    promet = row["promet"]

    G.add_node(dobavljac)
    G.add_edge("Firma", dobavljac, weight=promet)

# nacrtaj graf
plt.figure(figsize=(10,8))

pos = nx.spring_layout(G)

nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=3000,
    node_color="lightblue",
    font_size=10
)

labels = nx.get_edge_attributes(G,'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

plt.title("Mreza dobavljaca")
plt.show()
