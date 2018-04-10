"""
# Main file
"""

# Dependencies
import time
import Database_Management as dm
import Find_Files as ff
import Globals as glbl
import Reader
import State_Tracker as st


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
    # Begin the game
    initialise()
    reader = Reader.ReaderObj()
    st.readNarrative(reader)
    reader.checkReaderStatus()

    try:
        # Play the game
        while True:
            # Block whilst the narrator reads the script
            # @todo convert to non-blocking method to allow interrupts
            glbl.is_reading = reader.alive
            while reader.alive is True:
                reader.checkReaderStatus()
                time.sleep(0.01)
            glbl.is_reading = False

            # Get the users narrative selection
            st.getNarrativeOptions()

            # Get the users selection
            string = st.getSelection()

            # Double check that the user hasn't made an error
            if st.updateAddresses(string, False) is False:
                # print(pc.IRed + 'ERROR - "' + str(string) + '" IS NOT AN OPTION!' + pc.Reset)
                # print(pc.IBlue + 'Please try again.' + pc.Reset)
                read(reader, 'ERROR: "' + str(string) + '" IS NOT AN OPTION!')
                read(reader, 'Please try again.')
                reader.checkReaderStatus()
                with open("log_file.txt", "a") as log_file:
                    log_file.write('User Error - ERROR - "' + str(string) + '" IS NOT AN OPTION!' + '\n')
            else:
                st.readNarrative(reader)
                reader.checkReaderStatus()
    except Exception as e:
        with open("log_file.txt", "a") as log_file:
            log_file.write('Program Error - {0}'.format(e) + '\n')
        print('{0}'.format(e))
    finally:
        print('AN ERROR HAS OCCURRED! THIS GAME IS NOW CLOSING!')
        time.sleep(5)


if __name__ == '__main__':
    main()
















