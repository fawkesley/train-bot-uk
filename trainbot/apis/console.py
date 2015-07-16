
def write_to_console(outbound_message):
    print('CONSOLE {0}: {1}'.format(outbound_message.recipient,
                                    outbound_message.content))
