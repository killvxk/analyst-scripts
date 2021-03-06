from argparse import ArgumentParser
from pdb import pm
from miasm.jitter.csts import PAGE_READ, PAGE_WRITE, EXCEPT_INT_XX, EXCEPT_ACCESS_VIOL, EXCEPT_PRIV_INSN
from miasm.analysis.machine import Machine
from miasm.os_dep.linux import environment, syscall
import logging


def code_sentinelle(jitter):
    print("Done")
    jitter.run = False
    jitter.pc = 0
    return True

def priv(jitter):
    print("Privilege Exception")
    return False


if __name__ == '__main__':
    parser = ArgumentParser(description="x86 32 basic Jitter")
    parser.add_argument("filename", help="x86 32 shellcode filename")
    parser.add_argument("-j", "--jitter",
                        help="Jitter engine",
                        default="python")
    parser.add_argument("--verbose", "-v", action="store_true",
            help="Verbose mode")
    args = parser.parse_args()

    myjit = Machine("x86_32").jitter(args.jitter)
    myjit.init_stack()


    data = open(args.filename, 'rb').read()
    run_addr = 0x40000000
    myjit.vm.add_memory_page(run_addr, PAGE_READ | PAGE_WRITE, data)
    if args.verbose:
        myjit.set_trace_log()
    myjit.add_exception_handler(EXCEPT_PRIV_INSN, priv)
    myjit.push_uint32_t(0x1337beef)
    myjit.add_exception_handler(EXCEPT_ACCESS_VIOL, code_sentinelle)
    myjit.add_breakpoint(0x1337beef, code_sentinelle)

    log = logging.getLogger('syscalls')
    log.setLevel(logging.DEBUG)
    env = environment.LinuxEnvironment_x86_32()
    syscall.enable_syscall_handling(myjit, env, syscall.syscall_callbacks_x86_32)
    myjit.run(run_addr)
