from interface import agent_response


class Module:
    def __init__(self, agent, name: str = ''):
        self.agent = agent
        self.name = name

    def activate(self, input_text: str) -> bool:
        """
        Perform some action with the agent based on input text.

        :param input_text: a string containing the specific instructions for the module.
        :return: if input_text is valid, return True, otherwise return False
        """
        pass


class TerminationModule(Module):
    def __init__(self, agent, name: str = ''):
        super().__init__(agent=agent, name=name)

    def activate(self, input_text: str) -> bool:
        if "goodbye" in input_text or "ok bye" in input_text or "stop" in input_text:
            self.agent.speak(agent_response.ON_EXIT)
            self.agent.exit()
            return True
        else:
            return False
