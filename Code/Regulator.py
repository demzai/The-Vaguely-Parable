"""
The code presented focuses on regulating the listener, selector and reader child processes.
It provides the overarching control of all three sub-systems.
The code here calls child processes... thread safety rules apply.
Use protection, get consent, and play nice kids!
"""

# Dependencies:
import Reader
import Listener
import Selector


def resetChildProcess(curr_process, creator_function):
    """
    Forcibly kill off a given child process and replace it with a new one
    :param curr_process:
    :param creator_function:
    :return:
    """
    curr_process.terminate()
    return creator_function()


def main():
    """
    The main function!
    :return:
    """
    [listen, user_input, is_listen_faulty] = Listener.startListener()
    [select, selector_inputs, selector_results, is_select_faulty] = Selector.startSelector()
    [read, to_be_read, is_reader_faulty] = Reader.startReader()

    try:
        prev_state = [False, False, False]
        while True:
            # Ensure that the listener and reader processes are fully functional
            if is_listen_faulty is True:
                [listen, user_input, is_listen_faulty] = resetChildProcess(listen, Listener.startListener)
            if is_select_faulty is True:
                [select, selector_inputs, selector_results, is_select_faulty] = \
                    resetChildProcess(select, Selector.startSelector)
            if is_reader_faulty is True:
                [read, to_be_read, is_reader_faulty] = resetChildProcess(read, Reader.startReader)

            # Check the status of the listener
            with user_input[1]:
                # If the listener has picked something up...
                if user_input[0][-1] is True and prev_state[0] is False:
                    # Set the selector running - assumes it isn't already based on the rest of the logic
                    with selector_inputs[1]:
                        selector_inputs[0][0] = user_input[0][0]
                        selector_inputs[0][-1] = True
                    prev_state[0] = True
                # If not, then never mind
                else:
                    pass

            # Check the status of the selector and reader
            with selector_inputs[1] and to_be_read[1]:
                is_selector_busy = selector_inputs[0][-1]
                is_reader_reading = to_be_read[0][-1]

            # Otherwise, if the selector is busy, then the user is probably waiting for a response.
            if is_selector_busy is True and is_reader_reading is False:
                # Play some filler inflexions whilst the user waits (hmm...)
                prev_state[1] = True
                with to_be_read[1]:
                    to_be_read[0][0] = 'Hmm hmm hmm... Um... Uhh... '*5
                    to_be_read[0][-1] = True

            # If the selector has just finished
            elif is_selector_busy is False and prev_state[1] is True:
                # If the reader is currently reading, then forcibly stop it so it can say the important stuff
                if is_reader_reading is True:
                    [read, to_be_read, is_reader_faulty] = resetChildProcess(read, Reader.startReader)
                # Play the next thing (in this case, repeat what the computer thinks the user just said back to them
                with selector_results[1] and to_be_read[1]:
                    print(str(selector_results[0][0][0]))
                    to_be_read[0][0] = selector_results[0][0][0][0]
                    to_be_read[0][-1] = True
                prev_state[1] = False
                prev_state[2] = True

            # If the reader has just finished reading...
            elif is_reader_reading is False and prev_state[2] is True:
                # Restart the listener
                with user_input[1]:
                    user_input[0][-1] = False
                prev_state[0] = False
                prev_state[2] = False

    finally:
        listen.terminate()
        select.terminate()
        read.terminate()


if __name__ == '__main__':
    main()
