import urllib.request
import pandas as pd

last = 6200
site = 'https://api.ballmanproject.io/bmtoken/'
data = []

for i in range(last):
    with urllib.request.urlopen(site + str(i)) as f:
        raw = (f.read().decode('utf-8'))
    
    meta_dict = dict(eval(raw))
    atts_list = meta_dict.pop('attributes')
    meta_dict['token ID'] = i
    for a in atts_list:
        meta_dict[a['trait_type']] = a['value']
    data.append(meta_dict)

metadata = pd.DataFrame(data)
metadata.to_csv('BALLMAN stats.csv', index=False)
# replace missing trait values with 'none' for rarity scoring
metadata.fillna(value='none', inplace=True)
all_traits = [c for c in metadata.columns if c.isupper()]
rarity_scores = {}
for t in all_traits:
    rarity_scores[t] = dict(1 / (metadata[t].value_counts(dropna=False)/6200))

def calc_rarity(token, traits):
    rarity = 0
    for t in traits:
        rarity += rarity_scores[t][token[t]]
    return rarity

metadata['total_rarity'] = metadata.apply(lambda x: 
                                          calc_rarity(x, all_traits), 
                                          axis = 1)
metadata.sort_values('total_rarity', ascending=False, inplace=True)
metadata['rarity_rank'] = metadata['total_rarity'].rank(ascending=False)
cols = metadata.columns.tolist()
cols = cols[-2:] + cols[:-2]
metadata = metadata[cols]
metadata.to_csv('BALLMAN rarity.csv', index=False)
