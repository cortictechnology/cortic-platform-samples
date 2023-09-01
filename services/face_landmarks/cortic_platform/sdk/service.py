""" 
COPYRIGHT_NOTICE:
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2023
COPYRIGHT_NOTICE
"""
from abc import abstractmethod
from enum import Enum
from cortic_platform.sdk.service_data_types import *

class ServiceStatus(Enum):
    Deactivated = 0
    Activated = 1
    Idle = 2
    Processing = 3
    FailedToStart = 4

class ServiceContext:
    """
    The ServiceContext class provides a set of methods that can be used by a Service to
    manage its states. The ServiceContext class is automatically instantiated when a
    Service object is created. The ServiceContext object is passed to the Service object

        1. get_state: Retrieves the value of a state.
        2. set_state: Sets the value of a state.
        3. reset_states: Resets all states to their default values.
        4. clear_states: Clears the entire state dictionary. Developers need to calle the create_state() method
                            to create new states after calling this method.

    A state is a variable that can be used by a Service to store information that is
    required by the Service to perform its task. For example, a Service may need to
    store the number of times it has processed data. In this case, the Service can
    create a state called "count" and increment its value each time it processes data.
    """

    def __init__(self):
        self.states = {}
        self._default_states = {}
        self.service = None
        self._dm_connection = None

    def create_state(self, state_name, default_state_value):
        """
        Creates a state with a default value. If the state already exists, the default value
        is ignored and the existing value is used instead. If developers need to create more
        than one states, they should call this method multiple times. There is no method to
        create a batch of states as developers are expected to create states only when they
        are needed. This is to ensure that the state dictionary is not bloated with states
        that are not used.

        :param state_name: The name of the state.
        :type state_name: str

        :param state_value: The value of the state.
        :type state_value: object

        """
        self._default_states[state_name] = default_state_value

    def get_state(self, state_name):
        """
        Retrieves the value of a state. If the state does not exist, None is returned.

        :param state_name: The name of the state.
        :type state_name: str

        :return: A dictionary containing the state name and value.

        """
        if state_name not in self._default_states:
            return None
        key = self.service._current_task_source_hub + "_" + self.service._current_task_source_app + "_" + self.service._current_task_source_pipeline + "_" + state_name
        if self.service.config is not None:
            if self.service.config["is_data_source"]:
                key = "___" + state_name
        if key not in self.states:
            self.states[key] = self._default_states[state_name]
        return {state_name: self.states[key]}

    def set_state(self, state_name, state_value):
        """
        Sets the value of a state. If the state does not exist, an error code is returned.

        :param state_name: The name of the state.
        :type state_name: str

        :param state_value: The value of the state.
        :type state_value: object

        :return: A code indicating the result of the operation. 0 indicates success. A negative
                    value indicates failure.

        """
        self._set_state(self.service._current_task_source_hub, self.service._current_task_source_app, self.service._current_task_source_pipeline, state_name, state_value, from_self=True)

    def _set_state(self, hub_name, app_name, pipeline_name, state_name, state_value, from_self=False):
        if state_name not in self._default_states:
            return -15
        key = hub_name + "_" + app_name + "_" + pipeline_name + "_" + state_name
        if self.service.config is not None:
            if self.service.config["is_data_source"]:
                key = "___" + state_name
        if key not in self.states:
            self.states[key] = self._default_states[state_name]
        self.states[key] = state_value
        if from_self:
            if self._dm_connection is not None:
                self._dm_connection.send({"service_states": {"key": key, "value": state_value}})
        return 0
    
    def reset_states(self):
        """
        Resets all states to their default values.

        """
        self._reset_states(self.service._current_task_source_hub, self.service._current_task_source_app, self.service._current_task_source_pipeline)

    def _reset_states(self, hub_name, app_name, pipeline_name):
        target_key = hub_name + "_" + app_name + "_" + pipeline_name
        if self.service.config is not None:
            if self.service.config["is_data_source"]:
                target_key = "___" 
        for key in list(self.states.keys()):
            if target_key in key:
                del self.states[key]

    def clear_states(self):
        """
        Clears the entire state dictionary. Developers need to calle the create_state() method
        to create new states after calling this method.

        """
        self.states = {}
        self._default_states = {}
    
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
        self.status = ServiceStatus.Deactivated
        self.context = ServiceContext()
        self.context.service = self
        self.input_type = {}
        self.output_type = {}

        self._current_task_source_hub = ""
        self._current_task_source_app = ""
        self._current_task_source_pipeline = ""

    @abstractmethod
    def activate(self):
        """
        Abstract Method.
        Allocates and acquires any resources required by this service.  This method is executed
        when an App or another Service requires the output of this Service. Developers should
        implement this method to acquire any resources that are required by the process() method.
        The resources acquired in this method should be released in the deactivate() method. For
        example, if the process() method requires a neural network model, the activate() method
        should load the model from disk and store it in a variable. The deactivate() method should
        release the model by deleting the variable. This ensures that the model is loaded only when
        it is required and is released when it is no longer needed.

        Another thing developers should do in this method is to setup the context of this service.
        The context is a dictionary that can be used to store state information that is required by the
        service to perform its task. For example, a service may need to store the number of times
        it has processed data. In this case, the service can create a state called "count" and
        increment its value each time it processes data. However, the context is reset each time
        the service is deactivated and activated again. Therefore, if the service needs to maintain
        a state, it should create the state in the init() method instead.

        :raises: NotImplementedError: If this method is not implemented.

        """
        return NotImplementedError

    @abstractmethod
    def process(self, input_data=None):
        """
        Abstract Method.
        Processes the input data and produces an output. This method is executed when new data
        arrives from an App or another Service. There isn't a fixed number of calls per second
        for this method. The number of calls per second depends on the rate at which data is
        produced by the App or Service that is connected to this Service. Developers should
        implement this method to process the input data and produce an output. The output of
        this method is returned to the App or Service that is connected to this Service. It is
        not recommended to perform any resource allocation in this method. All resources should
        be allocated in the activate() method. This method should only contain the data processing
        logic.

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
        the activate() method. This method is executed when an App or another Service no longer
        requires the output of this Service. Developers should implement this method to release
        any resources that are no longer required.

        :raises: NotImplementedError: If this method is not implemented.

        """
        return NotImplementedError
