#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2021, Joey Zhang <thinkdoggie@gmail.com> <joey.z@dell.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: virt_cloudimg_vm
author: "Joey Zhang (@thinkdoggie)"
short_description: Provision virtual machines from cloud images via libvirt
description:
  - Create & configure new virtual machines from cloud images.
  - Cloud images can be retrieved and converted properly by this module.
  - Cloud-init user-data and meta-data can be provided as module arguments natively.
  - See 'man 1 virt-install' for more details about the corresponding options. 
options:
  uri:
    type: str
    description:
      - libvirt connection uri.
    default: qemu:///system
  name:
    type: str  
    description:
      - name of the guest VM being provisioned.
    required: true
    aliases:
      - guest
  state:
    type: str
    description:
      - If set to C(present), ensure that the guest is provisioned with desired configuration.
      - If set to C(updated), update the configuration in data source if the guest already exists.
      - If set to C(regenerated), update the configuration and generate a new instance ID if possible.
      - C(regenerated) cannot be set if I(instance_id) is specified.
    choices: [ present, updated, regenerated ]
    default: present
  autostart:
    type: bool  
    description:
      - Start VM at host startup.
    default: false
  recreate:
    type: bool
    description:
      - Use to force the re-creation of an existing guest VM.
    default: false
  virt_type:
    type: str
    description:
      - The hypervisor used to create the VM guest. Example choices are C(kvm), C(qemu), or C(xen).
  virt_opts:
    type: list
    elements: str
    description:
      - The additional virtualization features for specific hypervisors. 
      - The possbile values are C(hvm), C(paravirt) and C(container).
  arch:
    type: str  
    description:
      - Request a non-native CPU architecture for the guest virtual machine.
      - If omitted, the host CPU architecture will be used in the guest.
  machine:
    type: str
    description:
      - The machine type to emulate. This will typically not need to be specified for Xen or KVM, but is useful for choosing machine types of more exotic architectures.
  machine_features:
    type: dict
    description:
      - Turn on or off certain CPU / machine features supported by hypervisors, such as I(acpi), I(pvspinlock), I(kvm.hidden.state), etc.
  qemu_commandline:
    type: str
    description:
      - Pass options directly to the qemu emulator. Only works for the libvirt qemu driver.
  cpu_model:
    type: str
    description:
      - Configure the CPU model exposed to the guest.
      - For C(host-passthrough), the CPU visible to the guest should be exactly the same as the host CPU even in the aspects that libvirt does not understand. 
  cpu_opts:
    type: dict
    description:
      - Configure advanced virtual CPU options, such as C(vendor) or C(cache.mode).
  cpu_features:
    type: dict
    description:
    - Configure fine-tune CPU features exposed to the guest.
    suboptions:
      force:
        type: list
        description:
          - The virtual CPU will claim the feature(s) are supported regardless of it being supported by host CPU.
      require:
        type: list
        description:
          - Guest creation will fail unless the feature(s) are supported by the host CPU or the hypervisor is able to emulate it. 
      optional:
        type: list
        description:
          - The feature(s) will be supported by virtual CPU if and only if it is supported by host CPU.
      disable:
        type: list
        description:
          - The feature(s) will not be supported by virtual CPU.
      forbid:
        type: list
        description:
          - Guest creation will fail if the feature(s) are supported by host CPU.
    cpu_cells:
      type: list
      elements: dict
      description:
        - Configure guest NUMA topology
      suboptions:
        id:
          type: int
          description:
            - NUMA node id
        cpus:
          type: str
          description:
            - Specifies the CPU or range of CPUs that are part of the node.
        memory:
          type: int
          description:
            - Specifies the node memory in MiB.
        distances:
          type: list
          elements: dict
          description:
            - Define the distance between NUMA cells.
          suboptions:
            id:
              type: int
              description:
                - Sibling NUMA node id
            value:
              type: int
              description:
                - Distance value between sibling NUMA cells.
  vcpus:
    type: int
    description:
      - Number of virtual cpus to configure for the guest.
    required: true
  vcpus_opts:
    type: dict
    descriptions:
    - Configure virtual CPU topology and other options, like I(sockets), I(cores) and I(threads).
  memory:
    type: int
    description:
      - Memory to allocate for the guest, in MiB.
    required: true
  memory_opts:
    type: dict
    description:
      - Configure sub memory options, like I(currentMemory), I(maxMemory) and I(maxMemory.slots).
  memorybacking:
    type: dict
    description:
      - Configure options which will influence how virtual memory pages are backed by host pages.
  memballoon:
    type: str
    description:
      - Attach a virtual memory balloon device to the guest.
      - The value can be one of C(virtio), C(xen) or C(none).
  memballoon_opts:
    type: dict
    description:
      - Configure sub options for memory ballon device.
  cputune:
    type: dict
    description:
      - Tune CPU parameters for the guest VM. 
    suboptions:
      vcpupins:
        type: list
        elements: dict
        description:
          - Configure which of the host's physical CPUs the domain vCPU will be pinned to.
        suboptions:
          vcpu:
            type: int
            description:
              - Specifies vCPU id.
          cpuset:
            type: str
            description:
              - Specifies a comma-separated list of physical CPU numbers that vCPUs can be pinned to.
  memtune:
    type: dict
    description:
      - Tune memory policy for the guest VM.
    suboptions:
      hard_limit:
        type: int
        description:
          - The maximum memory for the guest to use, in MiB.
      soft_limit:
        type: int
        description:
          - The memory limit to enforce during memory contention, in MiB.
      swap_hard_limit:
        type: int
        description:
          - The maximum memory plus swap for the guest to use, in MiB.
      min_gurantee:
        type: int
        description:
          - The guaranteed minium memory allocation for the guest, in MiB.
  numatune:
    type: dict 
    description:
      - Tune NUMA policy for the guest VM.
    suboptions:
      nodeset:
        type: str
        description:
          - Specifies the numa nodes to allocate memory from as a comma separated list of numbers.
      mode:
        type: str
        description:
          - The mode of NUMA policy tuning.
        choices: [ interleave, preferred, strict ]
      placement:
        type: str
        description:
          - Indicates the memory placement mode for domain process.
        choices: [ static, auto ]
  blkiotune:
    type: dict
    description:
      - Tune blkio policy for the guest VM.
    suboptions:
      weight:
        type: int
        description:
          - The overall I/O weight of the guest.
          - The value should be in the range [100, 1000]. After kernel 2.6.39, the value could be in the range [10, 1000].
      devices:
        type: list
        elements: dict
        description:
          - Tune the weights for each host block device in use by the guest.
        suboptions:
          path:
            type: path
            description:
              - The absolute path of the block device.
          weight:
            type: int
            description:
              - The relative weight of that device.
  clock_offset:
    type: str
    description:
      - Set the clock offset, e.g. 'utc' or 'localtime'.
  clock_opts:
    type: dict
    description:
      - Configure additional clock options.
  os_variant:
    type: str
    description:
      - Optimize the guest configuration for a specific operating system (e.g. 'fedora29', 'rhel7', 'win10'). 
      - While not required, specifying this options is HIGHLY RECOMMENDED, as it can greatly increase performance by specifying virtio among other guest tweaks.
  uefi:
    type: bool
    description:
      - Enable UEFI support for the guest VM.
  root_disk:
    type: dict
    description:
      - Configure the root disk device for the guest.
    suboptions:
      path:
        type: str
        description:
          - A path of disk file for creating root disk device.
          - One of option I(path) and I(pool) is required explicitly.
      pool:
        type: str
        description:
          - An existing libvirt storage pool name to create new storage on.
          - Only directory or filesystem pools are supported so far.
          - If neither I(path) nor I(pool) options are specified, C(default) pool will be used to create the root disk.
      bus:
        type: str
        description:
          - Disk bus type. The value can be one of C(ide), C(sata), C(scsi), C(usb), C(virtio) or C(xen).
        default: virtio
      size:
        type: int
        description:
          - Size of root disk, in GiB.
          - The root disk size cannot be less than the original image size.
        required: true
      format:
        type: str
        description:
          - Disk image format. The possible values are C(raw), C(qcow2), etc.
          - If not specified, this will default to original format of cloud image in use.
      sparse:
        type: bool
        description:
          - Whether to skip fully allocating newly created storage.
        default: true          
      io:
        type: str
        description:
          - Disk IO backend. Can be either 'threads' or 'native'.
        choices: [ threads, native ]
      cache:
        type: str
        description:
          - The cache mode to be used.
        choices: [ none, writethrough, directsync, unsafe, writeback ]
      discard:
        type: str
        description:
          - Whether discard (also known as 'trim' or 'unmap') requests are ignored or passed to the filesystem.
        choices: [ trim, ignore ]        
      error_policy:
        type: str
        description:
          - How guest should react if a write error is encountered.
        choices: [ stop, ignore, enospace ]
      startup_policy:
        type: str
        description:
          - It defines what to do with the disk if the source file is not accessible.
        choices: [ mandatory, requisite, optional ]
      snapshot_policy:
        type: str
        description:
          - Defines default behavior of the disk during disk snapshots.
        choices: [ internal, external, no ]
    required: true    
  storage_devices:
    type: list
    elements: dict
    description:
      - Configure the optional storage devices for the guest, with various options.
      - One of sub-option I(path), I(pool) and I(vol) is required explicitly.
  network_devices:
    type: list
    elements: dict
    description:
      - Configure network devices connected to the host network.
      - Each network device can be specified by one of the formats as follows: I(bridge=BRIDGE), I(network=NAME), I(type=direct,source=IFACE).
      - If an empty list C([]) is specified, none of network interfaces will be available in the guest.
  graphics:
    type: str
    description:
      - Specifies the graphical display configuration.
      - The possible values are C(vnc), C(spice) or C(none).
  graphics_opts:
    type: dict
    description:
      - Configure sub options for graphical display configuration.
  video:
    type: str
    description:
      - Specify what video device model will be attached to the guest.
      - The possible values are C(cirrus), C(vga), C(qxl), C(virtio), C(ramfb), or C(none).
  video_opts:
    type: dict
    description:
      - Configure sub options for video device.
  sound:
    type: str
    description:
      - Specify what audio device model will be attached to the guest.
      - Possible values are C(ich6), C(ich9), C(ac97), C(es1370), C(sb16), C(pcspk), C(default) or C(none).
  sound_opts:
    type: dict
    description:
      - Configure sub options for audio device.
  serial_devices:
    type: list
    elements: dict
    description:
      - Attach serial devices to the guest, with various options.
      - Sub-option I(type) of each serial device can be one of C(pty), C(dev), C(file), C(pipe), C(tcp), C(udp), or C(unix).
  parallel_devices:
    type: list
    elements: dict
    description:
      - Attach parallel devices to the guest, with various options.
      - Sub-option I(type) of each parallel device can be one of C(pty), C(dev), C(file), C(pipe), C(tcp), C(udp), or C(unix).
  smartcard_devices:
    type: list
    elements: dict
    description:
      - Attach smartcard devices to the guest.
      - Sub-option I(mode) of each smartcard device can be one of C(host), C(host-certificates) or C(passthrough).
  input_devices:
    type: list
    elements: dict
    description:
      - Attach input devices to the guest.
      - Sub-option I(type) of each input device can be one of C(mouse), C(tablet), C(keyboard) or C(passthrough).
  controllers:
    type: list
    elements: dict
    description:
      - Attach a controller device to the guest.
      - Sub-option I(type) of each controller can be one of C(ide), C(fdc), C(scsi), C(sata), C(virtio-serial), C(usb), C(usb2), C(usb3).   
  host_devices:
    type: list
    elements: dict
    description:
      - Attach a physical host device to the guest.
      - Sub-option I(source) is the device identifier of the physical host device to be attached. For a PCI device, the value could be 'pci_0000_00_1b_0' (via virsh nodedev-list) or '1f.01.02' (via lspci). For a USB device, the value could be '001.003' (by bus id) or '0x1234:0x5678' (by vendor, product).
  image_path:
    type: str
    description:
      - File path or URL location of the cloud image to be used.
      - Currently, http, ftp and local fs path are supported.
      - If the option value is a remote location, cloud image file will be downloaded to C(ANSIBLE_REMOTE_TMP), unless I(image_cache_dir) is specified.
    required: true
  image_cache_dir:
    type: path
    description:
      - The directory to save image files downloaded from remote location.
      - If the same image file already exists in the specified I(image_cache_dir) and I(pull=false), there's no need to download it again.
  force_pull:
    type: bool
    description:
      - If true, always pull the latest image payload from remote location. Otherwise, will use the existing file in I(image_cache_dir) as for as possible.
      - This option has no effect if I(image_path) is a local path.
      - This option requires I(image_cache_dir) to be set.
    default: false
  instance_id:
    type: str
    description:
      - ID of the instance as discovered by cloud-init.
      - If omitted, I(instance_id) will be generated automatically.
      - This option cannot work together with I(state=regenerated).
  hostname:
    type: str
    description:
      -  Set the system hostname and fqdn in the guest VM by cloud-init.
  network_config:
    type: dict
    description:
      - Customize the instance's networking interface in either L(Networking Config Version 1,https://cloudinit.readthedocs.io/en/latest/topics/network-config-format-v1.html#network-config-v1) or L(Networking Config Version 2,https://cloudinit.readthedocs.io/en/latest/topics/network-config-format-v2.html#network-config-v2).
  cloud_config:
    type: dict
    description:
      - Provide user-data to the guest VM in cloud-config format.
    aliases:
      - user_data      
  disable_cloudinit:
    type: bool
    description:
      - Disable cloud-init to prevent unexpected changes after first boot.
    default: false
  wait:
    type: bool
    description:
      - Wait for the cloud-init to complete in the guest VM.
    default: false
  wait_timeout:
    type: int
    description:
      - How long before wait gives up, in seconds.
    default: 300
requirements:
    - "python >= 2.6"
    - libvirt-python 
    - virt-install
    - qmeu-img
seealso:
  - name: virt-install Man Page
    description: Ubuntu manpage of virt-install tool.
    link: https://manpages.ubuntu.com/manpages/focal/man1/virt-install.1.html
  - name: cloud-init Documentation
    description: Official documentation of cloud-init project
    link: https://cloudinit.readthedocs.io/en/latest/
author:
    - Joey Zhang (@thinkdoggie)
'''

EXAMPLES = '''
# Use local cloud image to create a new virtual machine
- community.libvirt.virt_cloudimg_vm:
    name: ubuntu-vm
    image_path: /srv/cloudimg/focal-server-cloudimg-amd64.img
    vcpus: 4
    memory: 8
    os_variant: ubuntu20.04
    root_disk:
      pool: default
      size: 50
      format: qcow2
    hostname: ubuntu-vm
    state: present

# Use remote cloud image to create a new virtual machine
- community.libvirt.virt_cloudimg_vm:
    name: webapp-vm
    image_path: https://cloud.centos.org/centos/8-stream/x86_64/images/CentOS-Stream-GenericCloud-8-20210210.0.x86_64.qcow2
    image_cache_dir: /srv/cloudimg
    force_pull: true
    vcpus: 4
    memory: 8
    os_variant: centos8
    root_disk:
      pool: default
      size: 50
      format: qcow2
    hostname: webapp-vm
    state: present

# Create a new virtual machine on bridge network with static IP address
- community.libvirt.virt_cloudimg_vm:
    name: ubuntu-vm
    image_path: /srv/cloudimg/focal-server-cloudimg-amd64.img
    vcpus: 4
    memory: 8
    os_variant: ubuntu20.04
    root_disk:
      pool: default
      size: 50
      format: qcow2
    network_devices:
    - bridge: br0
      model: virtio
    hostname: ubuntu-vm
    network_config:
      version: 2
      ethernets:
        eth0:
          dhcp4: false
          addresses:
          - 192.168.1.15/24
          gateway4: 192.168.1.1
          nameservers:
            addresses: [8.8.8.8, 8.8.4.4]
    state: present

# Create a new virtual machine with additional storage
- community.libvirt.virt_cloudimg_vm:
    name: ubuntu-vm
    image_path: /srv/cloudimg/focal-server-cloudimg-amd64.img
    vcpus: 4
    memory: 8
    os_variant: ubuntu20.04
    root_disk:
      pool: default
      size: 50
      format: qcow2
    storage_devices:
    - path: /var/lib/libvirt/images/ubuntu-vm_data.qcow2
      size: 100
      format: qcow2
      bus: virtio
      cache: none
      io: native
    hostname: ubuntu-vm
    state: present

# Create a new virtual machine with user data in cloud-config format
- community.libvirt.virt_cloudimg_vm:
    name: ubuntu-vm
    image_path: /srv/cloudimg/focal-server-cloudimg-amd64.img
    vcpus: 4
    memory: 8
    os_variant: ubuntu20.04
    root_disk:
      pool: default
      size: 50
      format: qcow2
    hostname: ubuntu-vm
    cloud_config:
      swap:
        filename: /swapfile
        size: 2147483648
    state: present

# Wait for cloud-init to complete and disable it after first boot
- community.libvirt.virt_cloudimg_vm:
    name: ubuntu-vm
    image_path: /srv/cloudimg/focal-server-cloudimg-amd64.img
    vcpus: 4
    memory: 8
    os_variant: ubuntu20.04
    root_disk:
      pool: default
      size: 50
      format: qcow2
    hostname: ubuntu-vm
    cloud_config:
      packages:
        - net-tools
        - build-essential
        - libssl-dev
        - libffi-dev
        - python3-dev
        - python3-pip
        - python3-venv
    disable_cloudinit: true
    wait: true
    state: present

# Update the instance-id and all configuration data. The virtual machine will be restarted if exists.
- community.libvirt.virt_cloudimg_vm:
    name: ubuntu-vm
    image_path: /srv/cloudimg/focal-server-cloudimg-amd64.img
    vcpus: 4
    memory: 8
    os_variant: ubuntu20.04
    root_disk:
      pool: default
      size: 50
      format: qcow2
    instance_id: iid-123456
    hostname: ubuntu-vm
    cloud_config:
      swap:
        filename: /swapfile
        size: 2147483648
      ntp:
        enabled: true
        ntp_client: auto
        pools: [0.pool.ntp.org, 1.pool.ntp.org, 2.pool.ntp.org, 3.pool.ntp.org]
    state: updated
'''

RETURN = '''
vm:
    description: Dictionary of all the VM attributes.
    type: dict
    returned: On success if VM is found or created.
instance_id:
    description: Generated or assigned unique ID used by cloud-init for each guest, typically using UUID of libvirt domain.
    type: str
    sample: "7588F051-E83C-49FC-890B-F54EF2FCC0F7"
    returned: On sucess if VM is found or created.
state:
    description: The lifecycle status of the created VM, among running, paused, shutdown and crashed
    type: str
    sample: "running"
    returned: On success if VM is found or created.
'''

import traceback

try:
    import libvirt
    from libvirt import libvirtError
except ImportError:
    HAS_VIRT = False
else:
    HAS_VIRT = True

import re
import json
import shutil

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible.module_utils.urls import fetch_file


def is_valid_url(target):
    pattern = re.compile(r'^[a-z]+://')
    result = pattern.match(target)

    return result is not None


class QemuImgError(Exception):
    pass


class LibvirtConnection(object):

    def __init__(self, module, uri):
        self.module = module
        conn = libvirt.open(uri)

        if not conn:
            raise Exception("Hypervisor connection failure")

        self.conn = conn


class QemuImgTool(object):

    def __init__(self, module):
        self.module = module
        self.qemu_img_bin = module.get_bin_path('qemu-img', True)

    def get_info(self, disk_file):
        cmd = [self.qemu_img_bin, 'info', '--output=json', disk_file]
        (rc, out, err) = self.module.run_command(cmd)
        if rc != 0:
            raise QemuImgError(err)

        return json.loads(out)

    def resize(self, disk_file, size):
        cmd = [self.qemu_img_bin, 'resize', disk_file, to_native(size)]
        (rc, out, err) = self.module.run_command(cmd)
        if rc != 0:
            raise QemuImgError(err)

    def convert(self, input_file, output_file, fmt='qcow2'):
        cmd = [self.qemu_img_bin, 'convert',
               '-f', fmt, input_file, output_file]
        (rc, out, err) = self.module.run_command(cmd)
        if rc != 0:
            raise QemuImgError(err)


class VirtImageProvision(object):

    def __init__(self, module):
        self.module = module
        self.uri = module.params['uri']
        self.name = module.params['name']
        self.recreate = module.params['recreate']
        self.root_disk = module.params['root_disk']
        self.storage_devices = module.params['storage_devices']
        self.network_devices = module.params['network_devices']
        self.image_path = module.params['image_path']
        self.image_cache_dir = module.params['image_cache_dir']
        self.force_pull = module.params['force_pull']
        self.instance_id = module.params['instance_id']
        self.hostname = module.params['hostname']
        self.network_config = module.params['network_config']
        self.cloud_config = module.params['cloud_config']
        self.disable_cloudinit = module.params['disable_cloudinit']
        self.wait = module.params['wait']
        self.wait_timeout = module.params['wait_timeout']

        self.virt_conn = LibvirtConnection(self.module, self.uri)
        self.virtinst = VirtInstTool(self.module, self.uri, self.name)
        self.qemu_img = QemuImgTool(self.module)

    def vm_exists(self):
        return True

    def prepare_base_image(self):
        return "/path/to/image"

    def make_root_disk(self):
        pass

    def generate_localds(self):
        pass

    def create_instance(self):
        pass


def main():
    module = AnsibleModule(
        argument_spec=dict(
            uri=dict(type='str', default='qemu:///system'),
            name=dict(type='str', aliases=['guest'],
                      required=True),
            state=dict(type='str', default='present',
                       choices=['present', 'updated', 'regenerated']),
            autostart=dict(type='bool', default=False),
            recreate=dict(type='bool', default=False),
            virt_type=dict(type='str'),
            virt_opts=dict(type='list', elements='str',
                           choices=['hvm', 'paravirt', 'container']),
            arch=dict(type='str'),
            machine=dict(type='str'),
            machine_features=dict(type='dict'),
            qemu_commandline=dict(type='str'),
            cpu_model=dict(type='str'),
            cpu_opts=dict(type='dict'),
            cpu_features=dict(
                type='dict',
                options=dict(
                    force=dict(type='list', elements='str'),
                    require=dict(type='list', elements='str'),
                    optional=dict(type='list', elements='str'),
                    disable=dict(type='list', elements='str'),
                    forbid=dict(type='list', elements='str'),
                )
            ),
            cpu_cells=dict(
                type='list',
                elements='dict',
                options=dict(
                    id=dict(type='int'),
                    cpus=dict(type='str'),
                    memory=dict(type='int'),
                    distances=dict(
                        type='list',
                        elements='dict',
                        options=dict(
                            id=dict(type='int', required=True),
                            value=dict(type='int', required=True),
                        )
                    )
                )
            ),
            vcpus=dict(type='int', required=True),
            vcpus_opts=dict(type='dict'),
            memory=dict(type='int', required=True),
            memory_opts=dict(type='dict'),
            memorybacking=dict(type='dict'),
            memballoon=dict(type='str'),
            memballoon_opts=dict(type='dict'),
            cputune=dict(
                type='dict',
                options=dict(
                    vcpupins=dict(
                        type='list',
                        elements='dict',
                        options=dict(
                            vcpu=dict(type='int', required=True),
                            cpuset=dict(type='str', required=True),
                        )
                    ),
                )
            ),
            memtune=dict(
                type='dict',
                options=dict(
                    hard_limit=dict(type='int'),
                    soft_limit=dict(type='int'),
                    swap_hard_limit=dict(type='int'),
                    min_gurantee=dict(type='int'),
                )
            ),
            numatune=dict(
                type='dict',
                options=dict(
                    nodeset=dict(type='str'),
                    mode=dict(type='str',
                              choices=['interleave', 'preferred', 'strict']),
                    placement=dict(type='str',
                                   choices=['static', 'auto']),
                )
            ),
            blkiotune=dict(
                type='dict',
                options=dict(
                    weight=dict(type='int'),
                    devices=dict(
                        type='list',
                        options=dict(
                            path=dict(type='path', required=True),
                            weight=dict(type='int', required=True),
                        )
                    ),
                )
            ),
            clock_offset=dict(type='str'),
            clock_opts=dict(type='dict'),
            os_variant=dict(type='str'),
            uefi=dict(type='bool'),
            root_disk=dict(
                type='dict',
                options=dict(
                    path=dict(type='path'),
                    pool=dict(type='str'),
                    bus=dict(type='str', default='virtio'),
                    size=dict(type='int', required=True),
                    format=dict(type='str'),
                    sparse=dict(type='bool', default=True),
                    io=dict(type='str',
                            choices=['threads', 'native']),
                    cache=dict(type='str',
                               choices=['none', 'writethrough', 'directsync', 'unsafe', 'writeback']),
                    discard=dict(type='str',
                                 choices=['trim', 'ignore']),
                    error_policy=dict(type='str',
                                      choices=['stop', 'ignore', 'enospace']),
                    startup_policy=dict(type='str',
                                        choices=['mandatory', 'requisite', 'optional']),
                    snapshot_policy=dict(type='str',
                                         choices=['internal', 'external', 'no']),
                ),
                required=True,
                mutually_exclusive=[
                    ('path', 'pool'),
                ],
                required_one_of=[
                    ('path', 'pool'),
                ],
            ),
            storage_devices=dict(type='list', elements='dict'),
            network_devices=dict(type='list', elements='dict'),
            video=dict(type='str'),
            video_opts=dict(type='dict'),
            sound=dict(type='str'),
            sound_opts=dict(type='dict'),
            serial_devices=dict(type='list', elements='dict'),
            parallel_devices=dict(type='list', elements='dict'),
            smartcard_devices=dict(type='list', elements='dict'),
            input_devices=dict(type='list', elements='dict'),
            controllers=dict(type='list', elements='dict'),
            host_devices=dict(type='list', elements='dict'),
            image_path=dict(type='str', required=True),
            image_cache_dir=dict(type='path'),
            force_pull=dict(type='bool', default=False),
            instance_id=dict(type='str'),
            hostname=dict(type='str'),
            network_config=dict(type='dict'),
            cloud_config=dict(type='dict'),
            disable_cloudinit=dict(type='bool', default=False),
            wait=dict(type='bool', default=False),
            wait_timeout=dict(typ='int', default=300),
        ),
        supports_check_mode=True,
        required_by=dict(
            cpu_opts=('cpu_model',),
            cpu_features=('cpu_model',),
            cpu_cells=('cpu_model',),
            vcpus_opts=('vcpus',),
            memory_opts=('memory',),
            memballoon_opts=('memballoon',),
            numatune_opts=('numatune',),
            blkiotune_opts=('blkiotune',),
            graphics_opts=('graphics',),
            video_opts=('video',),
            sound_opts=('sound',),
            force_pull=('image_cache_dir',),
        )
    )

    if not HAS_VIRT:
        module.fail_json(
            msg="The `libvirt` module is not importable. Check the requirements.")

    virtimgctl = VirtImageProvision(module)
    result = dict()

    state = module.params['state']

    try:
        if virtimgctl.vm_exists():
            instance_id = ''

            if state == 'regenerated' and \
                    virtimgctl.instance_id:
                module.fail_json(
                    msg="instance_id cannot be set when state=regenerated")

            if state == 'present':
                result['changed'] = False
            else:
                pass
        else:
            # If VM does not exist, state=present/updated/regenerated has no diference
            virtimgctl

        # TODO: Get VM state

    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())

    module.exit_json(**result)


if __name__ == '__main__':
    main()
