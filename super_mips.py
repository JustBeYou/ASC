from sys import argv

def getIndentation(line):
    return (len(line) - len(line.lstrip())) * ' '

def getArgs(line):
    return [x for x in line if x != '']

# $t0 is used internally!!!
# TODO: fix this BUG: you can't use variables with the same name in different functions! (same problem for arguments)
# TODO: fix this BUG: variables are replaced with .replace and that could lead to substring replaces
# TODO: add checking for errors

# !!! Some directives must be used in a predefined oreder or you could mess up the stack
# CALL function
# function:
# SAVE registers
# DECLARE locals
# other instructions
# return
def parseProgram(lines):
    parsedLines = []

    currentFunction = None
    functionPosition = 0
    frameSize = 0
    variables = {}
    arguments = {}
    saved = []
    savedSize = 0
    for i, line in enumerate(lines):
        indent = getIndentation(line)
        line = line.split(' ')
        args = getArgs(line)
        if 'func' in line:
            currentFunction = line[-1][:-1]
            frameSize = 0
            saved = []
            savedSize = 0
            argumentSize = 0

            line.remove('func')
            parsedLines.append(' '.join(line))
            parsedLines.append(indent + 'sw $ra, ($sp)')
            parsedLines.append(indent + 'subu $sp, $sp, 4')
            functionPosition = len(parsedLines)
        elif 'return' in line or 'exit' in line:
            # destroy stack frame and return - return
            # call exit system call          - exit
            if 'exit' in line:
                parsedLines.append(indent + 'li $v0, EXIT_SYSCALL')
                parsedLines.append(indent + 'syscall')
            else:
                # return <mem/reg/const> <value to return>
                parsedLines.insert(functionPosition + 0, indent + 'subu $sp, $sp, {}'.format(savedSize))
                parsedLines.insert(functionPosition + 1, indent + 'sw $fp, ($sp)')
                parsedLines.insert(functionPosition + 2, indent + 'subu $sp, $sp, 4')
                parsedLines.insert(functionPosition + 3, indent + 'move $fp, $sp')
                parsedLines.insert(functionPosition + 4, indent + 'subu $sp, $sp, {}'.format(frameSize))
                parsedLines.insert(functionPosition + 5, '')

                if len(args) == 3:
                    parsedLines.append('')
                    if args[1] == 'reg':
                        parsedLines.append(indent + 'move $v0, {}'.format(args[2]))
                    elif args[1] == 'mem':
                        parsedLines.append(indent + 'lw $t0, {}'.format(args[2]))
                        parsedLines.append(indent + 'move $v0, $t0')
                    elif args[1] == 'const':
                        parsedLines.append(indent + 'li $v0, {}'.format(args[2]))

                parsedLines.append('')
                parsedLines.append(indent + 'addiu $sp, $sp, {}'.format(frameSize + 4))
                parsedLines.append(indent + 'lw $fp, 0($sp)')

                if savedSize: parsedLines.append(indent + 'addiu $sp, $sp, {}'.format(4))
                oldSavedSize = savedSize
                for reg in saved:
                    savedSize -= 4
                    parsedLines.append(indent + 'lw {}, {}($sp)'.format(reg, savedSize))
                if oldSavedSize: parsedLines.append(indent + 'addiu $sp, $sp, {}'.format(oldSavedSize))

                parsedLines.append(indent + 'lw $ra, 0($sp)')
                parsedLines.append(indent + 'addiu $sp, $sp, 4')
                parsedLines.append(indent + 'jr $ra')

            currentFunction = 0
        elif 'var' in line:
            # var <name> <value>
            variables[args[1]] = frameSize
            parsedLines.append(indent + 'li $t0, {}'.format(args[2]))
            parsedLines.append(indent + 'sw $t0, -{}($fp)'.format(frameSize))
            frameSize += 4

        elif 'save' in line:
            parsedLines.append(indent + 'sw {}, -{}($sp)'.format(args[1], savedSize))
            savedSize += 4
            saved.append(args[1])
            functionPosition += 1

        elif 'arg' in line:
            arguments[args[1]] = 4 + savedSize + 8 + argumentSize
            argumentSize += 4
        elif 'push' in line:
            pass
        elif 'pop' in line:
            pass
        elif 'call' in line:
            funcName = args[1]
            args = args[2:]
            if len(args) > 0:
                parsedLines.append(indent + 'subu $sp, $sp, {}'.format(len(args) * 4))
                for i, arg in enumerate(args):
                    if arg[:3] == 'var':
                        parsedLines.append(indent + 'lw $t0, {}'.format(arg))
                        parsedLines.append(indent + 'sw $t0, {}($sp)'.format(i * 4))
                    else:
                        parsedLines.append(indent + 'sw {}, {}($sp)'.format(arg, i * 4))
            parsedLines.append(indent + 'subu $sp, $sp, 4')
            parsedLines.append(indent + 'jal {}'.format(funcName))
            if len(args) > 0:
                parsedLines.append(indent + 'addiu $sp, $sp, {}'.format(len(args) * 4))
        else:
            parsedLines.append(' '.join(line))


    content = '\n'.join(parsedLines)
    for var in variables:
        content = content.replace(var, '-{}($fp)'.format(variables[var]))
    for var in arguments:
        content = content.replace(var, '{}($fp)'.format(arguments[var]))

    return content

if len(argv) != 2:
    print ("Usage: ./super_mips.py <file>")
    exit(1)

with open(argv[1], 'r') as f:
    content = f.read()

lines = content.split('\n')
content = parseProgram(lines)
with open(argv[1] + '.super', 'w') as f:
    f.write(content)
