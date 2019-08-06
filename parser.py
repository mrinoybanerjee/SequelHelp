import re 


# string = 'SELECT c.FirstName, c.LastName, COUNT(*) FROM Customers c, Purchases pu, Products pr WHERE c.CustomerId = pu.CustomerId AND pu.ProductId = pr.ProductID AND c.CustomerId IN ( SELECT pu2.CustomerId FROM Purchases pu2 WHERE pu2.Price <= ALL(SELECT pu3.Price FROM Purchases pu3 WHERE pu3.ProductId = pu2.ProductId)) GROUP BY pu.CustomerId ORDER BY c.CustomerId DESC;' 

def find_end(string, start):
    i = 1 
    copy = start 
    while copy < len(string):
        if string[copy] == '(':
            i += 1 
        elif string[copy] == ')':
            i -= 1 
        copy += 1 
        if i == 0: 
            copy -= 1 
            return copy 
    return copy 

def get_indexes(string):
    starts = [m.start() for m in re.finditer('SELECT', string.upper())] 
    ends = [find_end(string, i) for i in starts] 
    indexes = [[starts[i], ends[i]] for i in range(len(starts))] 
    if indexes[0] != [0, len(string)]: 
        indexes.insert(0, [0, len(string)]) 
    return indexes 

def get_ordered(indexes): 
    count = len(indexes) 
    outputed = [0 for i in range(count)] 
    ordered = [] 
    stack = [0] 
    while True: 
        if (stack[-1] == count - 1) or (sum(outputed[stack[-1] + 1: ]) == count - stack[-1] - 1): 
            while len(stack) > 0: 
                ordered.append(stack.pop()) 
            break 
        start, end = indexes[stack[-1]] 
        next = stack[-1] + 1 
        while outputed[next] == 1: 
            next += 1 
        next_s, next_e = indexes[next] 
        if end > next_s: 
            stack.append(next) 
        else: 
            output = stack.pop() 
            ordered.append(output) 
            outputed[output] = 1 
    return [indexes[i] for i in ordered] 

def breakdown(string, ordered): 
    result = [] 
    for start, end in ordered: 
        if end != len(string): 
            result.append(string[start: end] + ';') 
        else: 
            result.append(string[start: end]) 
    return result 
    
def breakdown_omitted(string, ordered): 
    result = [] 
    for i in range(len(ordered)): 
        start, end = ordered[i] 
        if end != len(string): 
            s = list(string[start: end] + ';') 
        else: 
            s = list(string[start: end]) 
        for j in range(i): 
            os, oe = ordered[j] 
            if (start < os and end > oe): 
                for k in range(os - start, oe - start):
                    s[k] = '-' 
        result.append(''.join(s)) 
    return result 
    
def frag_indexes(omitted): 
    keywords = ['FROM', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'DESC', 'LIMIT'] 
    result = [] 
    for omit in omitted: 
        starts = [] 
        for keyword in keywords: 
            if omit.upper().find(keyword) > -1: 
                starts.append(omit.upper().find(keyword)) 
        result.append(starts) 
    return result 
    
def get_steps(pieces, frags): 
    step = [] 
    for i in range(len(pieces)): 
        for j in range(len(frags[i])):
            if j == len(frags[i]) - 1: 
                step.append('SELECT * ' + pieces[i][frags[i][0]: ]) 
            else: 
                step.append('SELECT * ' + pieces[i][frags[i][0]: frags[i][j + 1]] + ';') 
        step.append(pieces[i]) 
    return list(dict.fromkeys(step)) 

def parse(string):
    ordered = get_ordered(get_indexes(string)) 
    pieces = breakdown(string, ordered)
    frags = frag_indexes(breakdown_omitted(string, ordered))
    return get_steps(pieces, frags) 