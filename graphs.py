import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = {
    'Seed': ['42']*3 + ['123']*3 + ['456']*3 + ['789']*3 + ['2000']*3,
    'Iterations': [3, 5, 10]*5,
    'AStar': [200, 288, 642, 68, 290, 611, 98, 355, 355, 56, 109, 109, 47, 136, 1301],
    'Expectimax': [175, 417, 430, 61, 281, 400, 106, 193, 550, 149, 310, 783, 44, 191, 198],
    'MCTS': [386, 650, 2801, 283, 547, 2704, 216, 627, 2487, 261, 767, 3117, 214, 333, 333],
    'QLearn': [14, 14, 14, 115, 255, 736, 106, 186, 549, 98, 259, 259, 76, 143, 637]
}

df = pd.DataFrame(data)

# Line plot
plt.figure(figsize=(12, 6))
for seed in df['Seed'].unique():
    subset = df[df['Seed'] == seed]
    plt.plot(subset['Iterations'], subset['AStar'], marker='o', label=f'AStar (Seed {seed})')
    plt.plot(subset['Iterations'], subset['Expectimax'], marker='s', label=f'Expectimax (Seed {seed})')
    plt.plot(subset['Iterations'], subset['MCTS'], marker='^', label=f'MCTS (Seed {seed})')
    plt.plot(subset['Iterations'], subset['QLearn'], marker='D', label=f'QLearn (Seed {seed})')

plt.title('Algorithm Performance Based On Seeds and Iterations')
plt.xlabel('Iterations')
plt.ylabel('Final Score')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Bar plot
df_melted = df.melt(id_vars=['Seed', 'Iterations'], value_vars=['AStar', 'Expectimax', 'MCTS', 'QLearn'],
                    var_name='Algorithm', value_name='Score')

sns.set(style='whitegrid')
g = sns.catplot(
    data=df_melted,
    x='Iterations',
    y='Score',
    hue='Algorithm',
    col='Seed',
    kind='bar',
    height=4,
    aspect=1
)
g.fig.subplots_adjust(top=0.85)
g.fig.suptitle('Final Scores by Algorithm, Seed, and Iteration Number')
plt.show()
