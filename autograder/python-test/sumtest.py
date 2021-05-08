import json

from solution import *

score = 0
out = ''

if mysum(5, 8) == 13:
    score += 1
    out += 'Correct\n'
else:
    out += f'Test: 5+8, expected: 13, got {mysum(5,8)}\n'

result = {
    'score': score,
    'output': out,
}

print(json.dumps(result))