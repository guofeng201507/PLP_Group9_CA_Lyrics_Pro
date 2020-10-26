import pandas as pd

df = pd.read_csv('./PoetryFoundationData.csv')

result_df = pd.DataFrame()

result_df['text'] = df['Poem']

result_df.to_csv('poems.csv', index=False)
pass
