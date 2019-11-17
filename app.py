from flask import Flask, request, Response, render_template
import requests
import itertools
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Regexp, ValidationError, Optional
import re

def validate_one(form, field):
    a = form.avail_letters.data
    b = form.pattern.data
    if not (a or b):
        raise ValidationError('At least one field must be filled.')

def validate_length(form, field):
    a = form.pattern.data
    b = dict(form.selector.choices).get(form.selector.data)
    if b is "Any":
        b = -1
    else:
        b = int(b)
    if (a is not None) and (b is not -1) and (len(a) is not b):
        raise ValidationError('Pattern length must match requested Length')

class WordForm(FlaskForm):
    avail_letters = StringField("Letters", validators= [
        Optional(), Regexp(r'^[a-z]+$', message="must contain letters only")])
    pattern = StringField("Pattern", validators= [Regexp(r'^[a-zA-Z.]+$', message="must contain letters only"), validate_one])
    choices = [('-1', 'Any'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8'),('9', '9'),('10', '10')]
    selector = SelectField(u"Length", choices = choices, validators = [validate_length])
    submit = SubmitField("Go")


csrf = CSRFProtect()
app = Flask(__name__)
app.config["SECRET_KEY"] = "row the boat"
csrf.init_app(app)

@app.route('/')
def index():
    form = WordForm()
    numbers = []
    for i in range(3, 11):
        numbers.append(i)
    print(numbers)
    return render_template("index.html", form=form, numbers=numbers)

KEY = "720ee5f3-0d6b-42da-8be5-4bb5f4e27ec4"

@app.route('/def/<word>', methods=['GET'])
def define_word(word):
    url = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"+word+"?key="+KEY
    response = requests.get(url)
    try:
        json_response = response.json()
        defs = []
        type = ""
        text = ""
        final = ""
        for i in json_response:
            if i is not None:
                type = i['fl'] + ": "
                for j in i['shortdef']:
                    text = j + " "
                defs.append(type+text)
        for i in defs:
            final = final+ i + "\n\n"
        return final
    except:
        return "No definition provided by Merriam-Webster's Dictionary"

def sort_length(elem):
    return len(elem)

def match_set_regex(rgx, the_set):
    new_set = set()
    rgx_object = re.compile(rgx)
    for x in the_set:
        if rgx_object.fullmatch(x) is not None:
            new_set.add(x)
    return new_set

@app.route('/words', methods=['POST','GET'])
def letters_2_words():

    form = WordForm()
    if form.validate_on_submit():
        letters = form.avail_letters.data
        pattern = form.pattern.data
        dict_selector = dict(form.selector.choices)
        length = dict_selector.get(form.selector.data)
        if length is "Any":
            length = -1
        else:
            length = int(length)
        if length > len(letters):
            length = -1
    else:
        return render_template("index.html", form=form)

    with open('sowpods.txt') as f:

        good_words = set(x.strip().lower() for x in f.readlines())

    word_set = set()
    if length is -1:
        for l in range(3,len(letters)+1):
            for word in itertools.permutations(letters,l):
                w = "".join(word)
                if w in good_words:
                    word_set.add(w)
    else:
        for word in itertools.permutations(letters,length):
            w = "".join(word)
            if w in good_words:
                word_set.add(w)
    if pattern is not None:
        word_set = match_set_regex(pattern, word_set)

    return render_template('wordlist.html',
        wordlist=sorted(sorted(word_set), key=sort_length),
        name="Clark Ohnesorge")


@app.route('/proxy')
def proxy():
    result = requests.get(request.args['url'])
    resp = Response(result.text)
    resp.headers['Content-Type'] = 'application/json'
    return resp
