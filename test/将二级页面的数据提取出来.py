import json
f = open('jd_task.txt','r')
data = f.readlines()
data =json.loads(data[0])
tmp_data= {'order':[],'key_search':[],'key_word':[],'page':[],'platform':[],'sort':[],'kind':[]}
tmp_result = {'platform':[],'sort':[],'kind':[],'page':[],'html':[]}
for item in data['result']:
    if item['platform'] not in tmp_result['platform']:
        tmp_result['platform'].append(item['platform'])
    if item['sort'] not in tmp_result['sort']:
        tmp_result['sort'].append(item['sort'])
    if item['kind'] not in tmp_result['kind']:
        tmp_result['kind'].append(item['kind'])
    if item['page'] not in tmp_result['page']:
        tmp_result['page'].append(item['page'])
    if item['html'] not in tmp_result['html']:
        tmp_result['html'].append(item['html'])

for item in data['data']:
    if item['platform'] not in tmp_data['platform']:
        tmp_data['platform'].append(item['platform'])
    if item['sort'] not in tmp_data['sort']:
        tmp_data['sort'].append(item['sort'])
    if item['kind'] not in tmp_data['kind']:
        tmp_data['kind'].append(item['kind'])
    if item['page'] not in tmp_data['page']:
        tmp_data['page'].append(item['page'])
    if item['key_word'] not in tmp_data['key_word']:
        tmp_data['key_word'].append(item['key_word'])
    if item['key_search'] not in tmp_data['key_search']:
        tmp_data['key_search'].append(item['key_search'])
    for sku in item['order']:
        if sku not in tmp_data['order']:
            tmp_data['order'].append(sku)

print (tmp_result)
print (tmp_data)

f = open('jd_task_kind.txt','w+')
f.write('\n')
f.write('result的全体元素结果统计')
f.write('\n')
f.write(json.dumps(tmp_result))

f.write('\n')
f.write('\n')
f.write('data的全体元素结果统计')
f.write('\n')
f.write(json.dumps(tmp_data))