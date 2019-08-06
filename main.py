from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, login_required
from __init__ import db
import pymysql as pms

from parser import parse

main = Blueprint('main', __name__)

def run_student_query(query):
    mock = pms.connect("localhost","sequelhelp_411","abducs411!!!!!","sequelhelp_mock")
    
    cursor = mock.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    mock.close()
    
    return data

def get_expected_table(question_id):
    col_names = []
    
    mock = pms.connect("localhost","sequelhelp_411","abducs411!!!!!","sequelhelp_mock")
    cursor = mock.cursor()
    
    query = 'SELECT AnswerQuery FROM Questions WHERE QuestionId=' + str(question_id) + ';'
    
    cursor.execute(query)
    answer_query = cursor.fetchall()[0][0]
    cursor.execute(answer_query)
    
    col_names.append([i[0] for i in cursor.description])
    table = cursor.fetchall()
    mock.close()
    
    return {'table': table, 'col_names': col_names[0]}
    
def parse_student_query(query):
    MAX_RESULT_LENGTH = 10
    
    mock = pms.connect("localhost","sequelhelp_411","abducs411!!!!!","sequelhelp_mock")
    cursor = mock.cursor()
    
    try:
        run_student_query(query)
        
    except pms.Error as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        error_message = template.format(type(ex).__name__, ex.args)
        return {"error": error_message}
    
    result_queries = parse(query)

    result_tables = []
    bad_query_indices = []
    col_names = []
    is_shortened = []
    for i in range(len(result_queries)):
        try:
            cursor.execute(result_queries[i])
            col_names.append([i[0] for i in cursor.description])
            
        except:
            bad_query_indices.append(i)
            result_tables.append('table_for_bad_query')
            continue
        
        table = cursor.fetchall()
        is_shortened.append(False)
        if len(table) > MAX_RESULT_LENGTH:
            table = table [0 : MAX_RESULT_LENGTH]
            is_shortened.append(True)
            
        result_tables.append(table)
        
    for index in sorted(bad_query_indices, reverse=True):
        del result_tables[index]
        del result_queries[index]
    
    mock.close()
    
    results = {"queries": result_queries, "tables": result_tables, "col_names": col_names}
    
    return results


def run_query(query, db):
    db = pms.connect("localhost","sequelhelp_411","abducs411!!!!!", db)
    cursor = db.cursor()
    cursor.execute(query)
    db.commit()

    data = cursor.fetchall()
    db.close()
    return data
    
def get_next_question():
    total = run_query('SELECT count(*) FROM Questions', 'sequelhelp_mock')[0][0]
    query = 'SELECT cq.question_id, q.Question FROM Questions q, current_question cq WHERE cq.user_id =' + str(current_user.id) + ' AND cq.question_id = q.QuestionId'
    
    result = run_query(query, 'sequelhelp_mock')[0]

    if (len(result)):
        question_id = result[0]
        
        new_question_id = (question_id + 1) % (total+1)
        if (new_question_id == 0):
            new_question_id = 1
            
        run_query('UPDATE current_question SET question_id=' + str(new_question_id) + ' WHERE user_id=' + str(current_user.id) + ';', 'sequelhelp_mock')

    else:
        run_query('INSERT INTO current_question (user_id, question_id) VALUES ' + str(current_user.id) + ', 1);', 'sequelhelp_mock')
        new_question_id = 1
        
    question = run_query('SELECT Question FROM Questions WHERE QuestionId=' + str(new_question_id) + ';', 'sequelhelp_mock')[0][0]
        
    question = {'id': new_question_id, 'question': question}
    return question
    
# if the user has not  been assigned a question then
# give them one otherwise give the same question
def get_current_question():
    query = 'SELECT cq.question_id, q.Question FROM Questions q, current_question cq WHERE cq.user_id =' + str(current_user.id) + ' AND cq.question_id = q.QuestionId'
    
    result = run_query(query, 'sequelhelp_mock')
    total = run_query('SELECT count(*) FROM Questions', 'sequelhelp_mock')[0][0]
    
    if (result):
        question = result[0][1]
        question_id = result[0][0]
    else:
        run_query('INSERT INTO current_question (user_id, question_id) VALUES (' + str(current_user.id) + ', 1);', 'sequelhelp_mock')
        question_id = 1
        question = run_query('SELECT Question FROM Questions WHERE QuestionId=1', 'sequelhelp_mock')[0][0]
        

    question = {'id': question_id, 'question': question}
    
    return question
    
def get_question_pool():
    results = run_query('SELECT QuestionId, Question, AnswerQuery FROM Questions;', 'sequelhelp_mock')
    ret = []
    for r in results:
        ret.append({"id": r[0], "question": r[1], "answer": r[2]})
        
    return ret

def get_search(student_name, student_email, student_year, student_major):
    queryresult = 'SELECT name, email, year, major FROM user ' 
    selection = '' 
    if student_name: 
        selection += "AND name = '" + student_name + "' " 
    if student_email: 
        selection += "AND email = '" + student_email + "' " 
    if student_year != 'any': 
        selection += ("AND year = '" + student_year + "' ") 
    if student_major != 'any1': 
        selection += ("AND major = '" + student_major + "' ") 
    if len(selection) > 0: 
        queryresult += 'WHERE ' + selection[4: -1]
    results = run_query(queryresult, 'sequelhelp_users')
    ret = []
    for r in results:
        ret.append({"name": r[0], "email": r[1], "year": r[2], "major": r[3]})
        
    return ret
    
def compare_answer(s, e): 
    if len(s) != len(e) or len(s[0]) != len(e[0]): 
        return False 
    for x in range(len(s)): 
        for y in range(len(s[0])): 
            if s[x][y] != e[x][y]: 
                return False 
    return True 
    
################
    
@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
def profile():
    return render_template('profile.html')
    
    
@main.route('/parser')
@login_required
def parser():
    question = get_current_question()
    return render_template('parser.html', question=question)
    
@main.route('/parser', methods=['POST'])
@login_required
def parser_result(): 
    correct = ''
    question = ''
    student_results = ''
    question_id = ''
    expected_table = ''
    if(request.form.get('next')):
        question = get_next_question()
    
    
    elif(request.form.get('query')):
        student_query = request.form.get('query')
        student_results = parse_student_query(student_query)
        question = get_current_question()
        
        if ('error' not in student_results):
            correct = True 
            question_id = run_query('SELECT question_id FROM current_question WHERE user_id=' + str(current_user.id) + ';', 'sequelhelp_mock')[0][0]

            expected_table = get_expected_table(question_id)
            correct = compare_answer(student_results['tables'][-1], expected_table['table'])

    return render_template('parser.html', results=student_results, question=question, expected_table=expected_table, correct = correct)

@main.route('/instr_monitor')
def instr_monitor():
    students = [{"name": "Hassan"}, {"name": "Steve"}, {"name": "Eric"}, {"name": "Roy"}]
    return render_template('instr_monitor.html', students=students)

@main.route('/instr_q_bank')
@login_required
def instr_q_bank():
    q_pool = get_question_pool()
    return render_template('instr_q_bank.html', q_pool = q_pool)

@main.route('/instr_q_bank', methods=['POST'])
@login_required
def instr_q_bank_request():
    if(request.form.get('delete_question')):
        question_del_id = request.form.get('delete_question')
        run_query('DELETE FROM Questions WHERE QuestionId=' + str(question_del_id), 'sequelhelp_mock')
        run_query('UPDATE Questions SET QuestionId = QuestionId - 1 WHERE QuestionId > ' + str(question_del_id), 'sequelhelp_mock') 
        
        # CurrentQuestion.query.filter_by(question_id = question_del_id).delete()
        run_query('DELETE FROM current_question WHERE question_id=' + str(question_del_id) + ';', 'sequelhelp_mock')

        db.session.commit()
        
    elif(request.form.get('add_question')):
        question = request.form.get("new_question")
        answer = request.form.get("new_answer")
        query = 'INSERT INTO Questions(QuestionId, Question, AnswerQuery) VALUES((SELECT MAX(QuestionId) + 1 FROM (SELECT * FROM Questions) as q2), \'' + str(question) + '\',\'' + str(answer) + '\');'
        
        #query = 'INSERT INTO Questions(Question, AnswerQuery) VALUES(\'' + str(question) + '\',\'' + str(answer) + '\');'
        run_query(query, 'sequelhelp_mock')
        
    elif(request.form.get('update_question')):
        question_id = request.form.get('update_question')
        question = request.form.get('question_' + str(question_id))
        answer = request.form.get('answer_' + str(question_id))
        
        query = 'UPDATE Questions SET Question=\'' + str(question) + '\', AnswerQuery=\'' + str(answer) + '\' WHERE QuestionId=' + str(question_id)
        run_query(query, 'sequelhelp_mock')
        
    q_pool = get_question_pool()
    return render_template('instr_q_bank.html', q_pool = q_pool)
    
    
@main.route('/student_manager')
@login_required
def student_manager():
    return render_template('student_manager.html')
    
@main.route('/student_manager', methods=['POST'])
@login_required
def student_manager_result():
    student_name = request.form.get('name')
    student_email = request.form.get('email')
    student_year = request.form.get('year')
    student_major = request.form.get('major')
    cur_search = get_search(student_name, student_email, student_year, student_major)

    return render_template('student_manager.html', result = cur_search)



