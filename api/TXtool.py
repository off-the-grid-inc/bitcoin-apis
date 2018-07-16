from operator import itemgetter
import requests

def getUnspent(address, testnet):
	network = 'BTCTEST' if testnet else 'BTC'
	response = requests.get('https://chain.so/api/v2/get_tx_unspent/'+network+'/'+address).json()
	utxos = response['data']['txs']
	clean_utxos = [{'value':int(float(i['value'])*100000000), 'index':i['output_no'], 'txid':i['txid']} for i in utxos]
	return clean_utxos

def pushTX(tx, testnet=False):
	data = {'tx_hex':tx}
	network = 'BTCTEST' if testnet else 'BTC'
	response = requests.post('https://chain.so/api/v2/send_tx/'+network, data=data)
	return response.json()

def convert_single_input(input_):
	prev_index_padded = "".join(["0" for i in range(8-len(hex(input_['index'])[2:]))])+hex(input_['index'])[2:]
	prev_index_endian = "".join(list(reversed([prev_index_padded[2*i:2*(i+1)] for i in range(len(prev_index_padded)/2)]))) 
	prev_tx_hash_r = "".join(list(reversed([input_['txid'][2*i:2*(i+1)] for i in range(len(input_['txid'])/2)])))
	collected_input_data = prev_tx_hash_r + prev_index_endian
	return collected_input_data

def convert_single_output(output_):
	output_value_padded = "".join(["0" for i in range(16-len(hex(output_['value'])[2:]))])+hex(output_['value'])[2:]
	output_value_endian = "".join(list(reversed([output_value_padded[2*i:2*(i+1)] for i in range(len(output_value_padded)/2)])))
	collected_output_data = output_value_endian+'1976a914'+b58decode(output_['address'])+'88ac'
	return collected_output_data

def choose_inputs(utxos, amount, policy='basic'):
	tx_inputs = []
	try:
		if policy == 'all':
			return utxos
		elif policy == 'basic':
			utxos = sorted(utxos, key=itemgetter('value'), reverse=True)
		elif policy == 'small_first':
			utxos = sorted(utxos, key=itemgetter('value'))
		i = 0
		input_tally = 0
		while input_tally < amount:
			tx_inputs.append(utxos[i])
			input_tally += utxos[i]['value']
			i += 1
		return tx_inputs
	except:
		return -1

def unsigned_tx(address, outputs, satoshi_fee, change_address=None, testnet=False, utxo_policy='basic'):
	gross_input_thresh = sum([i['value'] for i in outputs]) + satoshi_fee
	utxos = getUnspent(address, testnet)
	total = sum([i['value'] for i in utxos])
	if total<gross_input_thresh:
		return -1
	tx_inputs = choose_inputs(utxos, gross_input_thresh, policy=utxo_policy)
	tx_outputs = outputs
	gross_input = sum([i['value'] for i in tx_inputs])
	change_address = change_address if change_address!=None else address
	if gross_input > gross_input_thresh:
		tx_outputs.append({'value':gross_input - gross_input_thresh, 'address':change_address})
	n_inputs = int2hexbyte(len(tx_inputs))
	n_outputs = int2hexbyte(len(tx_outputs))
	if n_inputs==-1 or n_outputs == -1:
		print "Error: Max inputs/outputs is 256. Abort Tx."
		return -1
	bytes_ = '01000000'+n_inputs+"".join([convert_single_input(i)+'00ffffffff' for i in tx_inputs])+n_outputs+"".join([convert_single_output(i) for i in tx_outputs])+'00000000'
	return bytes_

def quick_unsigned_tx(from_, to_, satoshi_amount, satoshi_fee):
	outs = [{'value':satoshi_amount, 'address':to_}]
	if from_[0] in ['1', '3']:
		testnet=False
	elif from_[0] in ['2', 'm', 'n']:
		testnet=True
	else:
		raise ValueError("Not a bitcoin address: %s" %from_)
	return unsigned_tx(from_, outs, satoshi_fee, testnet=testnet)

def int2hexbyte(int_):
	raw_hex = hex(int_)[2:]
	if len(raw_hex) == 1:
		byte_ = '0'+raw_hex
	elif len(raw_hex) == 2:
		byte_ = raw_hex
	else:
		raise ValueError("not interpretable as hex byte: %s" %int_)
	return byte_

def btc2sat(decimal):
	return int(decimal*100000000)

b58dict = {0:'1', 1:'2', 2:'3', 3:'4', 4:'5',5:'6',6:'7',7:'8',8:'9',9:'A',10:'B',11:'C',12:'D',13:'E',14:'F',15:'G',16:'H',17:'J',18:'K',19:'L',20:'M',21:'N',22:'P',23:'Q',24:'R',25:'S',26:'T',27:'U',28:'V',29:'W',30:'X',31:'Y',32:'Z',33:'a',34:'b',35:'c',36:'d',37:'e',38:'f',39:'g',40:'h',41:'i',42:'j',43:'k',44:'m',45:'n',46:'o',47:'p',48:'q',49:'r',50:'s',51:'t',52:'u',53:'v',54:'w',55:'x',56:'y',57:'z'}
b58inv = {v: k for k, v in b58dict.iteritems()}

def b58encode(hex_string):
	number = int(hex_string, 16)
	nums = []
	while number>0:
		nums.append(b58dict[number%58])
		number = number//58
	return ''.join(reversed(nums))

def b58decode(b58_string, btc=True):
	power = len(b58_string)-1
	num = 0
	for char in b58_string:
		num += b58inv[char]*(58**power)
		power -= 1
	out = hex(num)[2:]
	if out[-1]=='L':
		out = out[:-1]
	out = out[:-8] if btc else out
	out = out if b58_string[0]=='1' else out[2:]
	return out
