from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from mythic_container.MythicGoRPC import *


class IntervalArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(name="interval_number", display_name="Interval number", type=ParameterType.String,
                             description="Interval between the implant's callbacks"),
            CommandParameter(name="jitter_number", display_name="Jitter number", type=ParameterType.String,
                             description="Interval between the implant's callbacks"),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply an interval to run")
        self.add_arg("command", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        if type(dictionary_arguments) is list:
            constructed_params = {}
            for i, submitted_arg in enumerate(dictionary_arguments):
                if i < len(self.args):
                    constructed_params[self.args[i].name] = submitted_arg

            self.load_args_from_json_string(json.dumps(constructed_params))
        else:
            self.load_args_from_dictionary(dictionary_arguments)


class IntervalCommand(CommandBase):
    cmd = "interval"
    needs_admin = False
    help_cmd = "interval <number> <jitter>"
    description = """Allows you to change the time interval between the implant's callbacks"""
    version = 1
    author = "Balliskit Team"
    attackmapping = []
    argument_class = IntervalArguments
    attributes = CommandAttributes(
        suggested_command=True
    )

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID, ArtifactMessage="{}".format(taskData.args.get_arg("interval_number")),
            BaseArtifactType="Process Create"
        ))

        response.DisplayParams = taskData.args.get_arg("interval_number")
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
