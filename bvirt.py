import libvirt

uri = "qemu+ssh:///system"
conn = libvirt.openReadOnly(uri)
