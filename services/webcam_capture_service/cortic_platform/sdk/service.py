""" 
COPYRIGHT_NOTICE:
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2022-2023
COPYRIGHT_NOTICE

This module provides a base class for creating various types of services that 
can be used in a Cortic AIoT (Artificial Intelligence of Things) App.

"""

from abc import abstractmethod

class Context:
    def __init__(self, service):
        self.service = service
        self.states = {}

    def get_state(self, state_name):
        key = self.service._current_task_source_hub + "_" + self.service._current_task_source_app + self.service.current_task_source_pipeline + "_" + state_name
        if key not in self.states:
            return None
        return self.states[key]
    
    def set_states(self, hub_name, app_name, pipeline_name, states: dict):
        for state_name, state_value in states.items():
            key = hub_name + "_" + app_name + "_" + pipeline_name + "_" + state_name
            self.states[key] = state_value

class Service:
    """
    The Service class is a versatile foundation for developers to build custom services that can be
    used in a Cortic AIoT (Artificial Intelligence of Things) App. To create a service, developers should
    implement the following methods, which represent key stages in the service lifecycle:

        1. activate: In this stage, the service should gather all required resources.
        2. process: This method contains the data processing logic for the service and is executed when new data arrives from an App or another Service.
        3. deactivate: During this stage, the service should release all previously acquired resources.

    A service is activated only when an App or another Service requires its output. It will be
    automatically deactivated once its output is no longer needed. By releasing resources during
    the deactivation process, the system ensures that resources are always available to the services
    that genuinely need them.
    """

    def __init__(self):
        """Initializes a service"""
        self.activated = False
        self.context = Context(self)
        self.input_type = {}
        self.output_type = {}

        self._current_task_source_hub = ""
        self._current_task_source_app = ""
        self._current_task_source_pipeline = ""

    @abstractmethod
    def activate(self):
        """
        Abstract Method.
        Allocates and acquires any resources required by this service.

        :raises: NotImplementedError: If this method is not implemented.

        """
        return NotImplementedError

    @abstractmethod
    def process(self, input_data=None):
        """
        Abstract Method.
        Processes the input data and produces an output.

        :param input_data: Contains the data that needs to be processed by this Service.
                            The data are provided as <key>-<value> pairs, in which the <key>
                            is the name of the data, and <value> is the value of this data.
        :type input_data: dict

        :return: The output of this Service.
        :rtype: dict

        :raises: NotImplementedError: If this method is not implemented.

        """
        return NotImplementedError

    @abstractmethod
    def deactivate(self):
        """
        Abstract Method.
        Releases any resources being allocated and obtained by this Service in
        the activate() method.

        :raises: NotImplementedError: If this method is not implemented.

        """
        return NotImplementedError
