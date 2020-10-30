import pandas as pd

# df = pd.read_csv('./PoetryFoundationData.csv')
df = pd.read_csv('lyrics_data.csv')

df['artist'] = df['artist'].str.strip()


df_taylor_swift = df.loc[df['artist'] == 'Taylor Swift']

result_df = pd.DataFrame()

result_df['text'] = df_taylor_swift['lyrics']

result_df.to_csv('ts_lyrics_train.csv', index=False)
pass
