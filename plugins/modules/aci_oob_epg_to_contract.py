#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: aci_oob_epg_to_contract
short_description: Manage out-of-band contract association with an out-of-band management EPG in the mgmt tenant.
description:
- This module manages the contract association (mgmtRsOoBProv) under an out-of-band management EPG (mgmtOoB) within the Cisco ACI mgmt tenant.
options:
  epg:
    description:
    - The name of the out-of-band management EPG (under mgmtp-default) where the contract will be associated.
    type: str
    required: true
  contract:
    description:
    - The name of the out-of-band contract to be provided by the management EPG.
    type: str
    required: true
  state:
    description:
    - Use C(present) to associate the contract, or C(absent) to remove the association (not the entire EPG).
    choices: [ absent, present ]
    default: present
    type: str

author:
- Your Name (@yourhandle)
'''

EXAMPLES = r'''
- name: Associate contract to an out-of-band EPG
  aci_mgmt_oob_prov_contract:
    epg: "oob-testoob"
    contract: "oob-test-ct"
    state: present
  delegate_to: localhost

- name: Remove contract association from an out-of-band EPG
  aci_mgmt_oob_prov_contract:
    epg: "oob-testoob"
    contract: "oob-test-ct"
    state: absent
  delegate_to: localhost
'''

RETURN = r'''
changed:
  description: Whether the configuration was changed.
  type: bool
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.aci.plugins.module_utils.aci import ACIModule, aci_argument_spec, aci_annotation_spec


def main():
    argument_spec = aci_argument_spec()
    argument_spec.update(aci_annotation_spec())
    argument_spec.update(
        epg=dict(type='str', required=True),
        contract=dict(type='str'),
        state=dict(type="str", default="present", choices=["absent", "present", "query"]),
    )

    # Ensure epg is required when the state is either present or absent
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["state", "absent", ["epg", "contract"]],
            ["state", "present", ["epg", "contract"]],
        ],
    )

    # Get parameters
    epg = module.params['epg']
    contract = module.params['contract']
    state = module.params['state']

    # Initialize the ACIModule
    aci = ACIModule(module)
    ctProv_mo = "uni/tn-mgmt/oobbrc-{0}".format(contract)

    # Construct the URL path for the out-of-band management EPG and contract
    aci.construct_url(
        root_class=dict(
            aci_class="fvTenant",
            aci_rn="tn-mgmt",
            module_object="mgmt",
            target_filter={"name": "mgmt"},
        ),
        subclass_1=dict(
            aci_class="mgmtMgmtP",
            aci_rn="mgmtp-default",
            module_object="mgmtp-default",
        ),
        subclass_2=dict(
            aci_class="mgmtOoB",
            aci_rn=f"oob-{epg}",
            module_object=epg,
            target_filter={"dn": "uni/tn-mgmt/mgmtp-default/oob-{0}".format(epg)},
        ),
        subclass_3=dict(
            aci_class="mgmtRsOoBProv",
            aci_rn="rsooBProv-{0}".format(contract),
            module_object=contract,
            target_filter={"tDn": ctProv_mo},
        ),
    )
    # Get the existing configuration
    aci.get_existing()

    if state == "present":
        # Build payload and check for differences
        aci.payload(
            aci_class="mgmtRsOoBProv",
            class_config=dict(tnVzOOBBrCPName=contract)
        )
        aci.get_diff(aci_class="mgmtRsOoBProv")

        # Apply changes if necessary
        aci.post_config()

    elif state == "absent":
        aci.delete_config()

    # Exit and return changes
    aci.exit_json()

if __name__ == "__main__":
    main()