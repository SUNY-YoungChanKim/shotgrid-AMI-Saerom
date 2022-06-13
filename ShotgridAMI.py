import json
import os
from flask import Flask,flash, render_template
from flask import request

import shotgun_api3


app=Flask(__name__)

sg= shotgun_api3.Shotgun(
        "https://saerom1.shotgrid.autodesk.com",
        script_name="SequenceDelteWithShots",
        api_key="oxmzeeapaqletcXwsmgpr0*oh",
        )

@app.route('/delSequence',methods=['POST'])
def delSequence():
    try:
        dataDictForm= dict(request.form.to_dict())
        selectedIds=dataDictForm['selected_ids'].split(',')                                                     #생성된 시퀸스들의 아이디를 리스트 형태로 가져옴
        
        req = {'sequence':[],'shots':[]}                                                                #html에 포스트 할 데이터
        for SeqID in selectedIds:
            filters =[                                                                              
                ['project', 'is', {'type': 'Project', 'id': int(dataDictForm['project_id'])}],
                ['id','is',int(SeqID)]
            ]
            fields= ['code','shots']

            sg_Seq=sg.find_one('Sequence',filters,fields)                                                #해당 프로젝트내에서 선택된 시퀸스의 code와 shots필드를 포함한 형태의 entity를 로드
            
            sg_Shots=sg_Seq['shots']                                                                     #시퀸스에 포함된 샷들로드
            for sg_Shot in sg_Shots:                      
                sg_Shot['Episode']=sg_Seq['code']                                                       #html에 종속된 sequence를 포함하기위해 필드 추가
                sg_shotExtend=sg.find_one('Shot',[['id', 'is', int(sg_Shot['id'])]],['image'])
                image=sg_shotExtend['image']                                                            #샷의 썸네일 로드
                if image == None:                                                                       #없을 시 None
                    sg_Shot['image']="None"
                else:                                                                                   #있을 시 URL맵핑
                    sg_Shot['image']=image
                sg_Shot.pop('type')                                                                     #html에서 표기 안하기 위해 type필드 제거
                req['shots'].append(sg_Shot)                                                            #샷 데이터 추가


            sg_Seq.pop('shots')
            req['sequence'].append(sg_Seq)
        
        
    
        return render_template("delSequence.html", data=req,size=len(req['shots']))
    except shotgun_api3.ShotgunError as e:
        print(e)
        return render_template("error.html", data=req)                                                  #에러 페이지
    
@app.route('/delImplement',methods=['POST'])
def delImplement():
    dataDictForm=dict(request.form.to_dict())
    idLen = int(dataDictForm['IdLen'])
    seqIdLen = int(dataDictForm['seqIDLen'])

    for i in range(0,idLen):
        nextKey = 'Ids['+str(i)+']'
        sg.delete('Shot',int(dataDictForm[nextKey]))

    for i in range(0,seqIdLen):
        nextKey = 'seqID['+str(i)+']'
        sg.delete('Sequence',int(dataDictForm[nextKey]))

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


if __name__=='__main__':
    app.run(debug=True)
