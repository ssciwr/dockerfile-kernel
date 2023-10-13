from dockerfile_kernel.kernel import DockerKernel
from ipykernel.kernelapp import IPKernelApp


IPKernelApp.launch_instance(kernel_class=DockerKernel)
