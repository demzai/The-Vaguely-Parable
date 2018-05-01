"""
The code presented focuses on retrieving audio spoken by the user.
It provides a listen when spoken to service that can run independently from the rest of the system.
The code here is intended to be called as a child process... thread safety rules apply.
Use protection, get consent, and play nice kids!
"""

# Dependencies:
import speech_recognition as sr
import Code_Interpreter as ci
import multiprocessing as mp
import State_Tracker as st
import traceback as t
import Selector
import time


# noinspection PyBroadException
def listener(user_input, lock_user_input, is_faulty):
    """
    # Waits for user input, and provides the audio transcript of that input
    :param user_input:
    :param lock_user_input:
    :param is_faulty:
    :return:
    """
    try:
        recorder = sr.Recognizer()
        # recorder.energy_threshold = 500  # 10 to 25?
        with sr.Microphone() as source:
            while True:
                with lock_user_input:
                    should_wait = user_input[-1]
                # @todo remove non-listening period
                # @todo live-stream audio data
                # @todo manually check if user is talking?
                # If the main process isn't busy processing the previous input, then listen for use instructions
                if should_wait is False:
                    print("---Please speak when ready.---")
                    audio = recorder.listen(source)
                    timestamp = time.time()
                    with lock_user_input:
                        temp = user_input[0]
                        temp.update({timestamp: audio})
                        user_input[0] = temp
                        user_input[-1] = True
                # Otherwise, wait patiently for the main process to finish
                else:
                    time.sleep(0.5)
    except Exception as e:
        with open("log_file.txt", "a") as log_file:
            log_file.write(str(t.format_exc()) + '\n')
            log_file.write('Listener has failed unexpectedly. {0}\n'.format(e))
    finally:
        try:
            is_faulty[0] = True
        except FileNotFoundError:
            with open("log_file.txt", "a") as log_file:
                log_file.write("Listener: FileNotFoundError\n\n")


class ListenerObj:
    """
    Object used to simplify the interface with the listener object
    """
    def __init__(self):
        """
        # Initializer function for the listener class
        :return: list
        """
        self.should_listen = False
        self.alive = False
        self.stack_user_input = []
        self.__stack_selector = {}
        self.__selector_id = 0
        self.num_selectors = 0
        self.__user_input = mp.Manager().list([{}, False])  # [map of {timestamp: audio}, has_new_input]
        self.__is_faulty = mp.Manager().list([False])
        self.__lock_user_input = mp.Lock()
        self.__process = mp.Process(
            target=listener,
            args=(self.__user_input, self.__lock_user_input, self.__is_faulty)
        )

    def startListener(self):
        """
        # Initializer function for the listener
        :return: list
        """
        self.__user_input[-1] = False
        self.__is_faulty = mp.Manager().list([False])
        self.__lock_user_input = mp.Lock()

        self.__process = mp.Process(
            target=listener,
            args=(self.__user_input, self.__lock_user_input, self.__is_faulty)
        )
        self.__process.start()
        self.alive = True

    def stopListener(self):
        """
        Forcibly kill the listener if it is running
        :return:
        """
        if self.alive is True:
            self.__process.terminate()
            self.alive = False

    def __restartListener(self):
        """
        Restarts the Listener
        :return:
        """
        self.stopListener()
        self.startListener()

    def __updateAliveStatus(self):
        """
        Determines whether the listener should be active or not
        :return:
        """
        # Provide the user with the number of selectors currently running
        self.num_selectors = len(self.__stack_selector)

        # Check whether the listener has crashed
        self.alive = self.__process.is_alive()
        if self.alive is True and self.__is_faulty[0] is True:
            self.__restartListener()

        # If there's work to be done and the listener is dead, start it up
        if self.should_listen is True and self.alive is False:
            self.startListener()

        # If the listener shouldn't be listening
        elif self.should_listen is False and self.alive is True:
            self.stopListener()

    def checkListenerStatus(self):
        """
        Checks whether there's been an error within the listener and rectifies it if possible
        :return:
        """
        # Resolve (in)active status issues
        self.__updateAliveStatus()

        # Check if the listener has made another recording
        with self.__lock_user_input:
            has_new_input = self.__user_input[-1]

        # If there are new recordings, then create a new selector to process it
        if has_new_input is True:
            # Get the current narrative options once only
            narrative_options = st.getNarrativeOptions()
            with self.__lock_user_input:

                # For each new audio snippet:
                for audio in self.__user_input[0]:
                    # Create a new selector
                    self.__stack_selector.update(
                        {self.__selector_id: Selector.SelectorObj(
                            self.__user_input[0][audio], audio, narrative_options)})
                    self.__selector_id += 1

                    # Remove the audio entry from the listener
                    temp = self.__user_input[0]
                    temp.pop(audio, None)
                    self.__user_input[0] = temp

                # Tell the listener that the data has been collected
                self.__user_input[-1] = False

        # Check the status of each selector & retrieve user inputs if available
        to_be_removed = []
        broken = []
        for selector in self.__stack_selector:
            # Have it perform a self-check
            self.__stack_selector[selector].checkSelectorStatus()

            # Check for broken selectors
            if self.__stack_selector[selector].is_faulty is False:
                broken += [selector]
                continue

            # If its finished then return its results if they're non-empty
            elif self.__stack_selector[selector].is_finished is True and \
                    bool(self.__stack_selector[selector].selected_narrative) is True:
                to_be_removed += [selector]

                # If its an ignore, then don't show / add to the user input stack
                if self.__stack_selector[selector].selected_narrative[0] != '$Ignore':
                    self.stack_user_input += [self.__stack_selector[selector].selected_narrative]
                    if self.__stack_selector[selector].selected_narrative[0] == '$User_Error':
                        if self.__stack_selector[selector].result_google != '':
                            ci.interpretCode('#IHeard("{0}")'.format(
                                str(self.__stack_selector[selector].result_google[0])
                            ))
                        else:
                            ci.interpretCode('#IHeard("{0}")'.format(
                                str(self.__stack_selector[selector].result_sphinx[0])
                            ))
                # Make an exception if there's nothing else being processed
                elif len(self.__stack_selector) is 1:
                    self.stack_user_input += [self.__stack_selector[selector].selected_narrative]
            elif self.__stack_selector[selector].is_finished is True:
                broken += [selector]

        # Remove completed selectors
        for selector in to_be_removed:
            with open("log_file.txt", "a") as log_file:
                log_file.write('Google: ' + str(self.__stack_selector[selector].result_google) + '\n')
                log_file.write('WitAPI: ' + str(self.__stack_selector[selector].result_witapi) + '\n')
                log_file.write('Sphinx: ' + str(self.__stack_selector[selector].result_sphinx) + '\n')
                log_file.write('Select: ' + str(self.__stack_selector[selector].selected_narrative) + '\n')
            print('')
            print('Google: ' + str(self.__stack_selector[selector].result_google))
            print('WitAPI: ' + str(self.__stack_selector[selector].result_witapi))
            print('Sphinx: ' + str(self.__stack_selector[selector].result_sphinx))
            if len(self.__stack_selector[selector].selected_narrative[1]) >= 1:
                print('Select: ' + str(self.__stack_selector[selector].selected_narrative[1][0]))
            else:
                print('Select: ' + str(self.__stack_selector[selector].selected_narrative[1]))
            print('')
            self.__stack_selector.pop(selector, None)

        for selector in broken:
            self.__stack_selector.pop(selector, None)

    def dumpStackSelector(self):
        """
        Deletes the contents of the stack of selector sub-processes
        :return:
        """
        for selector in self.__stack_selector:
            self.__stack_selector[selector].stopSelector()
        self.__stack_selector = {}

    def dumpStackUserInput(self):
        """
        Deletes the contents of the stack of user inputs
        :return:
        """
        self.stack_user_input = []




















