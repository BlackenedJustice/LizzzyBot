def log_text(text, cmd_name=''):
    file = open('log.txt', 'a')
    if cmd_name != '':
        file.write(cmd_name + ': ' + text)
    else:
        file.write(text)
    file.write('\n')
    file.close()


def log_event(user_id, text, user_name=''):
    file = open('log.txt', 'a')
    if user_name != '':
        file.write(user_name + ' - ' + str(user_id) + ': ' + text)
    else:
        file.write(str(user_id) + ': ' + text)

    file.write('\n')
    file.close()
