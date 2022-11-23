from django.shortcuts import render
from django.utils import timezone
import logging
from django.conf import settings
from django.core.files.storage import default_storage
import numpy as np
import cv2
import string
from keras.models import load_model
from django.db import connection

# from pybo.model import Result
from .models import Result, AI_Model

# Create your views here.

logger = logging.getLogger('mylogger')

def index(request):
    return render(request, 'language/index.html')

def upload(request):
        #db 조회하여 모델 선택
    cursor = connection.cursor()
    cursor.execute("select address from account_profile where id=1")
    print(cursor.fetchall())
    results = []
    if request.method == 'POST' and request.FILES['files']:
        
        for idx, path in enumerate(request.FILES.getlist('files')):
        #todo form에서 전송한 파일을 획득한다.
            file = path
            # Django 과정에서 배웠던 request.FILES 을 활용하세요.
                    

            logger.error('file', file)
            # class names 준비
            class_names = list(string.ascii_lowercase)
            class_names = np.array(class_names)

            #todo 모델 로딩
            model_path = getattr(settings, 'MODEL_DIR', None)
            # model위치를 setting에 정의해놨으니 활용해서 채워보세요. 위치는 본인이 원하는 다른곳에 해도 됩니다.
            model = load_model(model_path+'/sign_model.h5')


            #todo history 저장을 위해 객체에 담아서 DB에 저장한다.
            # 이때 파일시스템에 저장도 된다.
            result = Result()
            result.answer = request.POST.getlist('answer', '')[idx] # answer를 채워봅시다.
            result.image = file # image를 채워봅시다.
            result.pub_date = timezone.datetime.now()
            result.save()


            #todo 흑백으로 읽기
            # model에서 ImageField로 처리된 항목은 ImageFieldFile 객체로 활용됩니다.
            # 해당 객체에는 path를 얻어오는 method가 있습니다.
            img = cv2.imread(result.image.path, cv2.IMREAD_GRAYSCALE)
            
            #todo 크기 조정
            img = cv2.resize(img, (28, 28))
            
            #todo input shape 맞추기
            test_sign = img.reshape(1, 28, 28, 1)
            
            #todo 스케일링
            test_sign = test_sign / 255
            
            #todo 예측 : 결국 이 결과를 얻기 위해 모든 것을 했다.
            # 예측 결과를 수행해보세요.
            pred = model.predict(test_sign)
            #todo 예측 결과를 DB에 저장한다.
            result.result = class_names[pred.argmax(axis=1)]    #예측결과
            result.save()
            if result.answer==result.result:
                result.test = '정답'
                result.save()
            else:
                result.test = '오답'
                result.save()
            results.append(result)


        # http method의 GET은 처리하지 않는다. 사이트 테스트용으로 남겨둠.
        else:
            test = request.GET['test']
            logger.error(('Something went wrong!!',test))
        context = {
                    'result': results,
                }
        return render(request, 'language/result.html', context)    

def modelFiles(request):
    fileList = AI_Model.objects.all()
