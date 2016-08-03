#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from rally.task import scenario
from rally.plugins.openstack.scenarios.nova import utils as nova_utils
from rally.plugins.openstack.scenarios.neutron import utils as neutron_utils
from rally.plugins.openstack.scenarios.glance import utils as glance_utils
from rally.task import types
from rally.task import validation


class BrowbeatPlugin(neutron_utils.NeutronScenario,
                     glance_utils.GlanceScenario,
                     nova_utils.NovaScenario,
                     scenario.Scenario):
    @types.convert(flavor={"type": "nova_flavor"})
    @validation.flavor_exists("flavor")
    @validation.required_openstack(users=True)
    @scenario.configure(context={"cleanup": ["nova", "neutron", "glance"]})
    def glance_create_boot_delete(self, container_format, image_location, disk_format, flavor,
                                  network_create_args=None, subnet_create_args=None, **kwargs):
        image = self._create_image(container_format, image_location, disk_format, **kwargs)
        image_id = image.id
        net = self._create_network(network_create_args or {})
        self._create_subnet(net, subnet_create_args or {})
        kwargs['nics'] = [{'net-id': net['network']['id']}]
        server = self._boot_server(image_id, flavor, **kwargs)
        self._delete_server(server)
        self._delete_image(image)
