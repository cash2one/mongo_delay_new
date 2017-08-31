url = {
                "platform":"", #string
                "header":{}, #字典 (必需)
                "method":"", #string  (必需)
                "useproxy":"", #string
                "proxy_info":{
                                    "is_use_proxy":False, #bool 是否使用代理
                                    "use_succ":False, # bool 代理是否使用成功
                                    "proxy_type": "" ,#string 使用蓝灯时填入landeng 使用其他代理时填入default
                                    "proxy_url": "", #string 使用的代理的完整的url
                                    "exec_time_ms":0, #int64 使用代理访问一共多长时间 毫秒
                                    "proxy_detail":"127.0.0.1:3000" #string  代理详情
                                },
                "no_text":False , #bool  false  需要html内容 true 不要要html内容 (必需)
                "url":"" ,#string (必需)
                'other':'',
                "data":{}, # 字典  表单数据  (有表单数据时必需)
                "text_data":"" ,#string post时需要添加的数据  (需要post数据时必需)
                "content_judge":{ #字典  检查内容
                                 "is_judge": False, # bool 是否执行检查内容
                                 "should_exist":[ #数组  应该存在的
                                                 { #字典
                                                 "context": "", #string 需要检查的内容
                                                 "judge_result":False #bool 该内容是否存在
                                                 },
                                                ],
                                 "no_should_exist":[ #数组  不应该存在的
                                                    { #字典
                                                    "context": "", #string 需要检查的内容
                                                    "judge_result":False, #bool 该内容是否存在
                                                    },

                                                   ]
                                 },


            }

tmp = {'platform':'app','header':{'a':1},'content_judge':{'is_judge':True,'should_exist':[1,2,3,4,5]},'proxy_info':{"proxy_detail":'111335555','proxy_type':'default','is_use_proxy':True}}
for i in tmp:
    if i in url.keys():
        try:
            url[i].keys()#查看该字段是否套字典
            if isinstance(tmp[i],dict):#如果传递进来的参数是字典，默认也是字典就更新
                url[i].update(tmp[i])
        except:
            url[i] = tmp[i]#没有套字典
    else:
        if i in url["proxy_info"].keys():
            url["proxy_info"][i] = tmp[i]
        elif i in url['content_judge'].keys():
            url['content_judge'][i] = tmp[i]

print (url)
