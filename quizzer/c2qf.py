import re

INLINE_TAGS_SUBST = {'python':{}}


def typeset_quizzes1(filestr, insert_missing_quiz_header=True):
    """
    Find all multiple choice questions in the string (file) filestr.
    Return filestr with comment indications for various parts of
    the quizzes.
    Method: extract all quizzes, replace each quiz by a new format
    consisting of digested text between begin-end comments, run
    doconce text transformations, interpret the begin-end comments
    and store quiz info in a data structure, send data structure
    to a format-specific function for final rendering (the text is
    already in the right format).
    """
    # Should have possibility to have textarea as answer to
    # question for future smart regex checks of the answer, maybe
    # also upload files.
    # Should also have the possibility to include sound files
    # for applause etc. from Dropbox/collected../ideas/doconce/sound

    pattern = '^!bquiz.+?^!equiz'
    quiztexts = re.findall(pattern, filestr, flags=re.DOTALL|re.MULTILINE)
    headings = [('', None)]*(len(quiztexts))
    # Find the heading before each quiz (can be compared with H: ...)
    pieces = filestr.split('!bquiz')
    # Can only do this when there are no extra inline !bquiz words
    # inside the text (because of the above split), just !bquiz in quiz envirs
    if len(pieces) == len(quiztexts) + 1:
        for i, piece in enumerate(pieces[:-1]):
            for line in reversed(piece.splitlines()):
                if line.startswith('===== '):
                    if re.search(r'=====\s+\{?(Exercise|Project|Problem|Example)', line):
                        headings[i] = line, 'exercise'
                    else:
                        headings[i] = line, 'subsection'
                    break
                elif line.startswith('======='):
                    headings[i] = line, 'section'
                    break
                """
                elif line.startswith('!bquestion') or line.startswith('!bnotice') or line.startswith('!bsummary'):
                    # Can have quiz in admons too
                    words = line.split()
                    if len(words) > 1:
                        headings[i] = (' '.join(words[1:]), words[2:] + '-admon')
                        break
                """
    quizzes = []
    for text, heading in zip(quiztexts, headings):
        new_text = interpret_quiz_text(text, insert_missing_quiz_header,
                                       heading[0], heading[1])
        quizzes.append(new_text)
        filestr = filestr.replace(text, new_text)

#     print(filestr, len(quiztexts))
    return filestr, len(quiztexts)



def interpret_quiz_text(text, insert_missing_heading= False,
                        previous_heading=None, previous_heading_tp=None):
    """
    Replace quiz (in string text) with begin-end groups typeset as
    comments. The optional new page and heading lines are replaced
    by one-line comments.
    The function extract_quizzes can recognize the output of the
    present function, and create a data structure with the quiz
    content..
    """
    ct = comment_tag
    bct = begin_comment_tag
    ect = end_comment_tag

    data = {}
    # New page? NP
    pattern = r'^NP:(.+)'
    m = re.search(pattern, text, flags=re.MULTILINE)
    if m:
        header = m.group(1).strip()
        text = re.sub(pattern, ct('--- new quiz page: ' + header), text,
                      flags=re.MULTILINE)
    # Heading?
    pattern = r'^H:(.+)'
    m = re.search(pattern, text, flags=re.MULTILINE)
    if m:
        heading = m.group(1).strip()
        if insert_missing_heading and isinstance(previous_heading, basestring):
            if heading.lower() not in previous_heading.lower():
                # Quiz heading is missing and wanted
                text = '===== Exercise: %s =====\n\n' % heading + text
                # no label, file=, solution= are needed for quizes
                previous_heading_tp = 'exercise'
        heading_comment = ct('--- quiz heading: ' + heading) + '\n' + ct('--- previous heading type: ' + str(previous_heading_tp))
        text = re.sub(pattern, heading_comment, text, flags=re.MULTILINE)
    else:
        # Give info about previous heading type
        if previous_heading_tp is not None:
            text = ct('--- previous heading type: ' + str(previous_heading_tp)) + '\n' + text


    def begin_end_tags(tag, content):
        return """
%s
%s
%s
""" % (bct(tag), content, ect(tag))

    # Question
    pattern = r'(^Q:(.+?))(?=^(C[rw]|K|L):)'
    m = re.search(pattern, text, flags=re.MULTILINE|re.DOTALL)
    if m:
        question = m.group(2).strip()
        text = text.replace(m.group(1), begin_end_tags('quiz question', question))
    else:
        errwarn('*** error: found quiz without question!')
        errwarn(text)
        _abort()

    # Keywords
    pattern = r'^(K:(.+))$'
    m = re.search(pattern, text, flags=re.MULTILINE)
    if m:
        keywords = [s.strip() for s in m.group(2).split(';')]
        text = text.replace(m.group(1), ct('--- keywords: ' + str(keywords)))

    # Label
    pattern = r'^(L:(.+))$'
    m = re.search(pattern, text, flags=re.MULTILINE)
    if m:
        text = text.replace(m.group(1), ct('--- label: ' + str(m.group(2).strip())))

    # Choices: grab choices + optional explanations first,
    # then extract explanations.
    # Need end-of-string marker, cannot use $ since we want ^ and
    # re.MULTILINE ($ is then end of line)
    text += '_EOS_'
    pattern = r'^(C[rw]:(.+?))(?=(^C[rw]:|L:|K:|_EOS_|^!equiz))'
    choices = re.findall(pattern, text, flags=re.MULTILINE|re.DOTALL)
    text = text[:-5]  # remove _EOS_ marker
    counter = 1
    if choices:
        for choice_text, choice, _lookahead in choices:
            if re.search(r'^[KL]:', choice, flags=re.MULTILINE):
                errwarn('*** error: keyword or label cannot appear between a')
                errwarn('    choice and explanation in a quiz:')
                errwarn(choice)
                _abort()
            right = choice_text.startswith('Cr')  # right or wrong choice?
            explanation = ''
            if re.search(r'^E:', choice, flags=re.MULTILINE):
                choice, explanation = re.split(r'^E:\s*',
                                               choice, flags=re.MULTILINE)
                text = text.replace(choice_text, begin_end_tags('quiz choice %d (%s)' % (counter, 'right' if right else 'wrong'), choice.strip()) + begin_end_tags('explanation of choice %d' % counter, explanation.strip()))
            else:
                text = text.replace(choice_text, begin_end_tags('quiz choice %d (%s)' % (counter, 'right' if right else 'wrong'), choice.strip()))
            counter += 1
    else:
        errwarn('*** error: found quiz without choices!')
        errwarn(text)
        _abort()
    text = re.sub('^!bquiz', bct('quiz'), text,
                  flags=re.MULTILINE)
    text = re.sub('^!equiz', ect('quiz'), text,
                  flags=re.MULTILINE)
#     print(text)
    return text

_QUIZ_BLOCK = '<<<!!QUIZ_BLOCK'



def extract_quizzes(filestr, format):
    """
    Replace quizzes, formatted as output from function interpret_quiz_text,
    by a Python data structure and a special instruction where formatting
    of this data structure is to be inserted.
    """
    from collections import OrderedDict
    ct = comment_tag
    bct = begin_comment_tag
    ect = end_comment_tag
    cp = '# %s' #INLINE_TAGS_SUBST[format].get('comment', '# %s') # comment pattern
#     if format in ("rst", "sphinx"):
#         #cp = '.. %s\n'  # \n gives error if text follows right after !equiz
#         cp = '.. %s'
#     if not isinstance(cp, basestring):
#         raise TypeError
    # line start: must allow spaces first in rst/sphinx, but quiz inside
    # indented admons do not work anyway in rst/sphix
    line_start = '^ *'  # could be rst/sphinx fix, but does not work
    line_start = '^'  # comments start in 1st column
    pattern = line_start + bct('quiz', cp) + '.+?' + ect('quiz', cp)
    quizzes = re.findall(pattern, filestr, flags=re.DOTALL|re.MULTILINE)
    data = []
    for i, quiz in enumerate(quizzes):
        data.append(OrderedDict())
        data[-1]['no'] = i+1
        filestr = filestr.replace(quiz, '%d %s' % (i, _QUIZ_BLOCK))
        # Extract data in quiz
        pattern = line_start + ct('--- new quiz page: (.+)', cp)
        m = re.search(pattern, quiz, flags=re.MULTILINE)
        if m:
            data[-1]['new page'] = m.group(1).strip()
        pattern = line_start + ct('--- quiz heading: (.+)', cp)
        m = re.search(pattern, quiz, flags=re.MULTILINE)
        if m:
            data[-1]['heading'] = m.group(1).strip()
        pattern = line_start + ct('--- previous heading type: (.+)', cp)
        m = re.search(pattern, quiz, flags=re.MULTILINE)
        if m:
            data[-1]['embedding'] = m.group(1).strip()

        pattern = line_start + bct('quiz question', cp) + '(.+?)' + ect('quiz question', cp)
        m = re.search(pattern, quiz, flags=re.MULTILINE|re.DOTALL)
        if m:
            question = m.group(1).strip()
            # Check if question prefix is specified
            # Q: [] Here goes the question...
            prefix_pattern = r'^\[(.*?)\]'
            m = re.search(prefix_pattern, question)
            if m:
                prefix = m.group(1)
                question = re.sub(prefix_pattern, '', question).strip()
                data[-1]['question prefix'] = prefix
            data[-1]['question'] = question
        else:
            errwarn('*** error: malformed quiz, no question')
            errwarn(quiz)
            errwarn('\n     Examine the corresponding doconce source code for syntax errors.')
#             _abort()

        pattern = line_start + ct('--- keywords: (.+)', cp)
        m = re.search(pattern, quiz, flags=re.MULTILINE)
        if m:
            try:
                keywords = eval(m.group(1))  # should have list format
            except Exception as e:
                errwarn('*** keywords in quiz have wrong syntax (should be semi-colon separated list):')
                errwarn(m.group(1))
                errwarn('    Quiz question: ' + question)
#                 _abort()
            data[-1]['keywords'] = keywords

        pattern = line_start + ct('--- label: (.+)', cp)
        m = re.search(pattern, quiz, flags=re.MULTILINE)
        if m:
            data[-1]['label'] = m.group(1).strip()

        pattern = line_start + bct('quiz choice (\d+) \((right|wrong)\)', cp) + '(.+?)' + ect('quiz choice .+?', cp)
        choices = re.findall(pattern, quiz, flags=re.MULTILINE|re.DOTALL)
        data[-1]['choices'] = []
        data[-1]['choice prefix'] = [None]*len(choices)
        for i, right, choice in choices:
            choice = choice.strip()
            # choice can be of the form [Solution:] Here goes the text...
            m = re.search(prefix_pattern, choice)
            if m:
                prefix = m.group(1).strip()
                choice = re.sub(prefix_pattern, '', choice).strip()
                data[-1]['choice prefix'][int(i)-1] = prefix
            data[-1]['choices'].append([right, choice])
        # Include choice prefix only if it is needed
        if data[-1]['choice prefix'] == [None]*len(choices):
            del data[-1]['choice prefix']
        pattern = line_start + bct('explanation of choice (\d+)', cp) + '(.+?)' + ect('explanation of choice \d+', cp)
        explanations = re.findall(pattern, quiz, flags=re.MULTILINE|re.DOTALL)
        for i_str, explanation in explanations:
            i = int(i_str)
            try:
                data[-1]['choices'][i-1].append(explanation.strip())
            except IndexError:
                errwarn("""
            *** error: quiz question
            "%s"
            has choices
            %s
            Something is wrong with the matching of choices and explanations
            (compare the list above with the source code of the quiz).
            This is a bug or wrong quiz syntax.
            The raw code of this quiz at this stage of processing reads
            %s
            """ % (data[-1]['question'], data[-1]['choices'], quiz))
#                         _abort()

    data = {"activity": "poll",
                     "instructors": ["imachine"],
                     'types':[],
                     "items":data}
    
                    
    for item in data['items']:
        for key, value in item.items():
            if isinstance(value, list):
                item[key] = []
                for options in value:
                    if isinstance(options, list):
                        item[key].append([sub_word(option)for option in options])
                    elif isinstance(options, str):
                        item[key].append(sub_word(options))

            elif isinstance(value, str):
                item[key] = sub_word(value)
                
    
    return data, quizzes, filestr

def sub_word(strn):
    tags = {'!bc pycod':'```python', '!bc pypro':'```python', '!ec':'```', '!bt':'$$', '!et':'$$'}
    for k, v in tags.items():
        strn = re.sub(k, v, strn)
#     strn = re.sub('!bc pycod', '```python', strn)
#     strn = re.sub('!bc pypro', '```python', strn)
#     strn = re.sub('!ec', '```', strn)
    
    return strn



# Functions for creating and reading comment tags
def begin_end_comment_tags(tag):
    return '--- begin ' + tag + ' ---', '--- end ' + tag + ' ---'

def comment_tag(tag, comment_pattern='# %s'):
    return comment_pattern % tag

def begin_comment_tag(tag, comment_pattern='# %s'):
    return comment_pattern % (begin_end_comment_tags(tag)[0])

def end_comment_tag(tag, comment_pattern='# %s'):
    return comment_pattern % (begin_end_comment_tags(tag)[1])