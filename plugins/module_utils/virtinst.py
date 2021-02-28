# (c) 2021, Joey Zhang <thinkdoggie@gmail.com> <joey.z@dell.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils._text import to_native


class VirtInstError(Exception):
    pass


def to_kv_pairs(data):
    pairs = ['='.join([k, to_native(v)]) for k, v in data.items()]
    return pairs


def to_kv_param(data):
    return ','.join(to_kv_pairs(data))


def to_mixed_param(prefix, data):
    sub_params = [to_native(prefix)]
    if data:
        sub_params.extend(to_kv_pairs(data))
    return ','.join(sub_params)


class VirtInstTool(object):

    def __init__(self, module, uri, name, **kwargs):
        self.module = module
        self.uri = uri
        self.name = name
        self.autostart = kwargs.get('autostart', module.params['autostart'])
        self.virt_type = kwargs.get('virt_type', module.params['virt_type'])
        self.virt_opts = kwargs.get('virt_opts', module.params['virt_opts'])
        self.arch = kwargs.get('arch', module.params['arch'])
        self.machine = kwargs.get('machine', module.params['machine'])
        self.machine_features = kwargs.get(
            'machine_features', module.params['machine_features'])
        self.qemu_commandline = kwargs.get(
            'qemu_commandline', module.params['qemu_commandline'])
        self.cpu_model = kwargs.get('cpu_model', module.params['cpu_model'])
        self.cpu_opts = kwargs.get('cpu_opts', module.params['cpu_opts'])
        self.cpu_features = kwargs.get(
            'cpu_features', module.params['cpu_features'])
        self.cpu_cells = kwargs.get('cpu_cells', module.params['cpu_cells'])
        self.vcpus = kwargs.get('vcpus', module.params['vcpus'])
        self.vcpus_opts = kwargs.get('vcpus_opts', module.params['vcpus_opts'])
        self.memory = kwargs.get('memory', module.params['memory'])
        self.memory_opts = kwargs.get(
            'memory_opts', module.params['memory_opts'])
        self.memorybacking = kwargs.get(
            'memorybacking', module.params['memorybacking'])
        self.memballoon = kwargs.get('memballoon', module.params['memballoon'])
        self.memballoon_opts = kwargs.get(
            'memballoon_opts', module.params['memballoon_opts'])
        self.cputune = kwargs.get('cputune', module.params['cputune'])
        self.memtune = kwargs.get('memtune', module.params['memtune'])
        self.numatune = kwargs.get('numatune', module.params['numatune'])
        self.blkiotune = kwargs.get('blkiotune', module.params['blkiotune'])
        self.clock_offset = kwargs.get(
            'clock_offset', module.params['clock_offset'])
        self.clock_opts = kwargs.get('clock_opts', module.params['clock_opts'])
        self.os_variant = kwargs.get('os_variant', module.params['os_variant'])
        self.uefi = kwargs.get('uefi', module.params['os_variant'])
        self.storage_devices = kwargs.get(
            'storage_devices', module.params['storage_devices'])
        self.network_devices = kwargs.get(
            'network_devices', module.params['network_devices'])
        self.graphics = kwargs.get('graphics', module.params['graphics'])
        self.graphics_opts = kwargs.get(
            'graphics_opts', module.params['graphics_opts'])
        self.video = kwargs.get('video', module.params['video'])
        self.video_opts = kwargs.get('video_opts', module.params['video_opts'])
        self.sound = kwargs.get('sound', module.params['sound'])
        self.sound_opts = kwargs.get('sound_opts', module.params['sound_opts'])
        self.serial_devices = kwargs.get(
            'serial_devices', module.params['serial_devices'])
        self.parallel_devices = kwargs.get(
            'parallel_devices', module.params['parallel_devices'])
        self.smartcard_devices = kwargs.get(
            'smartcard_devices', module.params['smartcard_devices'])
        self.input_devices = kwargs.get(
            'input_devices', module.params['input_devices'])
        self.controllers = kwargs.get(
            'controllers', module.params['controllers'])
        self.host_devices = kwargs.get(
            'host_devices', module.params['host_devices'])

        self.virtinst_bin = module.get_bin_path('virt-install', True)

    def _add_virt_args(self, args):
        if self.virt_type is not None:
            args.extend(['--virt-type', self.virt_type])

        if self.virt_opts is not None:
            if 'hvm' in self.virt_opts:
                args.append('--hvm')
            if 'paravirt' in self.virt_opts:
                args.append('--paravirt')
            if 'container' in self.virt_opts:
                args.append('--container')

        if self.qemu_commandline is not None:
            args.extend(['--qemu-commandline', self.qemu_commandline])

    def _add_general_args(self, args):
        if self.arch is not None:
            args.extend(['--arch', self.arch])

        if self.machine is not None:
            args.extend(['--machine', self.machine])

        if self.machine_features is not None:
            args.extend(['--features', to_kv_param(self.machine_features)])

        if self.os_variant is not None:
            args.extend(['--os-variant', self.os_variant])

        if self.clock_offset or self.clock_opts:
            args.append('--clock')
            sub_params = []

            if self.clock_offset:
                sub_params.append("offset={}".format(self.clock_offset))

            if self.clock_opts:
                sub_params.extend(to_kv_pairs(self.clock_opts))

            if sub_params:
                args.append(','.join(sub_params))

    def _add_cpu_args(self, args):
        if self.cpu_model is not None:
            args.append('--cpu')
            sub_params = [self.cpu_model]

            if self.cpu_features is not None:
                for item in self.cpu_features.get('force') or []:
                    sub_params.append("force={}".format(item))
                for item in self.cpu_features.get('require') or []:
                    sub_params.append("require={}".format(item))
                for item in self.cpu_features.get('optional') or []:
                    sub_params.append("optional={}".format(item))
                for item in self.cpu_features.get('disable') or []:
                    sub_params.append("disable={}".format(item))

            if self.cpu_opts is not None:
                sub_params.append(to_kv_pairs(self.cpu_opts))

            if self.cpu_cells is not None:
                for i, cell in enumerate(self.cpu_cells):
                    for k, v in cell:
                        if k in ['id', 'cpus', 'memory']:
                            sub_params.append(
                                "numa.cell{}.{}={}".format(i, k, v))

                    for j, item in enumerate(cell.get('distances') or []):
                        for k, v in item:
                            sub_params.append(
                                "numa.cell{}.distances.sibling{}.{}={}".format(i, j, k, v))

            if sub_params:
                args.append(','.join(sub_params))

        if self.vcpus is not None:
            args.extend(['--vcpus',
                         to_mixed_param(self.vcpus, self.vcpus_opts)])

    def _add_memory_args(self, args):
        if self.memory is not None:
            args.extend(['--memory',
                         to_mixed_param(self.memory, self.memory_opts)])

        if self.memorybacking is not None:
            args.extend(['--memorybacking',
                         to_kv_param(self.memorybacking)])

        if self.memballoon is not None:
            args.extend(['--memballoon',
                         to_mixed_param(self.memballoon, self.memballoon_opts)])

    def _add_tune_args(self, args):
        if self.cputune is not None:
            args.append('--cputune')
            sub_params = []

            for i, item in enumerate(self.cputune.get('vcpupins') or []):
                for k, v in item:
                    sub_params.append("vcpupin{}.{}={}".format(i, k, v))

            if sub_params:
                args.append(','.join(sub_params))

        if self.memtune is not None:
            args.extend('--memtune', to_kv_param(self.memtune))

        if self.blkiotune is not None:
            args.append('--blkiotune')
            sub_params = []

            for k, v in self.blkiotune:
                if k in ['weight']:
                    sub_params.append("{}={}".format(k, v))

            for i, item in enumerate(self.blkiotune.get('devices') or []):
                for k, v in item:
                    sub_params.append("device{}.{}={}".format(i, k, v))

            if sub_params:
                args.append(','.join(sub_params))

    def _add_boot_args(self, args):
        if self.uefi is not None:
            args.extend(['--boot', 'uefi'])

    def _add_storage_args(self, args):
        if self.storage_devices is not None:
            if not len(self.storage_devices):
                # empty list
                args.extend(['--disk', 'none'])
            else:
                for disk in self.storage_devices:
                    args.extend(['--disk', to_kv_param(disk)])

    def _add_network_args(self, args):
        if self.network_devices is not None:
            if not len(self.network_devices):
                # empty list
                args.extend(['--network', 'none'])
            else:
                for net in self.network_devices:
                    args.extend(['--network', to_kv_param(net)])

    def _add_device_args(self, args):
        if self.video is not None:
            args.extend(['--video',
                         to_mixed_param(self.video, self.video_opts)])

        if self.sound is not None:
            args.extend(['--sound',
                         to_mixed_param(self.sound, self.sound_opts)])

        if self.serial_devices is not None:
            for device_info in self.serial_devices:
                if 'type' not in device_info:
                    raise VirtInstError(
                        "Sub-option 'type' is required for each serial device")

                target_type = device_info['type']
                device_opts = device_info.copy()
                del device_opts['type']
                args.extend(['--serial',
                             to_mixed_param(target_type, device_opts)])

        if self.parallel_devices is not None:
            for device_info in self.parallel_devices:
                if 'type' not in device_info:
                    raise VirtInstError(
                        "Sub-option 'type' is required for each parallel device")

                target_type = device_info['type']
                device_opts = device_info.copy()
                del device_opts['type']
                args.extend(['--parallel',
                             to_mixed_param(target_type, device_opts)])

        if self.smartcard_devices is not None:
            for device_info in self.smartcard_devices:
                if 'mode' not in device_info:
                    raise VirtInstError(
                        "Sub-option 'mode' is required for each smartcard device")

                mode = device_info['mode']
                device_opts = device_info.copy()
                del device_opts['mode']
                args.extend(['--smartcard',
                             to_mixed_param(mode, device_opts)])

        if self.input_devices is not None:
            for device_info in self.input_devices:
                if 'type' not in device_info:
                    raise VirtInstError(
                        "Sub-option 'type' is required for each input device")

                args.extend(['--input', to_kv_param(device_info)])

        if self.controllers is not None:
            for ctrl_info in self.controllers:
                if 'type' not in ctrl_info:
                    raise VirtInstError(
                        "Sub-option 'type' is required for each controller device")

                ctrl_type = ctrl_info['type']
                ctrl_opts = ctrl_info.copy()
                del ctrl_opts['type']
                args.extend(['--controller',
                             to_mixed_param(ctrl_type, ctrl_opts)])

        if self.host_devices is not None:
            for device_info in self.host_devices:
                if 'source' not in device_info:
                    raise VirtInstError(
                        "Sub-option 'source' is required for each host device")

                source = device_info['source']
                device_opts = device_info.copy()
                del device_opts['source']
                args.extend(['--hostdev',
                             to_mixed_param(source, device_opts)])

    def _add_graphics_args(self, args):
        if self.graphics is not None:
            args.extend(['--graphics',
                         to_mixed_param(self.graphics, self.graphics_opts)])

    def _add_misc_args(self, args):
        if self.autostart:
            args.extend(['--autostart'])

        args.append('--noautoconsole')

        return args

    def _make_domain_args(self):
        args = list()
        args.extend(['--name', self.name])
        self._add_virt_args(args)
        self._add_general_args(args)
        self._add_cpu_args(args)
        self._add_memory_args(args)
        self._add_tune_args(args)
        self._add_boot_args(args)
        self._add_storage_args(args)
        self._add_network_args(args)
        self._add_device_args(args)
        self._add_graphics_args(args)
        self._add_misc_args(args)

        return args

    def install_by_cdrom(self, media,
                         noreboot=False, dryrun=False):
        cmd = [self.virtinst_bin, '--connect', self.uri]
        cmd.extend(self._make_domain_args())
        cmd.extend(['--cdrom', to_native(media)])

        if noreboot:
            cmd.append('--noreboot')

        if dryrun:
            cmd.append('--dry-run')

        return self.module.run_command(cmd)

    def install_by_url(self, url, extra_args=None, initrd_inject=None,
                       noreboot=False, dryrun=False):
        cmd = [self.virtinst_bin, '--connect', self.uri]
        cmd.extend(self._make_domain_args())
        cmd.extend(['--location', url])

        if extra_args is not None:
            cmd.extend(['--extra-args', to_native(extra_args)])

        if initrd_inject is not None:
            cmd.extend(['--initrd-inject', to_native(initrd_inject)])

        if noreboot:
            cmd.append('--noreboot')

        if dryrun:
            cmd.append('--dry-run')

        return self.module.run_command(cmd)

    def install_by_pxe(self, noreboot=False, dryrun=False):
        cmd = [self.virtinst_bin, '--connect', self.uri]
        cmd.extend(self._make_domain_args())
        cmd.append('--pxe')

        if noreboot:
            cmd.append('--noreboot')

        if dryrun:
            cmd.append('--dry-run')

        return self.module.run_command(cmd)

    def import_image(self, dryrun=False):
        cmd = [self.virtinst_bin, '--connect', self.uri]
        cmd.extend(self._make_domain_args())
        cmd.append('--import')

        if dryrun:
            cmd.append('--dry-run')

        return self.module.run_command(cmd)
