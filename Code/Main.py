"""
# Main file
"""

# Dependencies
import multiprocessing as mp
mp.freeze_support()
import Database_Management as dm
import win_unicode_console
win_unicode_console.enable()
import State_Tracker as st
import Find_Files as ff
import Globals as glbl
import traceback as t
import Listener
import Reader
import time
# import sys
# sys.stderr = sys.__stderr__


def initialise():
    """
    # Prepare the work environment:
        - create directory database
        - determine previous, start and next addresses
    """
    glbl.file_locales = ff.discoverFiles(glbl.start_directory)
    [files, folders] = glbl.file_locales
    glbl.database = dm.getStoryDatabase(files, folders)

    # @todo first node = None
    glbl.address_stack.append(st.getStartNode(files))
    glbl.address_stack.append(st.getStartNode(files))
    return


def read(reader, text):
    """
    Pass single sentences for processing over to the reader
    :param reader:
    :param text:
    :return:
    """
    to_reader = [['Text', str(text), []]]
    reader.stack += to_reader


def main():
    """
    The main function
    :return:
    """
    with open("log_file.txt", "a") as log_file:
        log_file.write('\n\nNEW GAME START!' + '\n')
    # Begin the game
    initialise()
    listener = Listener.ListenerObj()
    reader = Reader.ReaderObj()
    st.readNarrative(reader)
    reader.checkReaderStatus()

    try:
        # Play the game
        while True:
            # Block whilst the narrator reads the script
            # @todo convert to non-blocking method to allow interrupts
            glbl.ignore_addresses = []
            glbl.is_reading = reader.alive
            while reader.alive is True:
                listener.should_listen = False
                listener.checkListenerStatus()
                reader.checkReaderStatus()
                time.sleep(0.01)

            # Interrupts should be cleared only once the reader has finished reading
            # glbl.interrupt_addresses = []
            glbl.is_reading = False

            # Get the users narrative options
            types = st.getNarrativeOptions()
            # print(str(list(glbl.next_addresses.keys())))

            # If the reader is reading, then ignore 'auto' preferences
            # Otherwise, default to auto if it is available
            if reader.alive is False and 'auto' in types:
                select = 'auto'
            else:
                # Wait for a specific amount of time before defaulting to $Silent
                t1 = time.time()
                select = '$Silence'
                listener.should_listen = True

                while time.time() < t1+30 or listener.num_selectors is not 0:
                    # If over the time period, stop listening
                    if time.time() > t1+30:
                        listener.should_listen = False

                    # Update the listener & reader statuses
                    listener.checkListenerStatus()
                    reader.checkReaderStatus()

                    # Check if the listener thinks the user said something.
                    # If so, then hmm and um until processing has finished
                    if listener.num_selectors is not 0 and reader.alive is False:
                        reader.interruptable = True
                        read(reader, "Hmm hmm hmm... Um... Uhh... "*5)

                    # Check whether a selection has been made
                    if len(listener.stack_user_input) > 0:
                        select = listener.stack_user_input[0][0]
                        break

                    # Wait patiently before checking again
                    time.sleep(0.5)
                listener.dumpStackUserInput()
                listener.dumpStackSelector()

            # Get the users selection
            string = st.getSelection(select)

            # ###################################### TESTING LISTENER INTEGRATION!
            reader.stopReader()
            reader.dumpStack()
            reader.interruptable = False

            # Double check that the user hasn't made an error
            if st.updateAddresses(string, False) is False:
                string = '$Creator_Error'
                st.updateAddresses(string, False)

            # Update the narrative
            st.readNarrative(reader)
            reader.checkReaderStatus()
    except Exception as e:
        with open("log_file.txt", "a") as log_file:
            log_file.write(str(t.format_exc()))
            log_file.write('Program Error - {0}'.format(e) + '\n')
    finally:
        print('\n\nAN ERROR HAS OCCURRED! THIS GAME IS NOW CLOSING!\n\n')
        time.sleep(5)


if __name__ == '__main__':
    main()
















