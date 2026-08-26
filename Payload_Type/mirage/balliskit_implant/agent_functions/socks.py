from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


class SocksArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="action",
                type=ParameterType.ChooseOne,
                choices=["start", "stop"],
                description="Start or stop the SOCKS5 proxy",
            ),
            CommandParameter(
                name="port",
                type=ParameterType.Number,
                description="Port to use for SOCKS5 proxy (7000-7010)",
                default_value=7001,
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            self.load_args_from_json_string(self.command_line)


class SocksCommand(CommandBase):
    cmd = "socks"
    needs_admin = False
    help_cmd = 'socks {"action": "start", "port": 7001}'
    description = "Start or stop a SOCKS5 proxy through this callback"
    version = 1
    author = "Balliskit Team"
    argument_class = SocksArguments
    attackmapping = []
    supported_ui_features = ["proxy_management"]
    attributes = CommandAttributes(
        suggested_command=True
    )

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )

        action = taskData.args.get_arg("action")
        port = int(taskData.args.get_arg("port"))

        if action == "start":
            socks_resp = await SendMythicRPCProxyStartCommand(MythicRPCProxyStartMessage(
                TaskID=taskData.Task.ID,
                LocalPort=port,
                RemotePort=0,
                RemoteIP="0.0.0.0",
                PortType=CALLBACK_PORT_TYPE_SOCKS,
            ))
            if not socks_resp.Success:
                response.Success = False
                response.Error = socks_resp.Error
                return response

        elif action == "stop":
            socks_resp = await SendMythicRPCProxyStopCommand(MythicRPCProxyStopMessage(
                TaskID=taskData.Task.ID,
                LocalPort=port,
                PortType=CALLBACK_PORT_TYPE_SOCKS,
            ))
            if not socks_resp.Success:
                response.Success = False
                response.Error = socks_resp.Error
                return response

        response.DisplayParams = f"action={action} port={port}"
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp