#!/usr/bin/env python

"""
A Rocket fetches a FireWork from the database, runs the sequence of FireTasks inside, and then completes the Launch
"""
import os
import traceback
import threading
from fireworks.core.firework import FWAction
from fireworks.core.fw_config import FWConfig

__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'Feb 7, 2013'


def ping_launch(launchpad, launch_id, stop_event, master_thread, lp_lock):
    while not stop_event.is_set() and master_thread.isAlive():
        # add mutex to ensure thread safety
        lp_lock.acquire()
        launchpad.ping_launch(launch_id)
        lp_lock.release()
        stop_event.wait(FWConfig().PING_TIME_SECS)


class Rocket():
    """
    The Rocket fetches a workflow step from the FireWorks database and executes it.
    """

    def __init__(self, launchpad, fworker, fw_id):
        """
        
        :param launchpad: A LaunchPad object for interacting with the FW database
        :param fworker: A FWorker object describing the computing resource
        :param fw_id: id of a specific FireWork to run (quit if it cannot be found)
        """
        self.launchpad = launchpad
        self.fworker = fworker
        self.fw_id = fw_id
        self.lp_lock = threading.Lock()


    def run(self):
        """
        Run the rocket (check out a job from the database and execute it)
        """
        all_stored_data = {}  # stored data for *all* the Tasks

        lp = self.launchpad
        launch_dir = os.path.abspath(os.getcwd())

        # check a FW job out of the launchpad
        self.lp_lock.acquire()
        m_fw, launch_id = lp.checkout_fw(self.fworker, launch_dir, self.fw_id)
        self.lp_lock.release()
        fw_conf = FWConfig()
        if fw_conf.MULTIPROCESSING:
            fw_conf.PROCESS_LOCK.release()
        if not m_fw:
            raise ValueError("No FireWorks are ready to run and match query! {}".format(self.fworker.query))

        if '_launch_dir' in m_fw.spec:
            prev_dir = launch_dir
            os.chdir(m_fw.spec['_launch_dir'])
            launch_dir = os.path.abspath(os.getcwd())
            lp._change_launch_dir(launch_id, launch_dir)

            if not os.listdir(prev_dir) and FWConfig().REMOVE_USELESS_DIRS:
                try:
                    os.rmdir(prev_dir)
                except:
                    pass

        # write FW.json and/or FW.yaml to the directory
        if FWConfig().PRINT_FW_JSON:
            m_fw.to_file('FW.json', indent=4)
        if FWConfig().PRINT_FW_YAML:
            m_fw.to_file('FW.yaml')

        # set up heartbeat (pinging the server that we're still alive)
        try:
            ping_stop = threading.Event()
            ping_thread = threading.Thread(target=ping_launch,
                                           args=(lp, launch_id, ping_stop, threading.currentThread(), self.lp_lock))
            ping_thread.start()

            # execute the FireTasks!
            for my_task in m_fw.tasks:
                m_action = my_task.run_task(m_fw.spec)

                # read in a FWAction from a file, in case the task is not Python and cannot return it explicitly
                if os.path.exists('FWAction.json'):
                    m_action = FWAction.from_file('FWAction.json')
                elif os.path.exists('FWAction.yaml'):
                    m_action = FWAction.from_file('FWAction.yaml')

                if not m_action:
                    m_action = FWAction()

                # update the global stored data with the data to store from this particular Task
                all_stored_data.update(m_action.stored_data)

                if m_action.skip_remaining_tasks:
                    break;

            # perform finishing operation
            ping_stop.set()
            m_action.stored_data = all_stored_data
            self.lp_lock.acquire()
            lp.complete_launch(launch_id, m_action, 'COMPLETED')
            self.lp_lock.release()

        except:
            ping_stop.set()
            traceback.print_exc()
            m_action = FWAction(stored_data={'_message': 'runtime error during task', '_task': my_task.to_dict(),
                                             '_exception': traceback.format_exc()}, exit=True)
            self.lp_lock.acquire()
            lp.complete_launch(launch_id, m_action, 'FIZZLED')
            self.lp_lock.release()
