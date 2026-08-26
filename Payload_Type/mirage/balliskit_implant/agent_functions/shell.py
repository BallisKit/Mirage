from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from mythic_container.MythicGoRPC import *
import base64

class ShellArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(name="command", display_name="Command", type=ParameterType.String,
                             description="Command to run"),
        ]

    async def parse_arguments(self):
        print(self.command_line)
        if len(self.command_line) == 0:
            raise ValueError("Must supply a command to run")

        try:
            json_command = json.loads(self.command_line)
            if type(json_command) is list:
                self.add_arg("command", base64.b64encode(" ".join(f'"{sh_item}"' for sh_item in json_command).encode()).decode())
            else:
                raise ValueError("Command is in an unknow format for the container, please contact us")
        except:
            self.add_arg("command", base64.b64encode(self.command_line.encode()).decode())

    async def parse_dictionary(self, dictionary_arguments):
        self.add_arg("command", base64.b64encode(dictionary_arguments['command'].encode()).decode())


class ShellCommand(CommandBase):
    cmd = "shell"
    needs_admin = False
    help_cmd = "shell {command}"
    description = """The command will be executed via NSTask and the output returned."""
    version = 1
    author = "Balliskit Team"
    attackmapping = []
    argument_class = ShellArguments
    attributes = CommandAttributes(
        suggested_command=True
    )

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID, ArtifactMessage="{}".format(taskData.args.get_arg("command")),
            BaseArtifactType="Process Create"
        ))

        response.DisplayParams = base64.b64decode(taskData.args.get_arg("command").encode()).decode()
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
