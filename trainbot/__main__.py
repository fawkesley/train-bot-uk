#!/usr/bin/env python

import logging
import sys

from multiprocessing import Process, Queue

from .config import MESSAGE_RECEIVERS
from .messages import InboundMessage, StopProcessing
from .handle_message import handle_message
from .send_reply import send_reply

NUM_MESSAGE_HANDLERS = 2
NUM_REPLY_SENDERS = 2

LOG = logging.getLogger(__name__)


def start_n_processes(n, function, args):
    processes = []
    for _ in range(n):
        p = Process(
            target=function,
            args=args
        )
        p.start()
        processes.append(p)
    return processes


def _handle_command_line_options():
    if len(sys.argv) == 2:
        if sys.argv[1] == '--debug':
            return True
        else:
            sys.stderr.write('Usage: {} [--debug]\n'.format(sys.argv[0]))
            sys.exit(2)
    return False


def _get_test_messages_from_stdin(inbound_message_queue):
    while True:
        test_message = input('Enter message [enter to exit]: ')
        if not test_message:
            break

        inbound_message_queue.put(
            InboundMessage(
                channel='console',
                sender='me',
                content=test_message,
                extra={}))


def main():
    logging.basicConfig(level=logging.DEBUG)
    debug = _handle_command_line_options()

    inbound_message_queue = Queue()
    outbound_message_queue = Queue()

    receiver_processes = []

    if not debug:
        for channel_name, receive_function, n_processes in MESSAGE_RECEIVERS:

            receiver_processes.extend(
                start_n_processes(
                    n_processes,
                    receive_function,
                    (inbound_message_queue, channel_name)))
    else:
        receiver_processes = []

    message_handler_processes = start_n_processes(
        NUM_MESSAGE_HANDLERS,
        handle_message,
        (inbound_message_queue, outbound_message_queue))

    send_reply_processes = start_n_processes(
        NUM_REPLY_SENDERS,
        send_reply,
        (outbound_message_queue,))

    _get_test_messages_from_stdin(inbound_message_queue)

    LOG.info('Sending StopProcessing to all queues.')

    for p in receiver_processes:
        p.terminate()

    for _ in range(NUM_MESSAGE_HANDLERS):
        inbound_message_queue.put(StopProcessing)

    for _ in range(NUM_REPLY_SENDERS):
        outbound_message_queue.put(StopProcessing)

    for p in message_handler_processes + send_reply_processes:
        p.join()
