from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import base64


class RunShellcodeArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="file",
                type=ParameterType.File,
                description="The Shellcode file to execute",
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=True,
                        group_name="Default"
                    )
                ]
            ),
            CommandParameter(
                name="additionnal",
                type=ParameterType.String,
                description="Additional Parameters",
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=False,
                        group_name="Default"
                    )
                ]
            ),
            CommandParameter(
                name="fork",
                type=ParameterType.Boolean,
                description="Shellcode is forked",
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=False,
                        group_name="Default"
                    )
                ]
            )
        ]

    async def parse_arguments(self):
        try:
            received_args = json.loads(self.command_line)
            if type(received_args) is list:
                constructed_params = {}
                for i, submitted_arg in enumerate(received_args):
                    if i < len(self.args):
                        constructed_params[self.args[i].name] = submitted_arg

                self.load_args_from_json_string(json.dumps(constructed_params))
            else:
                self.load_args_from_json_string(self.command_line)
        except (ValueError, TypeError):
            raise ValueError("Expected JSON format for arguments")

class RunShellcodeCommand(CommandBase):
    cmd = "runshellcode"
    needs_admin = False
    help_cmd = "runshellcode"
    description = "Execute a shellcode"
    version = 1
    author = "Balliskit Team"
    attackmapping = []
    attributes = CommandAttributes(
        suggested_command=True
    )

    argument_class = RunShellcodeArguments

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True
        )

        file_uuid = taskData.args.get_arg("file")
        try:
            file_content = await SendMythicRPCFileGetContent(MythicRPCFileGetContentMessage(AgentFileId=file_uuid))
            if file_content.Success:
                base64_content = base64.b64encode(file_content.Content).decode('utf-8')
                taskData.args.remove_arg("file")
                taskData.args.add_arg("content", base64_content)
                filesearch = await SendMythicRPCFileSearch(MythicRPCFileGetContentMessage(AgentFileId=file_uuid))
                response.DisplayParams = f"with filename: {filesearch.Files[0].Filename}"

            else:
                response.Success = False
                response.Error = "Failed to get file content"
                return response

        except Exception as e:
            print(f"Error getting file info: {e}")
            response.Success = False
            response.Error = f"Error: {str(e)}"
            return response

        return response


