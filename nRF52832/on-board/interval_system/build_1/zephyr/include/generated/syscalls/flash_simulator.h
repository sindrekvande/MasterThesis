/* auto-generated by gen_syscalls.py, don't edit */

#ifndef Z_INCLUDE_SYSCALLS_FLASH_SIMULATOR_H
#define Z_INCLUDE_SYSCALLS_FLASH_SIMULATOR_H


#include <zephyr/tracing/tracing_syscall.h>

#ifndef _ASMLANGUAGE

#include <stdarg.h>

#include <syscall_list.h>
#include <zephyr/syscall.h>

#include <zephyr/linker/sections.h>


#ifdef __cplusplus
extern "C" {
#endif

extern void * z_impl_flash_simulator_get_memory(const struct device * dev, size_t * mock_size);

__pinned_func
static inline void * flash_simulator_get_memory(const struct device * dev, size_t * mock_size)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		union { uintptr_t x; size_t * val; } parm1 = { .val = mock_size };
		return (void *) arch_syscall_invoke2(parm0.x, parm1.x, K_SYSCALL_FLASH_SIMULATOR_GET_MEMORY);
	}
#endif
	compiler_barrier();
	return z_impl_flash_simulator_get_memory(dev, mock_size);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define flash_simulator_get_memory(dev, mock_size) ({ 	void * syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_FLASH_SIMULATOR_GET_MEMORY, flash_simulator_get_memory, dev, mock_size); 	syscall__retval = flash_simulator_get_memory(dev, mock_size); 	sys_port_trace_syscall_exit(K_SYSCALL_FLASH_SIMULATOR_GET_MEMORY, flash_simulator_get_memory, dev, mock_size, syscall__retval); 	syscall__retval; })
#endif
#endif


#ifdef __cplusplus
}
#endif

#endif
#endif /* include guard */
