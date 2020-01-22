import pandas as pd
import re
import numpy as np
from tqdm import tqdm

import glob

import Levenshtein
# from mid2names import import_fiw_names

from elasticsearch import Elasticsearch, helpers
from match_names import get_confidence
from matplotlib import pyplot as plt
from PIL import Image
from IPython.display import clear_output
import argparse

parser = argparse.ArgumentParser('Take input file paths')

parser.add_argument('path1')
parser.add_argument('path2')
args = parser.parse_args()


es = Elasticsearch()


def create_celeba_lut(path):
	ids, name = [], []
	with open(path) as f:
		next(f)
		next(f)
		for row in f.readlines():
			r = row.split()
			ids.append(r[0])
			name.append(re.sub(r'_', r' ', r[1]))
		df = pd.DataFrame(columns=['source_db', 'id','name'])
		df['id'] = ids
		df['name'] = name
		df['source_db'] = 'msceleb'
		df['first'] = df.name.apply(lambda x:x.split()[0])
		df['last'] = df.name.apply(lambda x:x.split()[-1])
	return df


def index_in_ES(df):
	# Index CelebA Face

	docs = []
	for i in tqdm(df.index):
		name, _id = df.loc[i, ["name", "id"]]
		docs.append({
					'_index':'celeba_test',
					'_type':'document',
					'_id':_id,
					'_source':{'name':name}
				})
		if len(docs)==1000:
			helpers.bulk(es, docs)
			docs = []
	if docs:
		helpers.bulk(es, docs)
		docs = []

def find_overlap(fiw_df):
	overlap_df = pd.DataFrame(columns=['db1', 'db2', 'fid.mid', 'db2.id', 'name1', 'name2', 'confidence'])

	for i in tqdm(fiw_df.index):
		first, last, gender, name, fid, mid = fiw_df.loc[i, ['first', 'last', 'gender', 'name', 'fid', 'mid']]
		if not isinstance(first, str): first = ''
		if not isinstance(last, str): last = ''
		body = {'query':{'bool':
						 {
							 'should':[{"match":{'name':first}}, {"match":{'name':last}}]
						 }
						}}
		resp = es.search(index='celeba', body=body)['hits']['hits']
		for r in resp:
			name2 = r['_source']['name']
			conf = get_confidence(name, name2)
			if conf > 0.9:
				overlap_df.loc[len(overlap_df)] = 'fiw', 'celeba_test', f'{fid}.{mid}', r['_id'], name, name2, conf
	return overlap_df

if __name__=="__main__":
	fiw_df = pd.read_csv(args.path1)	
	celebA_df = create_celeba_lut(args.path2)
	# index_in_ES(celebA_df)
	overlap_df = find_overlap(fiw_df)
	overlap_df.to_csv('celebA_x_fiw.csv', index=None)