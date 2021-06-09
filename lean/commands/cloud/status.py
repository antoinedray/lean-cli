# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean CLI v1.0. Copyright 2021 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import click

from lean.click import LeanCommand
from lean.container import container
from lean.models.api import QCLiveAlgorithmStatus
from lean.models.brokerages import all_brokerages


@click.command(cls=LeanCommand)
@click.argument("project", type=str)
def status(project: str) -> None:
    """Show the live trading status of a project in the cloud.

    PROJECT must be the name or the id of the project to show the status for.
    """
    logger = container.logger()
    api_client = container.api_client()

    cloud_project_manager = container.cloud_project_manager()
    cloud_project = cloud_project_manager.get_cloud_project(project, False)

    live_algorithm = next((d for d in api_client.live.get_all() if d.projectId == cloud_project.projectId), None)

    logger.info(f"Project id: {cloud_project.projectId}")
    logger.info(f"Project name: {cloud_project.name}")

    if live_algorithm is None:
        logger.info("Live status: not deployed")
        return

    live_status = {
        QCLiveAlgorithmStatus.DeployError: "Deploy error",
        QCLiveAlgorithmStatus.InQueue: "In queue",
        QCLiveAlgorithmStatus.RuntimeError: "Runtime error",
        QCLiveAlgorithmStatus.LoggingIn: "Logging in"
    }.get(live_algorithm.status, live_algorithm.status.value)

    brokerage_name = next((b.name for b in all_brokerages if b.id == live_algorithm.brokerage),
                          live_algorithm.brokerage)

    if brokerage_name == "PaperBrokerage":
        brokerage_name = "Paper Trading"

    logger.info(f"Live status: {live_status}")
    logger.info(f"Deployment id: {live_algorithm.deployId}")
    logger.info(f"Brokerage: {brokerage_name}")
    logger.info(f"Launched: {live_algorithm.launched.strftime('%Y-%m-%d %H:%M:%S')} UTC")

    if live_algorithm.stopped is not None:
        logger.info(f"Stopped: {live_algorithm.stopped.strftime('%Y-%m-%d %H:%M:%S')} UTC")

    if live_algorithm.error != "":
        logger.info("Error:")
        logger.info(live_algorithm.error)