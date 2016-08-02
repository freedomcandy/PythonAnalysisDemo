from flask import Flask            #Flask主体#
from flask import request          #Flask的request包 用来获取参数和头部#
from flask import redirect         #重定向网页使用#
from flask import make_response    #返回内容#
from flask import render_template  #渲染模板
from flask.ext.bootstrap import Bootstrap  #Bootstrap
# from flask.ext.wtf import Form      #表单
from flask import jsonify          #json
import pymongo                      #导入mongDb
import random                       #随机数
import time                         #获取当前时间


app = Flask(__name__)
bootstrap = Bootstrap(app)
conn = pymongo.MongoClient(host="127.0.0.1", port=27017)
db = conn['RoyDB']
print(db.collection_names())
collect = db['TJ']


currentTime =  time.strftime('%Y-%m-%d', time.localtime(time.time()))

@app.route('/',methods=['GET','POST'])
def indexPage():
    return render_template('index.html')

@app.route('/user/<name>')
def hello(name):
    return '<h1>Hello, %s!</h1>' % name


@app.route('/test',methods=['GET','POST'])
def test():
    if request.method == 'POST':
        return jsonify(code=200,message='OK')
    else:
        return jsonify(code=404, message='Error')

#type:launch启动 pagestart页面启动 pageend页面结束 finish程序结束
#记录用户信息并返回当前位移ID
@app.route('/jdb',methods=['GET','POST'])
def dbConnect():
    if request.method == 'POST':
        actionType = request.form['type']
        if actionType == 'launch': #开机
            idfa = request.form['idfa']  # idfa
            if idfa == "":
                return jsonify(code=500, message='Error')
            else:
                information = request.form.to_dict()
                information['authId'] = idfa + str(random.randint(1, 999999999))
                information['updateTime'] = time.time()
                print(information)
                information_id = collect.insert(information)
                return jsonify(code=200, data={'authId': information['authId']}, message='OK')
        elif actionType == 'pageStart':
            information = request.form.to_dict()
            information['updateTime'] = time.time()
            information_id = collect.insert(information)
            return jsonify(code=200, message='OK')
        elif actionType == 'pageEnd':
            information = request.form.to_dict()
            information['updateTime'] = time.time()
            information_id = collect.insert(information)
            return jsonify(code=200, message='OK')
        elif actionType == 'finish':
            #finish
            information = request.form.to_dict()
            information['updateTime'] = time.time()
            information_id = collect.insert(information)
            return jsonify(code=200, message='OK')
        else:
            return jsonify(code=500, message='Error')
    else:
        return jsonify(code=500, message='Error')


#服务器当天时间的 启动次数
@app.route('/launchCount')
def queryLifeLaunchCount():
    objs = []
    launchDoc = collect.find({'type':'launch'})
    for item in launchDoc:
        getTime = time.strftime('%Y-%m-%d', time.localtime(item['updateTime']))
        print(getTime)
        if getTime == currentTime:
            objs.append(item)
    print(len(objs))
    return render_template('launch.html',obj=objs,cTime = currentTime, count=len(objs))

#新用户 没有完成
@app.route('/newUser')
def queryNewUser():
    targetIdfaArray = []
    oldArray = []
    objs = []
    launchDoc = collect.find({})
    for item in launchDoc:
        getTime = time.strftime('%Y-%m-%d', time.localtime(item['updateTime']))
        print(getTime)
        if getTime == currentTime:
            targetIdfaArray.append(item['idfa'])
            print(getTime)
        else:
            oldArray.append(item)

    if len(oldArray) > 0:
      for item in oldArray:
        oldIdfa = item['idfa']
        for ifa in targetIdfaArray:
            if oldIdfa is not ifa:
                objs.append(item)
      return render_template('newUser.html', obj=objs, cTime=currentTime, count=len(objs))
    else:
      return render_template('newUser.html', obj=launchDoc, cTime=currentTime, count=len(launchDoc))



#攻略打开统计
@app.route('/readPost',methods=['GET','POST'])
def setPostRead():
    collect_read = db['post_read']
    if request.method == 'POST':
        information = request.form.to_dict()
        information['updateTime'] = time.time()
        print(information)
        information_id = collect_read.insert(information)
        return jsonify(code=200, data={'status': 1}, message='OK')
    return ''


#攻略跳淘宝
@app.route('/postJumpTB',methods=['POST'])
def setPostItemJupmTB():
    collect_item = db['post_to_item']
    if request.method == 'POST':
        information = request.form.to_dict()
        information['updateTime'] = time.time()
        print(information)
        information_id = collect_item.insert(information)
        return jsonify(code=200, data={'status': 1}, message='OK')
    return ''


#商品详情跳淘宝
@app.route('/jumpTB',methods=['POST'])
def setItemJupmTB():
    collect_item = db['item_to_tb']
    if request.method == 'POST':
        information = request.form.to_dict()
        information['updateTime'] = time.time()
        print(information)
        information_id = collect_item.insert(information)
        return jsonify(code=200, data={'status': 1}, message='OK')
    return ''


#统计攻略排行  times eg:2016-08-01
@app.route('/postsSort/<times>')
def quertPostsSort(times):
    collect_read = db['post_read']
    posts = collect_read.find({})
    tempObjs = []
    postObjs = []


    if times == 'all':
        print(posts)
        for item in posts:
            tempObjs.append(item)

    else:
        for item in posts:
            getTime = time.strftime('%Y-%m-%d', time.localtime(item['updateTime']))
            if getTime == times:
                tempObjs.append(item)

    #处理数据
    idsObj = []
    for item in tempObjs:
        tempId = item["postId"]
        if tempId not in idsObj:
            idsObj.append(tempId)

    for postId in idsObj:
        postSort = collect_read.find({'postId':postId})
        postName = ''
        if postSort.count() > 0:
           temp = postSort[0]
           postName = temp['Name']
        result = {"count":postSort.count(),"postId":postId, "Name":postName}
        postObjs.append(result)
    #排序
    print(postObjs)
    l = sorted(postObjs, key = lambda e:e.__getitem__('count'),reverse=True)
    # return jsonify(code=200, data={'post': l}, message='OK')
    return render_template('postSort.html',obj=l)



#统计攻略跳商品去TB  times eg:2016-08-01
@app.route('/itemsSort/<times>')
def quertPostsToTBSort(times):
    collect_item = db['post_to_item']
    items = collect_item.find({})
    tempObjs = []
    itemObjs = []
    if times == 'all':
        tempObjs = items
    else:
        for item in items:
            getTime = time.strftime('%Y-%m-%d', time.localtime(item['updateTime']))
            if getTime == times:
                tempObjs.append(item)
    # 处理数据
    idsObj = []
    for item in tempObjs:
        tempId = item["itemId"]
        if tempId not in idsObj:
            idsObj.append(tempId)
    for itemId in idsObj:
        itemSort = collect_item.find({'itemId': itemId})
        itemName = ''
        if itemSort.count() > 0:
            temp = itemSort[0]
            itemName = temp['Name']
        result = {"count": itemSort.count(), "postId": itemId, "Name": itemName}
        itemObjs.append(result)
    # 排序
    l = sorted(itemObjs, key=lambda e: e.__getitem__('count'), reverse=True)
    # return jsonify(code=200, data={'item': l}, message='OK')
    return render_template('itemsSort.html', obj=l)




#统计商品跳TB
@app.route('/itemSort/<times>')
def quertItemSort(times):
    collect_item = db['item_to_tb']
    items = collect_item.find({})
    tempObjs = []
    itemObjs = []
    if times == 'all':
        tempObjs = items
    else:
        for item in items:
            getTime = time.strftime('%Y-%m-%d', time.localtime(item['updateTime']))
            if getTime == times:
                tempObjs.append(item)
    # 处理数据
    idsObj = []
    for item in tempObjs:
        tempId = item["itemId"]
        if tempId not in idsObj:
            idsObj.append(tempId)
    for itemId in idsObj:
        itemSort = collect_item.find({'itemId': itemId})
        itemName = ''
        if itemSort.count() > 0:
            temp = itemSort[0]
            itemName = temp['Name']
        result = {"count": itemSort.count(), "postId": itemId, "Name": itemName}
        itemObjs.append(result)
    # 排序
    l = sorted(itemObjs, key=lambda e: e.__getitem__('count'), reverse=True)
    # return jsonify(code=200, data={'item': l}, message='OK')
    return render_template('itemSort.html', obj=l)


@app.errorhandler(404)
def page_not_found(e):
    return '404 找不到呀'

@app.errorhandler(500)
def not_found_page(e):
    return '500咯'



if __name__ == '__main__':
   app.run(debug=True,port=5000)