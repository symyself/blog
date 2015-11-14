#coding=utf-8
import random
import StringIO
from math import ceil
from flask import send_file, session
from PIL import Image, ImageDraw, ImageFont
import os,sys
import platform
reload(sys)
sys.setdefaultencoding('utf-8')


class verify_img(object):
    def __init__(self, request, width=150, height=30):
        self.request = request
        self.width = width
        self.height = height
        self.background = (random.randrange(230, 255), random.randrange(230, 255), random.randrange(230, 255))
        #self.font_file = './simfang.ttf'
        #self.font_file = '/home/songy/helloworld/python/first_flask/identify_code/simfang.ttf'
        if 'Linux' == platform.system():
            self.font_file = '%s/simfang.ttf' %(os.path.abspath( os.path.dirname( __file__ )))
        else:
            self.font_file = 'simfang.ttf'
        self.verify_code = self._get_verify_code()
        self.img = Image.new('RGB', (self.width, self.height), self.background)
        self.draw = ImageDraw.Draw(self.img)
        self.font_size = self._get_font_size()
        self.draw_verify_code()
        self.draw_noisy()
        


    def _set_answer(self, answer):
        if type(answer) is int:
            answer = str(answer)
        session['answer'] = answer
    def _get_verify_code(self):
        def words():
            import words_list as words
            code = random.choice(words.all)
            self._set_answer(code)
            return code
        def number():
            m, n = 1, 50
            x = random.randrange(m, n)
            y = random.randrange(m, n)
            if 0 == random.randrange(0, 2):
                code = '%s+%s=?'%(x, y)
                answer = x+y
            else:
                code = '%s-%s=?'%(x, y)
                answer = x-y

            self._set_answer(answer)
            return code
        def question():
            import question_list as question
            code = random.choice(question.all_question.keys())
            answer = question.all_question[code]
            self._set_answer(answer)
            return code

        #
        code_type = random.randrange(0, 3)
        
        #code_type = random.randrange(0, 2)
        if 0 == code_type:
            print 'words:'
            return words()
        elif 1 == code_type:
            print 'number:'
            return number()
        else:
            print 'question:'
            return question()
    def _get_font_size(self):
        """  将图片高度的80%作为字体大小  这个公式没搞懂?????????????
        """
        s1 = int(self.height * 0.8)
        s2 = int(self.width/len(self.verify_code))
        return int(min((s1, s2)) + max((s1, s2))*0.05)

    def rand_color(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    def draw_noisy(self):
        #lines
        for i in range(3):
            start_x = random.randrange(self.width)
            start_y = random.randrange(self.height)
            stop_x = random.randrange(self.width)
            stop_y = random.randrange(self.height)
            self.draw.line((start_x, start_y, stop_x, stop_y), self.rand_color(), 1)
        #points
        for i in range(self.height):
            start_x = random.randrange(self.width)
            start_y = random.randrange(self.height)
            self.draw.point([start_x, start_y], self.rand_color())

    def draw_verify_code(self):
        #字体,大小
        print 'font file:%s' %(self.font_file)
        #print 'verify_code:%s' %(self.verify_code.decode('utf-8').encode('gb2312'))
        print 'verify_code:%s' %(self.verify_code)
        font = ImageFont.truetype(self.font_file, self.font_size)
        #第一个字的x, y坐标
        draw_x = random.randrange(0, 2*self.font_size+1)
        draw_y = random.randrange(1, self.height-self.font_size)

        #y坐标的上下浮动量
        float_y = int(ceil(self.font_size * 0.3))

        for i in self.verify_code:
            self.draw.text((draw_x, draw_y), i, self.rand_color(), font)
            #x坐标递增移动
            draw_x += self.font_size * 0.6
            #y坐标上下浮动
            salt_y = random.randrange(0-float_y, float_y)
            draw_y += salt_y
            #控制y坐标，防止越界到图片上下之外
            if draw_y < 0:
                draw_y = 0
            if draw_y > self.height - self.font_size:
                draw_y += (-1)*salt_y

    def display(self):
        buf = StringIO.StringIO()
        self.img.save(buf, 'gif')
        #buf.closed
        buf.seek(0)
        #return Response(buf.getvalue(),'image/gif')
        #return send_file(buf.getvalue(), mimetype='image/gif')
        return send_file(buf, mimetype='image/gif')
